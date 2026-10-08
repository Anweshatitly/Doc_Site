from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count
from .models import GalleryCategory, GalleryImage, BeforeAfterImage


def make_preview_html(image_field, max_height=120, max_width=240, circular=False):
    """Utility to generate clean HTML image preview with fallback."""
    if image_field:
        border_radius = "50%" if circular else "8px"
        return format_html(
            '<div class="image-preview-card" style="display:inline-block; padding:4px; background:#fff; border:1px solid #e2e8f0; border-radius:{0};">'
            '<a href="{1}" target="_blank" title="Click to view full image">'
            '<img src="{1}" style="max-height:{2}px; max-width:{3}px; border-radius:{0}; object-fit:cover; display:block;" />'
            '</a>'
            '</div>',
            border_radius, image_field.url, max_height, max_width
        )
    return format_html('<span style="color:#94a3b8; font-style:italic; font-size:12px;">No image uploaded</span>')


def make_thumb_html(image_field, size=46, circular=False):
    """Utility to generate list thumbnail HTML with zoom-on-hover."""
    if image_field:
        border_radius = "50%" if circular else "6px"
        return format_html(
            '<img src="{0}" class="admin-thumb" style="width:{1}px; height:{1}px; border-radius:{2}; object-fit:cover; vertical-align:middle;" />',
            image_field.url, size, border_radius
        )
    return format_html(
        '<span class="admin-thumb-empty" style="display:inline-block; width:{0}px; height:{0}px; line-height:{0}px; text-align:center; background:#f1f5f9; color:#94a3b8; border-radius:6px; font-size:10px;">None</span>',
        size
    )


