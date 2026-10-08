from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count
from .models import TreatmentCategory, Treatment, Offer
from gallery.models import BeforeAfterImage


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
    """Utility to generate list thumbnail HTML."""
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


class TreatmentInline(admin.TabularInline):
    """Inline view of treatments belonging to a category."""
    model = Treatment
    extra = 0
    fields = ('name', 'duration', 'price_range', 'is_featured', 'is_active', 'order_display')
    readonly_fields = ('order_display',)
    show_change_link = True

    @admin.display(description='Preview')
    def order_display(self, obj):
        return make_thumb_html(obj.image, size=32)


class BeforeAfterInline(admin.TabularInline):
    """Inline view of before & after results linked to a treatment."""
    model = BeforeAfterImage
    extra = 0
    fields = (
        'title',
        'before_thumb',
        'before_image',
        'after_thumb',
        'after_image',
        'sessions_completed',
        'is_active',
        'order',
    )
    readonly_fields = ('before_thumb', 'after_thumb')
    show_change_link = True

    @admin.display(description='Before')
    def before_thumb(self, obj):
        return make_thumb_html(obj.before_image, size=36)

    @admin.display(description='After')
    def after_thumb(self, obj):
        return make_thumb_html(obj.after_image, size=36)


@admin.register(TreatmentCategory)
class TreatmentCategoryAdmin(admin.ModelAdmin):
    """Admin interface for treatment categories."""

    list_display = (
        'image_thumbnail',
        'name',
        'slug',
        'icon_display',
        'treatments_count_display',
        'order',
        'is_active',
        'updated_at',
    )
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    ordering = ('order', 'name')
    readonly_fields = ('image_preview', 'treatments_count_display', 'created_at', 'updated_at')
    inlines = (TreatmentInline,)
    actions = ('activate_categories', 'deactivate_categories')

    fieldsets = (
        ('🏷️ Category Details', {
            'description': 'Main information about this treatment department.',
            'fields': (
                ('name', 'slug'),
                'description',
            ),
        }),
        ('🖼️ Visual Styling', {
            'description': 'Upload category cover image and optional Bootstrap icon name.',
            'fields': (
                'icon_class',
                ('image', 'image_preview'),
            ),
        }),
        ('⚙️ Display Order & Status', {
            'fields': (
                ('order', 'is_active'),
                'treatments_count_display',
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(treatment_count=Count('treatments'))

    @admin.display(description='Cover')
    def image_thumbnail(self, obj):
        return make_thumb_html(obj.image, size=44)

    @admin.display(description='Category Image Preview')
    def image_preview(self, obj):
        return make_preview_html(obj.image, max_height=140, max_width=240)

    @admin.display(description='Icon')
    def icon_display(self, obj):
        if obj.icon_class:
            return format_html('<code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#2a7a6e;">{0}</code>', obj.icon_class)
        return format_html('<span style="color:#94a3b8;">None</span>')

    @admin.display(description='Total Treatments', ordering='treatment_count')
    def treatments_count_display(self, obj):
        count = getattr(obj, 'treatment_count', obj.treatments.count())
        return format_html(
            '<span style="background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px;">{0} Services</span>',
            count
        )

    @admin.action(description='✅ Activate selected categories')
    def activate_categories(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} category(ies) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected categories')
    def deactivate_categories(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} category(ies) deactivated.', messages.WARNING)


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    """Admin interface for managing clinic treatments and medical procedures."""

    list_display = (
        'image_thumbnail',
        'name',
        'category_badge',
        'duration',
        'price_range',
        'is_featured',
        'is_active',
        'updated_at',
    )
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'short_description', 'description', 'benefits')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'is_active')
    ordering = ('category__order', 'name')
    readonly_fields = ('image_preview', 'banner_preview', 'created_at', 'updated_at')
    inlines = (BeforeAfterInline,)
    actions = ('mark_featured', 'unmark_featured', 'activate_treatments', 'deactivate_treatments')

    fieldsets = (
        ('🏷️ Basic Information', {
            'description': 'Select category and enter treatment title and URL slug.',
            'fields': (
                ('category', 'name'),
                'slug',
            ),
        }),
        ('📝 Description & Patient Benefits', {
            'description': 'Explain the procedure, expected outcomes, and enter bulleted benefits.',
            'fields': (
                'short_description',
                'description',
                'benefits',
            ),
        }),
        ('🖼️ Treatment Media', {
            'description': 'Main card thumbnail and wide hero banner for the detail page.',
            'fields': (
                ('image', 'image_preview'),
                ('banner_image', 'banner_preview'),
            ),
        }),
        ('⏱️ Session Details & Pricing', {
            'fields': (
                ('duration', 'sessions_required'),
                'price_range',
            ),
        }),
        ('👁️ Promotion & Status', {
            'fields': (
                ('is_featured', 'is_active'),
            ),
        }),
        ('🔍 SEO Meta Information', {
            'classes': ('collapse',),
            'description': 'Customize page title and description for search engines.',
            'fields': (
                'meta_title',
                'meta_description',
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Image')
    def image_thumbnail(self, obj):
        return make_thumb_html(obj.image, size=44)

    @admin.display(description='Category', ordering='category')
    def category_badge(self, obj):
        return format_html(
            '<span style="background:#e8f5f2; color:#1e5c53; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{0}</span>',
            obj.category.name
        )

    @admin.display(description='Featured', ordering='is_featured')
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color:#f59e0b; font-weight:bold; font-size:14px;" title="Featured">⭐ Yes</span>')
        return format_html('<span style="color:#94a3b8; font-size:12px;">No</span>')

    @admin.display(description='Main Image Preview')
    def image_preview(self, obj):
        return make_preview_html(obj.image, max_height=140, max_width=240)

    @admin.display(description='Banner Image Preview')
    def banner_preview(self, obj):
        return make_preview_html(obj.banner_image, max_height=100, max_width=320)

    @admin.action(description='⭐ Mark selected as Featured')
    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} treatment(s) marked as featured.', messages.SUCCESS)

    @admin.action(description='Remove Featured flag from selected')
    def unmark_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} treatment(s) unmarket as featured.', messages.INFO)

    @admin.action(description='✅ Activate selected treatments')
    def activate_treatments(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} treatment(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected treatments')
    def deactivate_treatments(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} treatment(s) deactivated.', messages.WARNING)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin interface for clinic promotional packages and special discounts."""

    list_display = (
        'image_thumbnail',
        'title',
        'discount_badge',
        'pricing_display',
        'schedule_display',
        'is_active',
        'updated_at',
    )
    list_display_links = ('title',)
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)
    filter_horizontal = ('treatments',)
    ordering = ('-created_at',)
    readonly_fields = ('image_preview', 'savings_display', 'created_at', 'updated_at')
    actions = ('activate_offers', 'deactivate_offers')

    fieldsets = (
        ('🎁 Package Details', {
            'description': 'Offer headline, slug, and promotional description.',
            'fields': (
                ('title', 'slug'),
                'short_description',
                'description',
                ('image', 'image_preview'),
            ),
        }),
        ('💰 Pricing & Discount Calculation', {
            'description': 'Original standard price vs discounted clinic package price.',
            'fields': (
                ('original_price', 'offer_price'),
                ('discount_text', 'savings_display'),
            ),
        }),
        ('💆 Included Treatments', {
            'description': 'Select which clinic procedures are bundled into this package.',
            'fields': (
                'treatments',
            ),
        }),
        ('📅 Validity Period & Status', {
            'description': 'Control the time window during which this promotion runs.',
            'fields': (
                ('start_date', 'end_date'),
                'is_active',
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Poster')
    def image_thumbnail(self, obj):
        return make_thumb_html(obj.image, size=44)

    @admin.display(description='Current Poster Preview')
    def image_preview(self, obj):
        return make_preview_html(obj.image, max_height=140, max_width=240)

    @admin.display(description='Discount', ordering='discount_text')
    def discount_badge(self, obj):
        if obj.discount_text:
            return format_html(
                '<span style="background:#ea580c; color:#fff; padding:3px 8px; border-radius:12px; font-weight:700; font-size:11px;">{0}</span>',
                obj.discount_text
            )
        return format_html('<span style="color:#94a3b8;">None</span>')

    @admin.display(description='Pricing')
    def pricing_display(self, obj):
        if obj.original_price and obj.offer_price:
            return format_html(
                '<span style="text-decoration:line-through; color:#94a3b8; font-size:12px;">₹{0}</span> '
                '<span style="color:#16a34a; font-weight:bold; font-size:13px;">₹{1}</span>',
                obj.original_price, obj.offer_price
            )
        elif obj.offer_price:
            return format_html('<span style="color:#16a34a; font-weight:bold;">₹{0}</span>', obj.offer_price)
        return format_html('<span style="color:#94a3b8;">Custom</span>')

    @admin.display(description='Calculated Patient Savings')
    def savings_display(self, obj):
        savings = obj.savings
        if savings:
            return format_html(
                '<strong style="color:#16a34a; font-size:14px;">₹{0} SAVED</strong>',
                savings
            )
        return format_html('<span style="color:#94a3b8; font-style:italic;">Enter both Original and Offer price to calculate</span>')

    @admin.display(description='Valid Period')
    def schedule_display(self, obj):
        if obj.start_date and obj.end_date:
            return format_html('<span style="font-size:12px;">{0} to {1}</span>', obj.start_date, obj.end_date)
        elif obj.end_date:
            return format_html('<span style="font-size:12px;">Until {0}</span>', obj.end_date)
        return format_html('<span style="color:#15803d; font-size:12px; font-weight:500;">Ongoing</span>')

    @admin.action(description='✅ Activate selected offers')
    def activate_offers(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} offer(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected offers')
    def deactivate_offers(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} offer(s) deactivated.', messages.WARNING)
