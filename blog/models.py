from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class BlogCategory(models.Model):
    """Blog post categories for dermatology, trichology, and aesthetics."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'category_slug': self.slug})

    @property
    def published_posts(self):
        """Return only published posts in this category."""
        return self.posts.filter(status='published')


class Tag(models.Model):
    """Topical tags for blog articles."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = 'Article Tag'
        verbose_name_plural = 'Article Tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_slug': self.slug})


class BlogPost(models.Model):
    """Clinical blog article / educational post."""

    STATUS_CHOICES = [
        ('draft', 'Draft / Unpublished'),
        ('published', 'Published'),
    ]

    title = models.CharField(
        max_length=300,
        verbose_name='Blog Title',
        help_text='Headline of the article',
    )
    slug = models.SlugField(
        max_length=320,
        unique=True,
        blank=True,
        help_text='SEO-friendly permanent URL slug (auto-generated from title)',
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Category',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
        verbose_name='Tags',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts',
        verbose_name='Author',
    )
    featured_image = models.ImageField(
        upload_to='blog/',
        blank=True,
        null=True,
        verbose_name='Featured Image',
        help_text='Cover image displayed in article listings and detail header',
    )
    excerpt = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Short Description',
        help_text='Short description or summary displayed on blog listing cards',
    )
    content = models.TextField(
        verbose_name='Full Content',
        help_text='Full article body content with paragraphs',
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        verbose_name='Publication Status',
        help_text='Published articles appear on the public website; draft articles remain private.',
    )
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Featured Article',
        help_text='Pin as spotlight article at top of blog',
    )
    allow_comments = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Incremented each time the post is viewed',
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='SEO Title',
        help_text='Custom title tag for search engines (leave blank to use the blog title)',
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='SEO Description',
        help_text='Meta description for search engine snippets (leave blank to use the short description)',
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Published Date',
        help_text='Date and time when the article is published (auto-set when published)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blog Article / Post'
        verbose_name_plural = 'Blog Articles & Posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-populate published_at when published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def short_description(self):
        """Convenience property for short description."""
        if self.excerpt:
            return self.excerpt
        if len(self.content) > 180:
            return self.content[:177] + '...'
        return self.content

    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == 'published'

    @property
    def reading_time(self):
        """Estimated reading time in minutes (avg 200 words/min)."""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))
