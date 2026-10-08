from django.db import models
from django.utils.text import slugify


class Doctor(models.Model):
    """Doctor / specialist profile."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES,
        blank=True,
    )
    designation = models.CharField(
        max_length=200,
        help_text='e.g. Dermatologist, Trichologist, Cosmetic Surgeon',
    )
    qualifications = models.CharField(
        max_length=300, blank=True,
        help_text='e.g. MBBS, MD (Dermatology), FAAD',
    )
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    banner_image = models.ImageField(
        upload_to='doctors/banners/', blank=True, null=True,
        help_text='Banner for the doctor detail page',
    )
    treatments = models.ManyToManyField(
        'treatments.Treatment', blank=True,
        related_name='doctors',
        help_text='Treatments this doctor performs',
    )
    experience_years = models.PositiveIntegerField(
        default=0, help_text='Years of professional experience',
    )
    consultation_fee = models.CharField(
        max_length=100, blank=True,
        help_text='e.g. ₹500, ₹500 – ₹1,000',
    )
    available_days = models.CharField(
        max_length=200, blank=True,
        help_text='e.g. Mon–Fri, Mon/Wed/Fri',
    )
    available_time = models.CharField(
        max_length=200, blank=True,
        help_text='e.g. 10:00 AM – 4:00 PM',
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor / Specialist'
        verbose_name_plural = 'Doctors & Specialists'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return f'Dr. {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('doctors:doctor_detail', kwargs={'slug': self.slug})

    @property
    def full_title(self):
        """e.g. Dr. Priya Sharma, MD (Dermatology)"""
        parts = [f'Dr. {self.name}']
        if self.qualifications:
            parts.append(self.qualifications)
        return ', '.join(parts)
