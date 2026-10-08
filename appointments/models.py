from django.db import models


class Appointment(models.Model):
    """Patient appointment booking."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00', '09:00 AM'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('12:30', '12:30 PM'),
        ('14:00', '02:00 PM'),
        ('14:30', '02:30 PM'),
        ('15:00', '03:00 PM'),
        ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
        ('17:00', '05:00 PM'),
        ('17:30', '05:30 PM'),
        ('18:00', '06:00 PM'),
    ]

    # ── Patient Info ──
    patient_name = models.CharField(max_length=200)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    patient_age = models.PositiveIntegerField(null=True, blank=True)
    patient_gender = models.CharField(
        max_length=10, blank=True,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
    )

    # ── Appointment Details ──
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='appointments',
    )
    treatment = models.ForeignKey(
        'treatments.Treatment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='appointments',
    )
    preferred_date = models.DateField()
    preferred_time = models.CharField(
        max_length=5, choices=TIME_SLOT_CHOICES, default='10:00',
    )
    message = models.TextField(
        blank=True, help_text='Additional notes or concerns',
    )

    # ── Status Tracking ──
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', db_index=True,
    )
    admin_notes = models.TextField(
        blank=True, help_text='Internal notes (not visible to patient)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Appointment Booking'
        verbose_name_plural = 'Appointment Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['preferred_date', 'preferred_time']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f'{self.patient_name} — {self.preferred_date} at {self.get_preferred_time_display()}'
