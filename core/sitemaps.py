from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from treatments.models import Treatment, TreatmentCategory
from doctors.models import Doctor
from blog.models import BlogPost, BlogCategory


class StaticViewSitemap(Sitemap):
    """Sitemap for high-level clinic pages."""

    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:about',
            'treatments:treatment_list',
            'doctors:doctor_list',
            'gallery:before_after',
            'gallery:gallery_list',
            'core:testimonials',
            'blog:post_list',
            'treatments:offer_list',
            'core:faq',
            'core:contact',
            'appointments:book_appointment',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'core:home':
            return 1.0
        elif item in ('treatments:treatment_list', 'doctors:doctor_list', 'appointments:book_appointment'):
            return 0.9
        return 0.8


class TreatmentSitemap(Sitemap):
    """Sitemap for individual treatment and procedure pages."""

    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Treatment.objects.filter(is_active=True).order_by('category__order', 'name')

    def location(self, item):
        return reverse('treatments:treatment_detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


class TreatmentCategorySitemap(Sitemap):
    """Sitemap for treatment department categories."""

    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return TreatmentCategory.objects.filter(is_active=True).order_by('order', 'name')

    def location(self, item):
        return reverse('treatments:category_detail', kwargs={'category_slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


class DoctorSitemap(Sitemap):
    """Sitemap for doctor and specialist profile pages."""

    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Doctor.objects.filter(is_active=True).order_by('order', 'name')

    def location(self, item):
        return reverse('doctors:doctor_detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


class BlogPostSitemap(Sitemap):
    """Sitemap for published blog and editorial articles."""

    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')

    def location(self, item):
        return reverse('blog:post_detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


class BlogCategorySitemap(Sitemap):
    """Sitemap for blog categories."""

    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogCategory.objects.filter(is_active=True).order_by('name')

    def location(self, item):
        return reverse('blog:category_detail', kwargs={'category_slug': item.slug})


sitemaps = {
    'static': StaticViewSitemap,
    'treatments': TreatmentSitemap,
    'treatment_categories': TreatmentCategorySitemap,
    'doctors': DoctorSitemap,
    'blog': BlogPostSitemap,
    'blog_categories': BlogCategorySitemap,
}
