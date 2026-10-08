from django.shortcuts import render, get_object_or_404
from .models import Doctor


def doctor_list(request):
    """
    Doctors & Specialists Directory.
    Showcases our medical team, dermatologists, trichologists, and aesthetic experts.
    """
    doctors = Doctor.objects.filter(is_active=True).prefetch_related('treatments').order_by('order', 'name')

    context = {
        'doctors': doctors,
    }
    return render(request, 'doctors/doctor_list.html', context)


def doctor_detail(request, slug):
    """
    Specialist Profile page.
    Displays doctor credentials, qualifications, biography, performed treatments,
    consultation schedule, patient reviews, and appointment booking CTA.
    """
    doctor = get_object_or_404(Doctor, slug=slug, is_active=True)
    treatments = doctor.treatments.filter(is_active=True)
    testimonials = doctor.testimonials.filter(is_active=True)[:4]
    other_doctors = Doctor.objects.filter(is_active=True).exclude(pk=doctor.pk)[:3]

    context = {
        'doctor': doctor,
        'treatments': treatments,
        'testimonials': testimonials,
        'other_doctors': other_doctors,
    }
    return render(request, 'doctors/doctor_detail.html', context)
