from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from .models import BlogCategory, Tag, BlogPost


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


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin interface for blog categories."""

    list_display = ('name', 'slug', 'posts_count_display', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    actions = ('activate_categories', 'deactivate_categories')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(post_count=Count('posts'))

    @admin.display(description='Total Articles', ordering='post_count')
    def posts_count_display(self, obj):
        count = getattr(obj, 'post_count', obj.posts.count())
        return format_html(
            '<span style="background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px;">{0} Articles</span>',
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for article tags."""

    list_display = ('name', 'slug', 'posts_count_display')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(post_count=Count('posts'))

    @admin.display(description='Tagged Articles', ordering='post_count')
    def posts_count_display(self, obj):
        count = getattr(obj, 'post_count', obj.posts.count())
        return format_html(
            '<span style="background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-weight:600; font-size:11px;">{0} Posts</span>',
            count
        )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin interface for clinic blog articles, skincare advice, and news."""

    list_display = (
        'image_thumbnail',
        'title',
        'category_badge',
        'author',
        'status',
        'is_featured',
        'reading_time_badge',
        'views_count',
        'published_at',
    )
    list_display_links = ('title',)
    list_filter = ('status', 'category', 'is_featured', 'published_at', 'tags')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    date_hierarchy = 'published_at'
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
    ordering = ('-published_at', '-created_at')
    readonly_fields = ('image_preview', 'reading_time_badge', 'views_count', 'created_at', 'updated_at')
    actions = ('publish_articles', 'unpublish_articles', 'feature_articles', 'unfeature_articles')

    fieldsets = (
        ('📰 Blog Title & Core Information', {
            'description': 'Headline, SEO slug, category selection, and author assignment.',
            'fields': (
                ('title', 'slug'),
                ('category', 'author'),
                'tags',
            ),
        }),
        ('🖼️ Featured Image', {
            'description': 'Article cover image displayed on blog listings and article header.',
            'fields': (
                ('featured_image', 'image_preview'),
            ),
        }),
        ('✍️ Short Description & Full Content', {
            'description': 'Short summary for cards and the complete article body.',
            'fields': (
                'excerpt',
                'content',
            ),
        }),
        ('🚀 Publication & Scheduling', {
            'description': 'Manage published/unpublished status and publication date.',
            'fields': (
                ('status', 'is_featured'),
                ('published_at', 'allow_comments'),
            ),
        }),
        ('🔍 SEO Meta Information', {
            'description': 'Search engine metadata for optimal Google ranking.',
            'fields': (
                'meta_title',
                'meta_description',
            ),
        }),
        ('📊 Engagement & Timestamps', {
            'classes': ('collapse',),
            'fields': (
                ('views_count', 'reading_time_badge'),
                ('created_at', 'updated_at'),
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-assign current logged-in user as author if not explicitly selected."""
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Cover')
    def image_thumbnail(self, obj):
        return make_thumb_html(obj.featured_image, size=44)

    @admin.display(description='Cover Preview')
    def image_preview(self, obj):
        return make_preview_html(obj.featured_image, max_height=140, max_width=240)

    @admin.display(description='Category', ordering='category')
    def category_badge(self, obj):
        if obj.category:
            return format_html(
                '<span style="background:#e8f5f2; color:#1e5c53; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:600;">{0}</span>',
                obj.category.name
            )
        return format_html('<span style="color:#94a3b8;">Uncategorized</span>')

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        if obj.status == 'published':
            return format_html('<span class="badge-status badge-success">● Published</span>')
        return format_html('<span class="badge-status badge-secondary">Draft / Unpublished</span>')

    @admin.display(description='Read Time')
    def reading_time_badge(self, obj):
        return format_html(
            '<span style="background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">⏱️ {0} min</span>',
            obj.reading_time
        )

    @admin.action(description='🚀 Publish selected articles')
    def publish_articles(self, request, queryset):
        count = 0
        for post in queryset:
            post.status = 'published'
            if not post.published_at:
                post.published_at = timezone.now()
            post.save()
            count += 1
        self.message_user(request, f'{count} article(s) published successfully.', messages.SUCCESS)

    @admin.action(description='📝 Set selected articles to Draft / Unpublished')
    def unpublish_articles(self, request, queryset):
        count = queryset.update(status='draft')
        self.message_user(request, f'{count} article(s) set to Draft / Unpublished.', messages.INFO)

    @admin.action(description='⭐ Mark selected as Featured')
    def feature_articles(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} article(s) marked as featured.', messages.SUCCESS)

    @admin.action(description='Remove Featured flag from selected')
    def unfeature_articles(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} article(s) unfeatured.', messages.INFO)
