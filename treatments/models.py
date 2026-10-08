from django.db import models
from django.utils.text import slugify


class TreatmentCategory(models.Model):
    """Top-level grouping for treatments (e.g. Skin Care, Hair Care, Laser)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(
        max_length=50, blank=True,
        help_text='Bootstrap icon class, e.g. bi-heart-pulse',
    )
    image = models.ImageField(upload_to='treatments/categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Treatment Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def active_treatments(self):
        """Return only active treatments in this category."""
        return self.treatments.filter(is_active=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('treatments:category_detail', kwargs={'category_slug': self.slug})


class Treatment(models.Model):
    """Individual treatment or service offered by the clinic."""

    category = models.ForeignKey(
        TreatmentCategory, on_delete=models.CASCADE, related_name='treatments',
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    benefits = models.TextField(
        blank=True,
        help_text='Key benefits, one per line',
    )
    image = models.ImageField(upload_to='treatments/', blank=True, null=True)
    banner_image = models.ImageField(
        upload_to='treatments/banners/', blank=True, null=True,
        help_text='Wide banner image for the detail page header',
    )
    duration = models.CharField(
        max_length=50, blank=True, help_text='e.g. 30\u201345 minutes',
    )
    sessions_required = models.CharField(
        max_length=100, blank=True, help_text='e.g. 4\u20136 sessions',
    )
    price_range = models.CharField(
        max_length=100, blank=True, help_text='e.g. \u20b92,000 \u2013 \u20b95,000',
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Treatment / Procedure'
        verbose_name_plural = 'Treatments & Procedures'
        ordering = ['category__order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('treatments:treatment_detail', kwargs={'slug': self.slug})


class Offer(models.Model):
    """Promotional offer or treatment package."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    treatments = models.ManyToManyField(
        Treatment, blank=True, related_name='offers',
        help_text='Treatments included in this offer',
    )
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    offer_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    discount_text = models.CharField(
        max_length=50, blank=True,
        help_text='e.g. 20% OFF, Buy 1 Get 1 Free',
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Special Offer / Package'
        verbose_name_plural = 'Special Offers & Packages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'end_date']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def savings(self):
        """Calculate savings amount when both prices are set."""
        if self.original_price and self.offer_price:
            return self.original_price - self.offer_price
        return None
