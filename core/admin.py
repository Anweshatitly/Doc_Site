from django.contrib import admin, messages
from django.utils.html import format_html
from .models import SiteConfiguration, Testimonial, FAQ, ContactEnquiry, PageSEO


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


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin for the singleton site configuration."""

    save_on_top = True

    readonly_fields = (
        'logo_preview',
        'logo_dark_preview',
        'favicon_preview',
        'hero_image_preview',
        'about_image_preview',
    )

    fieldsets = (
        ('🏥 Clinic Branding & Identity', {
            'description': 'Configure the clinic name, slogan, logos, and website icon.',
            'fields': (
                'site_name',
                'tagline',
                ('logo', 'logo_preview'),
                ('logo_dark', 'logo_dark_preview'),
                ('favicon', 'favicon_preview'),
            ),
        }),
        ('📖 About Us & Hero Section', {
            'description': 'Content for the clinic homepage banner and About Us page.',
            'fields': (
                'about_short',
                'about_full',
                ('hero_image', 'hero_image_preview'),
                ('about_image', 'about_image_preview'),
            ),
        }),
        ('📞 Contact Information', {
            'description': 'Primary customer support phone numbers, emails, and WhatsApp booking line.',
            'fields': (
                ('phone_primary', 'phone_secondary'),
                ('email_primary', 'email_secondary'),
                'whatsapp_number',
            ),
        }),
        ('📍 Physical Location & Address', {
            'description': 'Physical clinic address details for patient visits.',
            'fields': (
                'address',
                ('city', 'state', 'pincode'),
            ),
        }),
        ('⏰ Clinic Operating Hours', {
            'description': 'Working hours shown across website header, footer, and contact page.',
            'fields': (
                ('working_hours_weekday', 'working_hours_weekend'),
            ),
        }),
        ('🗺️ Maps & Navigation', {
            'description': 'Embedded map iframe code and direct link for navigation buttons.',
            'fields': (
                'google_maps_embed',
                'google_maps_link',
            ),
        }),
        ('📱 Social Media Channels', {
            'description': 'Links to clinic social media profiles.',
            'fields': (
                ('facebook_url', 'instagram_url'),
                ('twitter_url', 'youtube_url'),
                'linkedin_url',
            ),
        }),
        ('🔍 SEO & Search Engines', {
            'classes': ('collapse',),
            'description': 'Default search engine meta tags for optimal online ranking.',
            'fields': (
                'meta_description',
                'meta_keywords',
            ),
        }),
        ('📄 Footer Information', {
            'classes': ('collapse',),
            'fields': ('footer_text',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Current Logo')
    def logo_preview(self, obj):
        return make_preview_html(obj.logo, max_height=80, max_width=180)

    @admin.display(description='Dark Mode Logo')
    def logo_dark_preview(self, obj):
        return make_preview_html(obj.logo_dark, max_height=80, max_width=180)

    @admin.display(description='Favicon')
    def favicon_preview(self, obj):
        return make_preview_html(obj.favicon, max_height=40, max_width=40)

    @admin.display(description='Hero Background Preview')
    def hero_image_preview(self, obj):
        return make_preview_html(obj.hero_image, max_height=140, max_width=280)

    @admin.display(description='About Image Preview')
    def about_image_preview(self, obj):
        return make_preview_html(obj.about_image, max_height=140, max_width=280)


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    """Admin interface for configuring SEO tags and social previews for main pages."""

    list_display = ('page_badge', 'meta_title_display', 'has_description', 'has_og_image', 'updated_at')
    list_display_links = ('page_badge',)
    search_fields = ('page', 'meta_title', 'meta_description', 'meta_keywords')
    readonly_fields = ('og_image_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('📄 Page Selection', {
            'description': 'Select which main website page to configure SEO tags for.',
            'fields': ('page',),
        }),
        ('🔍 Search Engine Optimization (SEO)', {
            'description': 'Configure the dynamic page title and meta description tag shown on Google.',
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'canonical_url',
            ),
        }),
        ('🌐 Social Media & Open Graph (OG)', {
            'description': 'Social preview card image for Facebook, LinkedIn, WhatsApp, and Twitter.',
            'fields': (
                ('og_image', 'og_image_preview'),
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Page', ordering='page')
    def page_badge(self, obj):
        return format_html('<strong>{0}</strong>', obj.get_page_display())

    @admin.display(description='SEO Title')
    def meta_title_display(self, obj):
        if obj.meta_title:
            return obj.meta_title
        return format_html('<span style="color:#94a3b8; font-style:italic;">Default Clinic Title</span>')

    @admin.display(description='Meta Description', boolean=True)
    def has_description(self, obj):
        return bool(obj.meta_description)

    @admin.display(description='Social Image', boolean=True)
    def has_og_image(self, obj):
        return bool(obj.og_image)

    @admin.display(description='OG Image Preview')
    def og_image_preview(self, obj):
        return make_preview_html(obj.og_image, max_height=140, max_width=280)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin interface for managing patient testimonials and reviews."""

    list_display = (
        'photo_thumbnail',
        'name',
        'rating_display',
        'treatment',
        'doctor',
        'location',
        'is_featured',
        'is_active',
        'created_at',
    )
    list_display_links = ('name',)
    list_filter = ('is_active', 'is_featured', 'rating', 'doctor', 'treatment', 'created_at')
    search_fields = ('name', 'content', 'location', 'designation')
    list_editable = ('is_featured', 'is_active')
    autocomplete_fields = ('treatment', 'doctor')
    date_hierarchy = 'created_at'
    ordering = ('-is_featured', '-created_at')
    readonly_fields = ('photo_preview', 'created_at', 'updated_at')
    actions = ('make_featured', 'remove_featured', 'activate_testimonials', 'deactivate_testimonials')

    fieldsets = (
        ('👤 Patient Profile', {
            'fields': (
                'name',
                ('designation', 'location'),
                ('photo', 'photo_preview'),
            ),
        }),
        ('⭐ Review & Feedback', {
            'fields': (
                'rating',
                'content',
            ),
        }),
        ('🔗 Associated Services', {
            'description': 'Optionally link this review to the treatment received or attending doctor.',
            'fields': (
                ('treatment', 'doctor'),
            ),
        }),
        ('👁️ Display Settings', {
            'fields': (
                ('is_featured', 'is_active'),
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Photo')
    def photo_thumbnail(self, obj):
        return make_thumb_html(obj.photo, size=44, circular=True)

    @admin.display(description='Current Photo')
    def photo_preview(self, obj):
        return make_preview_html(obj.photo, max_height=120, max_width=120, circular=True)

    @admin.display(description='Rating', ordering='rating')
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color:#f59e0b; font-size:14px; font-weight:bold;" title="{0}/5 Stars">{1}</span>',
            obj.rating, stars
        )

    @admin.action(description='⭐ Mark selected testimonials as Featured')
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} testimonial(s) marked as featured.', messages.SUCCESS)

    @admin.action(description='Remove Featured flag from selected testimonials')
    def remove_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} testimonial(s) removed from featured.', messages.INFO)

    @admin.action(description='✅ Activate selected testimonials')
    def activate_testimonials(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} testimonial(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected testimonials')
    def deactivate_testimonials(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} testimonial(s) deactivated.', messages.WARNING)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin interface for frequently asked questions."""

    list_display = (
        'question_short',
        'category',
        'order',
        'is_active',
        'updated_at',
    )
    list_display_links = ('question_short',)
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    list_editable = ('category', 'order', 'is_active')
    ordering = ('category', 'order', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('activate_faqs', 'deactivate_faqs')

    fieldsets = (
        ('❓ FAQ Content', {
            'fields': (
                'category',
                'question',
                'answer',
            ),
        }),
        ('⚙️ Display & Ordering', {
            'fields': (
                ('order', 'is_active'),
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Question', ordering='question')
    def question_short(self, obj):
        return obj.question if len(obj.question) <= 85 else f'{obj.question[:82]}...'

    @admin.action(description='✅ Activate selected FAQs')
    def activate_faqs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} FAQ(s) activated.', messages.SUCCESS)

    @admin.action(description='🚫 Deactivate selected FAQs')
    def deactivate_faqs(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} FAQ(s) deactivated.', messages.WARNING)


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    """Admin interface for managing incoming patient contact messages."""

    list_display = (
        'status',
        'name',
        'email_link',
        'phone_link',
        'subject_short',
        'created_at',
    )
    list_display_links = ('name', 'subject_short')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message', 'admin_notes')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at', 'updated_at')
    actions = ('mark_as_read', 'mark_as_replied', 'mark_as_closed')


    fieldsets = (
        ('📩 Enquiry Details', {
            'description': 'Information submitted by the patient via the Contact Us form.',
            'fields': (
                ('name', 'email'),
                ('phone', 'created_at'),
                'subject',
                'message',
            ),
        }),
        ('🛠️ Internal Clinic Management', {
            'description': 'Update inquiry status and record notes on communications with the patient.',
            'fields': (
                'status',
                'admin_notes',
            ),
        }),
        ('⏱️ Timestamps', {
            'classes': ('collapse',),
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        styles = {
            'new': ('#dbeafe', '#1e40af', 'New Message'),
            'read': ('#e0f2fe', '#0369a1', 'Read'),
            'replied': ('#dcfce7', '#15803d', 'Replied'),
            'closed': ('#f1f5f9', '#475569', 'Closed'),
        }
        bg, text_color, label = styles.get(obj.status, ('#f1f5f9', '#475569', obj.status))
        return format_html(
            '<span class="badge-status" style="background:{0}; color:{1}; border:1px solid {0};">{2}</span>',
            bg, text_color, label
        )

    @admin.display(description='Email')
    def email_link(self, obj):
        return format_html('<a href="mailto:{0}" style="color:#2a7a6e; font-weight:500;">{0}</a>', obj.email)

    @admin.display(description='Phone')
    def phone_link(self, obj):
        if obj.phone:
            return format_html('<a href="tel:{0}" style="color:#2a7a6e;">{0}</a>', obj.phone)
        return format_html('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Subject', ordering='subject')
    def subject_short(self, obj):
        return obj.subject if len(obj.subject) <= 60 else f'{obj.subject[:57]}...'

    @admin.action(description='👁️ Mark selected as Read')
    def mark_as_read(self, request, queryset):
        count = queryset.update(status='read')
        self.message_user(request, f'{count} message(s) marked as read.', messages.INFO)

    @admin.action(description='✉️ Mark selected as Replied')
    def mark_as_replied(self, request, queryset):
        count = queryset.update(status='replied')
        self.message_user(request, f'{count} message(s) marked as replied.', messages.SUCCESS)

    @admin.action(description='📁 Mark selected as Closed')
    def mark_as_closed(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f'{count} message(s) marked as closed.', messages.SUCCESS)
