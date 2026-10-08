from django.db import models


class SiteConfiguration(models.Model):
    """Singleton model for site-wide configuration managed via Django Admin."""

    # ── Branding ──
    site_name = models.CharField(max_length=200, default='Skin & Hair Care Clinic')
    tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    logo_dark = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Logo variant for dark backgrounds',
    )
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)

    # ── About ──
    about_short = models.TextField(
        blank=True, help_text='Short intro for the homepage hero section',
    )
    about_full = models.TextField(
        blank=True, help_text='Detailed text for the About Us page',
    )
    hero_image = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Homepage hero background image',
    )
    about_image = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Image shown on the About section / page',
    )

    # ── Contact ──
    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email_primary = models.EmailField(blank=True)
    email_secondary = models.EmailField(blank=True)
    whatsapp_number = models.CharField(
        max_length=20, blank=True,
        help_text='Include country code, e.g. +919876543210',
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # ── Working Hours ──
    working_hours_weekday = models.CharField(
        max_length=100, blank=True,
        help_text='e.g. Mon–Fri: 9:00 AM – 7:00 PM',
    )
    working_hours_weekend = models.CharField(
        max_length=100, blank=True,
        help_text='e.g. Sat: 9:00 AM – 2:00 PM',
    )

    # ── Maps ──
    google_maps_embed = models.TextField(
        blank=True, help_text='Full Google Maps embed <iframe> code',
    )
    google_maps_link = models.URLField(
        blank=True, help_text='Direct Google Maps link for the "Get Directions" button',
    )

    # ── Social Media ──
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    # ── SEO ──
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)

    # ── Misc ──
    footer_text = models.TextField(
        blank=True, help_text='Extra text shown in the site footer',
    )

    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'

    def __str__(self):
        return self.site_name

    def clean(self):
        super().clean()
        if self.google_maps_embed:
            content = self.google_maps_embed.strip().lower()
            # Enforce that embed is an iframe and contains no scripts or malicious attributes
            if not content.startswith('<iframe') or not content.endswith('</iframe>'):
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'google_maps_embed': 'Google Maps embed code must be a valid <iframe>...</iframe> snippet.'
                })
            dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', 'eval(']
            for pattern in dangerous_patterns:
                if pattern in content:
                    from django.core.exceptions import ValidationError
                    raise ValidationError({
                        'google_maps_embed': f'Potentially dangerous content detected in embed code ({pattern}).'
                    })

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        self.clean()
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the singleton instance, creating it on first access."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def clean_whatsapp_number(self):
        """Return clean digits only for wa.me links, e.g. 919876543210."""
        import re
        num = self.whatsapp_number or ''
        return re.sub(r'\D', '', num)

    def get_whatsapp_booking_url(self, patient_name='', treatment='', preferred_date='', preferred_time=''):
        """Generate a pre-filled WhatsApp click-to-chat URL for appointment booking."""
        import urllib.parse
        clean_num = self.clean_whatsapp_number
        if not clean_num:
            return ''

        msg_lines = [
            f"Hello {self.site_name}, I would like to book an appointment:",
            f"• Patient Name: {patient_name or 'N/A'}",
            f"• Selected Treatment: {treatment or 'General Consultation'}",
            f"• Preferred Date: {preferred_date or 'Earliest Available'}",
            f"• Preferred Time: {preferred_time or 'Any Open Slot'}",
            "",
            "Please confirm slot availability. Thank you!"
        ]
        encoded_msg = urllib.parse.quote("\n".join(msg_lines))
        return f"https://wa.me/{clean_num}?text={encoded_msg}"


class PageSEO(models.Model):
    """Configurable SEO metadata for main clinic pages."""

    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('about', 'About Clinic Page'),
        ('doctors', 'Doctors & Specialists Page'),
        ('treatments', 'Treatments Listing Page'),
        ('before_after', 'Before & After Results Page'),
        ('gallery', 'Clinic Gallery Page'),
        ('testimonials', 'Patient Reviews Page'),
        ('blog', 'Blog & Journal Page'),
        ('offers', 'Special Offers Page'),
        ('faq', 'Frequently Asked Questions Page'),
        ('contact', 'Contact & Location Page'),
        ('book_appointment', 'Book Appointment Page'),
    ]

    page = models.CharField(max_length=40, choices=PAGE_CHOICES, unique=True, db_index=True)
    meta_title = models.CharField(
        max_length=200, blank=True,
        help_text='Custom SEO title for browser tab and search engines (leave blank for defaults)',
    )
    meta_description = models.CharField(
        max_length=320, blank=True,
        help_text='Meta description for search engine snippets (150–160 chars recommended)',
    )
    meta_keywords = models.CharField(
        max_length=300, blank=True,
        help_text='Comma-separated SEO keywords',
    )
    canonical_url = models.CharField(
        max_length=300, blank=True,
        help_text='Custom canonical URL (defaults to current page URL if blank)',
    )
    og_image = models.ImageField(
        upload_to='seo/', blank=True, null=True,
        help_text='Custom social share banner image (1200x630px recommended)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page SEO Configuration'
        verbose_name_plural = 'Pages SEO Configuration'
        ordering = ['page']

    def __str__(self):
        return f'{self.get_page_display()} SEO'


class Testimonial(models.Model):
    """Patient testimonials displayed on the homepage."""

    name = models.CharField(max_length=100)
    designation = models.CharField(
        max_length=100, blank=True,
        help_text='e.g. Patient, Client',
    )
    location = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
    )
    treatment = models.ForeignKey(
        'treatments.Treatment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='testimonials',
        help_text='Treatment this testimonial relates to',
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='testimonials',
        help_text='Doctor this testimonial relates to',
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.name} \u2014 {self.rating}\u2605'


class FAQ(models.Model):
    """Frequently asked questions."""

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('treatments', 'Treatments'),
        ('appointments', 'Appointments'),
        ('pricing', 'Pricing'),
        ('aftercare', 'Aftercare'),
    ]

    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES,
        default='general', db_index=True,
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question[:80]


class ContactEnquiry(models.Model):
    """Enquiries submitted through the Contact Us form."""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='new', db_index=True,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Internal notes (not visible to the patient)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Enquiry'
        verbose_name_plural = 'Contact Enquiries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f'{self.name} \u2014 {self.subject}'
