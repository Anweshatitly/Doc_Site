import urllib.parse
import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm
from doctors.models import Doctor
from treatments.models import Treatment
from core.models import SiteConfiguration


def book_appointment(request):
    """
    Patient Appointment Booking View.
    Renders the appointment booking form with server-side validation,
    CSRF protection, 'pending' status persistence, and clear flash messages.
    """
    initial_data = {}

    treatment_slug = request.GET.get('treatment')
    if treatment_slug:
        treatment = Treatment.objects.filter(slug=treatment_slug, is_active=True).first()
        if treatment:
            initial_data['treatment'] = treatment

    doctor_slug = request.POST.get('doctor_slug') or request.GET.get('doctor')
    doctor_obj = None
    if doctor_slug:
        doctor_obj = Doctor.objects.filter(slug=doctor_slug, is_active=True).first()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'pending'
            if doctor_obj:
                appointment.doctor = doctor_obj
            appointment.save()

            # Store appointment ID in session for confirmation receipt display
            request.session['last_appointment_id'] = appointment.id
            messages.success(
                request,
                f'Thank you, {appointment.patient_name}! Your appointment booking request has been successfully submitted.'
            )
            return redirect('appointments:appointment_success')
        else:
            messages.error(
                request,
                'There was a problem submitting your appointment request. Please review the highlighted errors below.'
            )
    else:
        form = AppointmentForm(initial=initial_data)

    context = {
        'form': form,
        'doctor_obj': doctor_obj,
        'selected_doctor_slug': doctor_slug if doctor_obj else '',
    }
    return render(request, 'appointments/book_appointment.html', context)


def appointment_success(request):
    """
    Booking Confirmation Receipt page.
    Displays appointment overview, reference number, patient details, and status.
    Provides a pre-filled WhatsApp confirmation CTA.
    """
    appointment_id = request.session.get('last_appointment_id')
    appointment = None
    whatsapp_url = None
    if appointment_id:
        appointment = Appointment.objects.filter(pk=appointment_id).select_related('doctor', 'treatment').first()
        if appointment:
            config = SiteConfiguration.load()
            treatment_name = appointment.treatment.name if appointment.treatment else 'General Consultation'
            date_str = appointment.preferred_date.strftime('%A, %B %d, %Y')
            time_str = appointment.get_preferred_time_display()
            whatsapp_url = config.get_whatsapp_booking_url(
                patient_name=appointment.patient_name,
                treatment=treatment_name,
                preferred_date=date_str,
                preferred_time=time_str,
            )

    context = {
        'appointment': appointment,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, 'appointments/appointment_success.html', context)


def whatsapp_booking(request):
    """
    Generate and redirect to a pre-filled WhatsApp appointment chat.
    Reads:
    - patient_name
    - treatment
    - preferred_date
    - preferred_time
    WhatsApp number is dynamically retrieved from clinic configuration.
    """
    config = SiteConfiguration.load()
    raw_number = config.whatsapp_number or getattr(settings, 'CLINIC_WHATSAPP', '')
    clean_number = re.sub(r'\D', '', raw_number)

    patient_name = request.GET.get('patient_name', '').strip()
    treatment_name = request.GET.get('treatment', '').strip()
    preferred_date = request.GET.get('preferred_date', '').strip()
    preferred_time = request.GET.get('preferred_time', '').strip()

    if not clean_number:
        messages.error(request, 'WhatsApp appointment booking is currently unavailable. Please submit via the booking form.')
        return redirect('appointments:book_appointment')

    whatsapp_url = config.get_whatsapp_booking_url(
        patient_name=patient_name,
        treatment=treatment_name,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
    )
    return redirect(whatsapp_url)
