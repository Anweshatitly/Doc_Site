from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SiteConfiguration, Testimonial, FAQ, ContactEnquiry
from .forms import ContactEnquiryForm
from treatments.models import TreatmentCategory, Treatment, Offer
from doctors.models import Doctor
from gallery.models import BeforeAfterImage
from blog.models import BlogPost


from django.db.models import Q


def home(request):
    """
    Clinic Homepage view.
    Retrieves all dynamic active/published content from database:
    1. Hero section (site_config)
    2. Short clinic introduction (site_config + stats)
    3. Featured treatments
    4. Skin care treatments
    5. Hair care treatments
    6. Doctors / specialists
    7. Why choose us (clinical metrics & safety protocols)
    8. Before & After transformations
    9. Testimonials
    10. Current offers
    11. Latest blog posts
    12. FAQ
    13. Appointment CTA
    14. Contact information
    15. Footer
    """
    site_config = SiteConfiguration.load()

    # 3. Featured treatments (only active and featured)
    featured_treatments = Treatment.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category').order_by('category__order', 'name')[:6]

    # 4. Skin care treatments
    skin_category = TreatmentCategory.objects.filter(
        is_active=True
    ).filter(
        Q(slug__icontains='skin') | Q(name__icontains='skin')
    ).first()

    skin_treatments = Treatment.objects.filter(
        is_active=True
    ).filter(
        Q(category__slug__icontains='skin') | Q(category__name__icontains='skin')
    ).select_related('category').order_by('name')[:6]

    # 5. Hair care treatments
    hair_category = TreatmentCategory.objects.filter(
        is_active=True
    ).filter(
        Q(slug__icontains='hair') | Q(name__icontains='hair')
    ).first()

    hair_treatments = Treatment.objects.filter(
        is_active=True
    ).filter(
        Q(category__slug__icontains='hair') | Q(category__name__icontains='hair')
    ).select_related('category').order_by('name')[:6]

    # 6. Doctors / specialists (active only)
    doctors = Doctor.objects.filter(
        is_active=True
    ).order_by('order', 'name')[:4]

    # 7. Metrics for Why Choose Us
    doctor_count = Doctor.objects.filter(is_active=True).count()
    treatment_count = Treatment.objects.filter(is_active=True).count()
    case_count = BeforeAfterImage.objects.filter(is_active=True).count()
    testimonial_count = Testimonial.objects.filter(is_active=True).count()

    # 8. Before & After transformations (active only)
    before_after_cases = BeforeAfterImage.objects.filter(
        is_active=True
    ).select_related('treatment', 'treatment__category').order_by('order', '-created_at')[:6]

    # 9. Testimonials (active only, prioritized by featured & rating)
    testimonials = Testimonial.objects.filter(
        is_active=True
    ).select_related('treatment', 'doctor').order_by('-is_featured', '-rating', '-created_at')[:6]

    # 10. Current active offers
    current_offers = Offer.objects.filter(
        is_active=True
    ).prefetch_related('treatments').order_by('-created_at')[:3]

    # 11. Latest published blog articles
    latest_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('category', 'author').prefetch_related('tags').order_by('-published_at')[:3]

    # 12. FAQ (active only)
    faqs = FAQ.objects.filter(
        is_active=True
    ).order_by('order', '-created_at')[:6]

    context = {
        'site_config': site_config,
        'featured_treatments': featured_treatments,
        'skin_category': skin_category,
        'skin_treatments': skin_treatments,
        'hair_category': hair_category,
        'hair_treatments': hair_treatments,
        'doctors': doctors,
        'doctor_count': doctor_count,
        'treatment_count': treatment_count,
        'case_count': case_count,
        'testimonial_count': testimonial_count,
        'before_after_cases': before_after_cases,
        'testimonials': testimonials,
        'current_offers': current_offers,
        'latest_posts': latest_posts,
        'faqs': faqs,
    }
    return render(request, 'core/home.html', context)



def about(request):
    """
    About Us page.
    Highlights clinic mission, advanced medical infrastructure, safety protocols,
    and board-certified medical leadership.
    """
    site_config = SiteConfiguration.load()
    doctors = Doctor.objects.filter(is_active=True).order_by('order')
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:3]
    treatment_count = Treatment.objects.filter(is_active=True).count()
    doctor_count = doctors.count()

    context = {
        'site_config': site_config,
        'doctors': doctors,
        'testimonials': testimonials,
        'treatment_count': treatment_count,
        'doctor_count': doctor_count,
    }
    return render(request, 'core/about.html', context)


def testimonials(request):
    """
    Patient Testimonials & Reviews page.
    Displays patient stories, star ratings, and treatment experiences.
    """
    site_config = SiteConfiguration.load()
    all_testimonials = Testimonial.objects.filter(is_active=True).select_related('treatment', 'doctor').order_by('-is_featured', '-created_at')

    # Optional filter by rating or treatment
    rating_filter = request.GET.get('rating')
    if rating_filter and rating_filter.isdigit():
        all_testimonials = all_testimonials.filter(rating=int(rating_filter))

    context = {
        'site_config': site_config,
        'testimonials': all_testimonials,
        'selected_rating': rating_filter,
    }
    return render(request, 'core/testimonials.html', context)


def faq(request):
    """
    Frequently Asked Questions page.
    Organized by category (General, Treatments, Appointments, Pricing, Aftercare).
    """
    site_config = SiteConfiguration.load()
    category_filter = request.GET.get('category', 'all')
    faqs = FAQ.objects.filter(is_active=True).order_by('order', '-created_at')

    if category_filter and category_filter != 'all':
        faqs = faqs.filter(category=category_filter)

    context = {
        'site_config': site_config,
        'faqs': faqs,
        'categories': FAQ.CATEGORY_CHOICES,
        'selected_category': category_filter,
    }
    return render(request, 'core/faq.html', context)


def contact(request):
    """
    Contact Us page.
    Provides address, interactive map, operating hours, and processes
    patient inquiries with validation and flash notifications.
    """
    site_config = SiteConfiguration.load()

    if request.method == 'POST':
        form = ContactEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            messages.success(
                request,
                f'Thank you, {enquiry.name}! Your message has been received. Our clinical concierge will be in touch with you shortly.'
            )
            return redirect('core:contact')
        else:
            # Check for honeypot bot trap
            if 'website_url' in form.errors:
                # Silently redirect bots without saving spam to database
                return redirect('core:contact')
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
    else:
        form = ContactEnquiryForm()

    context = {
        'site_config': site_config,
        'form': form,
    }
    return render(request, 'core/contact.html', context)


def custom_404(request, exception=None):
    """Custom 404 error page."""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, 'errors/500.html', status=500)


def robots_txt(request):
    """Dynamic robots.txt endpoint linking to XML sitemap."""
    from django.http import HttpResponse
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /appointments/success/\n"
        "Allow: /\n\n"
        f"Sitemap: {sitemap_url}\n"
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
