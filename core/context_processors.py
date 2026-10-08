import re
from django.conf import settings


def clinic_info(request):
    """
    Make clinic information and SEO available in all templates.
    Pulls from SiteConfiguration and PageSEO models (editable in Admin),
    falling back to settings.py/.env if not configured in DB.
    Also provides active treatments, time slot choices, and canonical URL.
    """
    try:
        from .models import SiteConfiguration, PageSEO
        from treatments.models import Treatment
        from appointments.models import Appointment

        config = SiteConfiguration.load()
        raw_whatsapp = config.whatsapp_number or getattr(settings, 'CLINIC_WHATSAPP', '')
        clean_whatsapp = re.sub(r'\D', '', raw_whatsapp)
        active_treatments = Treatment.objects.filter(is_active=True).only('id', 'name', 'slug').order_by('name')

        # Map current URL name to PageSEO key
        url_name = getattr(request.resolver_match, 'url_name', '') if hasattr(request, 'resolver_match') else ''
        url_to_page = {
            'home': 'home',
            'about': 'about',
            'doctor_list': 'doctors',
            'treatment_list': 'treatments',
            'before_after': 'before_after',
            'before_after_list': 'before_after',
            'gallery_list': 'gallery',
            'testimonials': 'testimonials',
            'post_list': 'blog',
            'category_detail': 'blog',
            'tag_detail': 'blog',
            'offer_list': 'offers',
            'faq': 'faq',
            'contact': 'contact',
            'book_appointment': 'book_appointment',
            'appointment_success': 'book_appointment',
        }
        page_key = url_to_page.get(url_name)
        page_seo = None
        if page_key:
            page_seo = PageSEO.objects.filter(page=page_key).first()

        # Build clean canonical URL (stripping query parameters)
        canonical_url = request.build_absolute_uri(request.path)

        return {
            'site_config': config,
            'page_seo': page_seo,
            'canonical_url': (page_seo.canonical_url if page_seo and page_seo.canonical_url else canonical_url),
            'CLINIC_NAME': config.site_name or getattr(settings, 'CLINIC_NAME', 'Skin & Hair Care Clinic'),
            'CLINIC_PHONE': config.phone_primary or getattr(settings, 'CLINIC_PHONE', ''),
            'CLINIC_EMAIL': config.email_primary or getattr(settings, 'CLINIC_EMAIL', ''),
            'CLINIC_ADDRESS': config.address or getattr(settings, 'CLINIC_ADDRESS', ''),
            'CLINIC_WHATSAPP': raw_whatsapp,
            'CLINIC_WHATSAPP_CLEAN': clean_whatsapp,
            'global_treatments': active_treatments,
            'global_time_slots': Appointment.TIME_SLOT_CHOICES,
        }
    except Exception:
        raw_whatsapp = getattr(settings, 'CLINIC_WHATSAPP', '')
        clean_whatsapp = re.sub(r'\D', '', raw_whatsapp)
        canonical_url = request.build_absolute_uri(request.path) if hasattr(request, 'build_absolute_uri') else ''
        return {
            'site_config': None,
            'page_seo': None,
            'canonical_url': canonical_url,
            'CLINIC_NAME': getattr(settings, 'CLINIC_NAME', 'Skin & Hair Care Clinic'),
            'CLINIC_PHONE': getattr(settings, 'CLINIC_PHONE', ''),
            'CLINIC_EMAIL': getattr(settings, 'CLINIC_EMAIL', ''),
            'CLINIC_ADDRESS': getattr(settings, 'CLINIC_ADDRESS', ''),
            'CLINIC_WHATSAPP': raw_whatsapp,
            'CLINIC_WHATSAPP_CLEAN': clean_whatsapp,
            'global_treatments': [],
            'global_time_slots': [],
        }
