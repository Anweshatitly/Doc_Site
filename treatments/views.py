from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import TreatmentCategory, Treatment, Offer


def treatment_list(request, category_slug=None):
    """
    Treatments Catalog page.
    Displays all medical and aesthetic treatments with category tabs,
    benefits preview, pricing, and keyword search.
    Supports clean SEO URL (/treatments/category/<slug>/) or query parameters (?category=<slug>).
    """
    categories = TreatmentCategory.objects.filter(is_active=True).order_by('order', 'name')
    treatments = Treatment.objects.filter(is_active=True).select_related('category').order_by('category__order', 'name')

    # Category filtering
    selected_category_slug = category_slug or request.GET.get('category')
    selected_category = None
    if selected_category_slug and selected_category_slug != 'all':
        try:
            selected_category = TreatmentCategory.objects.get(slug=selected_category_slug, is_active=True)
            treatments = treatments.filter(category=selected_category)
        except TreatmentCategory.DoesNotExist:
            if category_slug:
                from django.http import Http404
                raise Http404("Treatment category not found.")
            selected_category = None

    # Keyword search
    query = request.GET.get('q', '').strip()
    if query:
        treatments = treatments.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(benefits__icontains=query)
        )

    context = {
        'categories': categories,
        'treatments': treatments,
        'selected_category': selected_category,
        'query': query,
    }
    return render(request, 'treatments/treatment_list.html', context)


def treatment_detail(request, slug):
    """
    Individual Treatment Detail page.
    Provides comprehensive procedure information, medical benefits,
    session duration, pricing, attending specialists, and before/after proofs.
    """
    treatment = get_object_or_404(Treatment, slug=slug, is_active=True)
    doctors = treatment.doctors.filter(is_active=True)
    before_after_images = treatment.before_after_images.filter(is_active=True)
    related_treatments = Treatment.objects.filter(category=treatment.category, is_active=True).exclude(pk=treatment.pk)[:3]
    active_offers = treatment.offers.filter(is_active=True)

    # Convert benefits newline-separated string into a clean list
    benefits_list = [b.strip() for b in treatment.benefits.split('\n') if b.strip()]

    context = {
        'treatment': treatment,
        'doctors': doctors,
        'before_after_images': before_after_images,
        'related_treatments': related_treatments,
        'active_offers': active_offers,
        'benefits_list': benefits_list,
    }
    return render(request, 'treatments/treatment_detail.html', context)


def offer_list(request):
    """
    Special Offers & Treatment Packages page.
    Displays active promotional discounts, bundled packages, and savings.
    """
    offers = Offer.objects.filter(is_active=True).prefetch_related('treatments').order_by('-created_at')

    context = {
        'offers': offers,
    }
    return render(request, 'treatments/offer_list.html', context)
