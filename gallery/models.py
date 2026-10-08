from django.db import models


class GalleryCategory(models.Model):
    """Categories for gallery images (e.g. Clinic, Events, Team)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryImage(models.Model):
    """Individual gallery image."""

    category = models.ForeignKey(
        GalleryCategory, on_delete=models.CASCADE, related_name='images',
    )
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/')
    alt_text = models.CharField(
        max_length=200, blank=True,
        help_text='Accessible alt text for the image (SEO & screen readers)',
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return self.title or f'Image #{self.pk}'


class BeforeAfterImage(models.Model):
    """Before-and-after treatment comparison images."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    treatment = models.ForeignKey(
        'treatments.Treatment', on_delete=models.CASCADE,
        related_name='before_after_images',
    )
    title = models.CharField(
        max_length=200, blank=True,
        help_text='e.g. Acne Treatment \u2014 3-month result',
    )
    before_image = models.ImageField(upload_to='gallery/before_after/')
    after_image = models.ImageField(upload_to='gallery/before_after/')
    description = models.TextField(
        blank=True,
        help_text='Details about the treatment duration, sessions, etc.',
    )
    patient_age = models.PositiveIntegerField(null=True, blank=True)
    patient_gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, blank=True,
    )
    sessions_completed = models.CharField(
        max_length=50, blank=True,
        help_text='e.g. 6 sessions over 3 months',
    )
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Before & After Image'
        verbose_name_plural = 'Before & After Images'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'{self.treatment.name} \u2014 Before/After #{self.pk}'