class GalleryImageInline(admin.TabularInline):
    """Inline view of images inside a gallery category."""
    model = GalleryImage
    extra = 1
    fields = ('thumb', 'title', 'image', 'alt_text', 'order', 'is_active')
    readonly_fields = ('thumb',)
    show_change_link = True

    @admin.display(description='Preview')
    def thumb(self, obj):
        return make_thumb_html(obj.image, size=38)


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    """Admin interface for clinic photo gallery categories/albums."""

    list_display = ('name', 'slug', 'images_count_display', 'order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    readonly_fields = ('images_count_display',)
    inlines = (GalleryImageInline,)
    actions = ('activate_categories', 'deactivate_categories')

    fieldsets = (
        ('📁 Category Information', {
            'description': 'Album title and URL slug.',
            'fields': (
                ('name', 'slug'),
                'description',
            ),
        }),
        ('⚙️ Order & Status', {
            'fields': (
                ('order', 'is_active'),
                'images_count_display',
            ),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(img_count=Count('images'))

    @admin.display(description='Photos Count', ordering='img_count')
    def images_count_display(self, obj):
        count = getattr(obj, 'img_count', obj.images.count())
        return format_html(
            '<span style="background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px;">{0} Photos</span>',
            count
        )

    @admin.action(description='✅ Activate selected albums')
    def activate_categories(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} album(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected albums')
    def deactivate_categories(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} album(s) deactivated.', messages.WARNING)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Admin interface for individual gallery pictures (clinic interior, events, equipment)."""

    list_display = (
        'thumbnail_preview',
        'title_display',
        'category_badge',
        'alt_text_short',
        'is_active',
        'order',
        'uploaded_at',
    )
    list_display_links = ('title_display',)
    list_filter = ('category', 'is_active', 'uploaded_at')
    search_fields = ('title', 'description', 'alt_text')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-uploaded_at')
    readonly_fields = ('image_preview', 'uploaded_at')
    actions = ('activate_images', 'deactivate_images')

    fieldsets = (
        ('🖼️ Photo Information', {
            'description': 'Select album and upload image file.',
            'fields': (
                ('category', 'title'),
                ('image', 'image_preview'),
                'alt_text',
            ),
        }),
        ('📝 Description & Caption', {
            'fields': ('description',),
        }),
        ('⚙️ Order & Status', {
            'fields': (
                ('order', 'is_active'),
            ),
        }),
        ('⏱️ Upload Details', {
            'classes': ('collapse',),
            'fields': ('uploaded_at',),
        }),
    )

    @admin.display(description='Photo')
    def thumbnail_preview(self, obj):
        return make_thumb_html(obj.image, size=46)

    @admin.display(description='Photo Preview')
    def image_preview(self, obj):
        return make_preview_html(obj.image, max_height=140, max_width=240)

    @admin.display(description='Title', ordering='title')
    def title_display(self, obj):
        return obj.title if obj.title else format_html('<span style="color:#94a3b8; font-style:italic;">Untitled Image #{0}</span>', obj.pk)

    @admin.display(description='Category', ordering='category')
    def category_badge(self, obj):
        return format_html(
            '<span style="background:#e8f5f2; color:#1e5c53; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{0}</span>',
            obj.category.name
        )

    @admin.display(description='Alt Text (SEO)')
    def alt_text_short(self, obj):
        if obj.alt_text:
            return obj.alt_text if len(obj.alt_text) <= 30 else f'{obj.alt_text[:28]}...'
        return format_html('<span style="color:#f59e0b; font-size:11px;">⚠️ Missing</span>')

    @admin.action(description='✅ Activate selected images')
    def activate_images(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} image(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected images')
    def deactivate_images(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} image(s) deactivated.', messages.WARNING)


@admin.register(BeforeAfterImage)
class BeforeAfterImageAdmin(admin.ModelAdmin):
    """Admin interface for before-and-after clinical case studies."""

    list_display = (
        'side_by_side_thumbnail',
        'title_display',
        'treatment_badge',
        'sessions_completed',
        'patient_info',
        'is_active',
        'order',
        'created_at',
    )
    list_display_links = ('title_display',)
    list_filter = ('treatment__category', 'treatment', 'is_active', 'patient_gender', 'created_at')
    search_fields = ('title', 'description', 'treatment__name', 'sessions_completed')
    list_editable = ('is_active', 'order')
    autocomplete_fields = ('treatment',)
    date_hierarchy = 'created_at'
    ordering = ('order', '-created_at')
    readonly_fields = ('before_preview', 'after_preview', 'side_by_side_preview', 'created_at')
    actions = ('activate_cases', 'deactivate_cases')

    fieldsets = (
        ('💆 Clinical Procedure Link', {
            'description': 'Link this result to the treatment performed.',
            'fields': (
                'treatment',
                'title',
                'description',
            ),
        }),
        ('🔄 Comparison Photos', {
            'description': 'Upload the patient’s initial condition and post-treatment outcome photos.',
            'fields': (
                'side_by_side_preview',
                ('before_image', 'before_preview'),
                ('after_image', 'after_preview'),
            ),
        }),
        ('👤 Patient Profile & Treatment Duration', {
            'fields': (
                ('patient_age', 'patient_gender'),
                'sessions_completed',
            ),
        }),
        ('⚙️ Order & Status', {
            'fields': (
                ('order', 'is_active'),
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at',),
        }),
    )

    @admin.display(description='Before vs After')
    def side_by_side_thumbnail(self, obj):
        before_tag = format_html('<img src="{0}" style="width:38px; height:38px; border-radius:4px; object-fit:cover; border:1px solid #cbd5e1;" title="Before" />', obj.before_image.url) if obj.before_image else '<span>None</span>'
        after_tag = format_html('<img src="{0}" style="width:38px; height:38px; border-radius:4px; object-fit:cover; border:1px solid #cbd5e1;" title="After" />', obj.after_image.url) if obj.after_image else '<span>None</span>'
        return format_html(
            '<div style="display:flex; align-items:center; gap:4px;">'
            '{0} <span style="font-size:11px; color:#64748b;">➔</span> {1}'
            '</div>',
            before_tag, after_tag
        )

    @admin.display(description='Case Title', ordering='title')
    def title_display(self, obj):
        if obj.title:
            return format_html('<strong>{0}</strong>', obj.title)
        return format_html('<span style="color:#64748b;">{0} (Case #{1})</span>', obj.treatment.name, obj.pk)

    @admin.display(description='Treatment', ordering='treatment')
    def treatment_badge(self, obj):
        return format_html(
            '<span style="background:#e8f5f2; color:#1e5c53; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{0}</span>',
            obj.treatment.name
        )

    @admin.display(description='Patient Profile')
    def patient_info(self, obj):
        parts = []
        if obj.patient_gender:
            parts.append(obj.get_patient_gender_display())
        if obj.patient_age:
            parts.append(f'{obj.patient_age} yrs')
        return ', '.join(parts) if parts else format_html('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Before Image Preview')
    def before_preview(self, obj):
        return make_preview_html(obj.before_image, max_height=140, max_width=180)

    @admin.display(description='After Image Preview')
    def after_preview(self, obj):
        return make_preview_html(obj.after_image, max_height=140, max_width=180)

    @admin.display(description='Side-by-Side Comparison')
    def side_by_side_preview(self, obj):
        if obj.before_image and obj.after_image:
            return format_html(
                '<div style="display:inline-flex; gap:16px; align-items:center; padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; margin-bottom:8px;">'
                '<div style="text-align:center;">'
                '<div style="font-weight:700; color:#ef4444; font-size:12px; margin-bottom:4px;">BEFORE</div>'
                '<a href="{0}" target="_blank"><img src="{0}" style="max-height:160px; max-width:200px; border-radius:6px; object-fit:cover;" /></a>'
                '</div>'
                '<div style="font-size:24px; color:#94a3b8; font-weight:bold;">➔</div>'
                '<div style="text-align:center;">'
                '<div style="font-weight:700; color:#16a34a; font-size:12px; margin-bottom:4px;">AFTER</div>'
                '<a href="{1}" target="_blank"><img src="{1}" style="max-height:160px; max-width:200px; border-radius:6px; object-fit:cover;" /></a>'
                '</div>'
                '</div>',
                obj.before_image.url, obj.after_image.url
            )
        return format_html('<span style="color:#94a3b8; font-style:italic;">Upload both before and after images to see comparison preview</span>')

    @admin.action(description='✅ Activate selected results')
    def activate_cases(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} case(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected results')
    def deactivate_cases(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} case(s) deactivated.', messages.WARNING)
