from django import template

register = template.Library()

# Curated high-resolution aesthetic clinic images for seamless fallback
FALLBACK_IMAGES = {
    'hero': 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1600&q=80',
    'about': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80',
    'treatment': 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80',
    'doctor_male': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=800&q=80',
    'doctor_female': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=800&q=80',
    'doctor': 'https://images.unsplash.com/photo-1594824813567-93335026938a?auto=format&fit=crop&w=800&q=80',
    'before': 'https://images.unsplash.com/photo-1512290900672-1f41d999037c?auto=format&fit=crop&w=600&q=80',
    'after': 'https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=600&q=80',
    'patient': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80',
    'offer': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80',
    'blog': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
    'gallery': 'https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=800&q=80',
}


@register.filter
def fallback_img(image_field, fallback_type='treatment'):
    """
    Returns image_field.url if available, else a relevant high-resolution clinic image.
    """
    if image_field:
        try:
            return image_field.url
        except Exception:
            pass
    return FALLBACK_IMAGES.get(fallback_type, FALLBACK_IMAGES['treatment'])


@register.filter
def split_lines(text):
    """Splits a multi-line string into a list of non-empty stripped strings."""
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]
