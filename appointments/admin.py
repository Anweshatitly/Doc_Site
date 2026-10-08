from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for clinic patient appointment requests and scheduling."""

    list_display = (
        'status',
        'patient_name',
        'contact_display',
        'treatment_display',
        'doctor_display',
        'slot_display',
        'created_at',
    )
    list_display_links = ('patient_name',)
    list_filter = ('status', 'preferred_date', 'treatment', 'doctor')
    search_fields = ('patient_name', 'patient_email', 'patient_phone', 'message', 'admin_notes')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'preferred_date'
    autocomplete_fields = ('treatment', 'doctor')
    ordering = ('-preferred_date', 'preferred_time', '-created_at')
    actions = (
        'mark_as_pending',
        'mark_as_confirmed',
        'mark_as_completed',
        'mark_as_cancelled',
        'mark_as_rescheduled',
        'mark_as_no_show',
    )

    fieldsets = (
        ('👤 Patient Demographics & Contact', {
            'description': 'Patient identifying details provided during online booking.',
            'fields': (
                ('patient_name', 'patient_email'),
                ('patient_phone', 'patient_age', 'patient_gender'),
            ),
        }),
        ('📅 Appointment Schedule & Service Details', {
            'description': 'Procedure requested, date, time slot, and assigned specialist.',
            'fields': (
                ('treatment', 'doctor'),
                ('preferred_date', 'preferred_time'),
                'message',
            ),
        }),
        ('🏥 Clinic Workflow & Internal Records', {
            'description': 'Update booking status (Pending, Confirmed, Completed, Cancelled) and log internal notes.',
            'fields': (
                'status',
                'admin_notes',
            ),
        }),
        ('⏱️ Booking Timestamps', {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
    )

    @admin.display(description='Contact')
    def contact_display(self, obj):
        return format_html(
            '<div><a href="tel:{0}" style="color:#2a7a6e; font-weight:600; font-size:12px;">📞 {0}</a></div>'
            '<div><a href="mailto:{1}" style="color:#64748b; font-size:11px;">✉️ {1}</a></div>',
            obj.patient_phone, obj.patient_email
        )

    @admin.display(description='Doctor', ordering='doctor')
    def doctor_display(self, obj):
        if obj.doctor:
            return format_html('<strong>Dr. {0}</strong>', obj.doctor.name)
        return format_html('<span style="color:#94a3b8; font-style:italic;">Unassigned / Any Doctor</span>')

    @admin.display(description='Treatment', ordering='treatment')
    def treatment_display(self, obj):
        if obj.treatment:
            return format_html('<span style="color:#2a7a6e; font-weight:600;">{0}</span>', obj.treatment.name)
        return format_html('<span style="color:#94a3b8; font-style:italic;">General Consultation</span>')

    @admin.display(description='Date & Time', ordering='preferred_date')
    def slot_display(self, obj):
        return format_html(
            '<div><strong>{0}</strong></div>'
            '<small style="color:#0284c7; font-weight:600;">⏰ {1}</small>',
            obj.preferred_date, obj.get_preferred_time_display()
        )

    @admin.action(description='⏳ Mark selected as Pending')
    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} appointment(s) marked as Pending.', messages.INFO)

    @admin.action(description='✅ Mark selected as Confirmed')
    def mark_as_confirmed(self, request, queryset):
        count = queryset.update(status='confirmed')
        self.message_user(request, f'{count} appointment(s) marked as Confirmed.', messages.SUCCESS)

    @admin.action(description='🎉 Mark selected as Completed')
    def mark_as_completed(self, request, queryset):
        count = queryset.update(status='completed')
        self.message_user(request, f'{count} appointment(s) marked as Completed.', messages.SUCCESS)

    @admin.action(description='❌ Mark selected as Cancelled')
    def mark_as_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'{count} appointment(s) marked as Cancelled.', messages.WARNING)

    @admin.action(description='🔄 Mark selected as Rescheduled')
    def mark_as_rescheduled(self, request, queryset):
        count = queryset.update(status='rescheduled')
        self.message_user(request, f'{count} appointment(s) marked as Rescheduled.', messages.INFO)

    @admin.action(description='⚠️ Mark selected as No Show')
    def mark_as_no_show(self, request, queryset):
        count = queryset.update(status='no_show')
        self.message_user(request, f'{count} appointment(s) marked as No Show.', messages.WARNING)
