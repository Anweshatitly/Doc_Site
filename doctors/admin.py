from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Doctor


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


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin interface for clinic doctors, dermatologists, and trichologists."""

    list_display = (
        'photo_thumbnail',
        'name_display',
        'designation_badge',
        'experience_display',
        'consultation_fee',
        'availability_display',
        'is_active',
        'order',
    )
    list_display_links = ('name_display',)
    list_filter = ('is_active', 'gender', 'designation', 'created_at')
    search_fields = ('name', 'designation', 'qualifications', 'bio', 'email', 'phone')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    filter_horizontal = ('treatments',)
    ordering = ('order', 'name')
    readonly_fields = ('photo_preview', 'banner_preview', 'created_at', 'updated_at')
    actions = ('activate_doctors', 'deactivate_doctors')

    fieldsets = (
        ('👨‍⚕️ Specialist Profile & Imagery', {
            'description': 'Basic details and portrait photo of the doctor.',
            'fields': (
                ('name', 'slug'),
                'gender',
                ('photo', 'photo_preview'),
                ('banner_image', 'banner_preview'),
            ),
        }),
        ('🎓 Professional Qualifications & Bio', {
            'description': 'Medical degrees, designations, years in practice, and performed treatments.',
            'fields': (
                ('designation', 'qualifications'),
                'experience_years',
                'bio',
                'treatments',
            ),
        }),
        ('⏰ Consultation Fees & Availability Schedule', {
            'description': 'Consultation pricing and weekly consulting hours for appointments.',
            'fields': (
                'consultation_fee',
                ('available_days', 'available_time'),
            ),
        }),
        ('📞 Contact Information & Social Profiles', {
            'classes': ('collapse',),
            'description': 'Direct doctor contact channels and social media profiles.',
            'fields': (
                ('email', 'phone'),
                ('facebook_url', 'instagram_url'),
                'linkedin_url',
            ),
        }),
        ('👁️ Clinic Website Display & SEO', {
            'fields': (
                ('is_active', 'order'),
                ('meta_title', 'meta_description'),
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Photo')
    def photo_thumbnail(self, obj):
        return make_thumb_html(obj.photo, size=46, circular=True)

    @admin.display(description='Doctor Name', ordering='name')
    def name_display(self, obj):
        qual = f' <span style="font-size:11px; color:#64748b;">({obj.qualifications})</span>' if obj.qualifications else ''
        return format_html('<strong>Dr. {0}</strong>{1}', obj.name, format_html(qual))

    @admin.display(description='Designation', ordering='designation')
    def designation_badge(self, obj):
        return format_html(
            '<span style="background:#e8f5f2; color:#1e5c53; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{0}</span>',
            obj.designation
        )

    @admin.display(description='Experience', ordering='experience_years')
    def experience_display(self, obj):
        if obj.experience_years:
            return format_html('<span>{0} Yrs</span>', obj.experience_years)
        return format_html('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Schedule')
    def availability_display(self, obj):
        if obj.available_days and obj.available_time:
            return format_html('<span style="font-size:12px;">{0}<br/><small style="color:#64748b;">{1}</small></span>', obj.available_days, obj.available_time)
        elif obj.available_days:
            return format_html('<span style="font-size:12px;">{0}</span>', obj.available_days)
        return format_html('<span style="color:#94a3b8;">On Request</span>')

    @admin.display(description='Doctor Portrait Preview')
    def photo_preview(self, obj):
        return make_preview_html(obj.photo, max_height=140, max_width=140, circular=True)

    @admin.display(description='Banner Image Preview')
    def banner_preview(self, obj):
        return make_preview_html(obj.banner_image, max_height=100, max_width=320)

    @admin.action(description='✅ Activate selected doctors')
    def activate_doctors(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} doctor(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected doctors')
    def deactivate_doctors(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} doctor(s) deactivated.', messages.WARNING)
