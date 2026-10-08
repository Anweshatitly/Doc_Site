from django.shortcuts import render, get_object_or_404
from .models import GalleryCategory, GalleryImage, BeforeAfterImage
from treatments.models import TreatmentCategory


def gallery_list(request):
    """
    Clinic Photo Gallery page.
    Categorized photos of treatment suites, clinical equipment, ambience, and team.
    """
    categories = GalleryCategory.objects.filter(is_active=True).order_by('order', 'name')
    images = GalleryImage.objects.filter(is_active=True).select_related('category').order_by('order', '-uploaded_at')

    # Category filter
    selected_slug = request.GET.get('category')
    selected_category = None
    if selected_slug and selected_slug != 'all':
        selected_category = get_object_or_404(GalleryCategory, slug=selected_slug, is_active=True)
        images = images.filter(category=selected_category)

    context = {
        'categories': categories,
        'images': images,
        'selected_category': selected_category,
    }
    return render(request, 'gallery/gallery_list.html', context)


def before_after_list(request):
    """
    Before & After Clinical Outcomes page.
    Real patient transformations with procedure notes, session details, and side-by-side proofs.
    """
    treatment_categories = TreatmentCategory.objects.filter(is_active=True).order_by('order')
    cases = BeforeAfterImage.objects.filter(is_active=True).select_related('treatment', 'treatment__category').order_by('order', '-created_at')

    # Category filter
    cat_slug = request.GET.get('category')
    selected_cat = None
    if cat_slug and cat_slug != 'all':
        selected_cat = get_object_or_404(TreatmentCategory, slug=cat_slug, is_active=True)
        cases = cases.filter(treatment__category=selected_cat)

    context = {
        'treatment_categories': treatment_categories,
        'cases': cases,
        'selected_cat': selected_cat,
    }
    return render(request, 'gallery/before_after_list.html', context)
