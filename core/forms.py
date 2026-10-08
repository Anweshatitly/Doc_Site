import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import ContactEnquiry


class ContactEnquiryForm(forms.ModelForm):
    """
    Secure ModelForm for patient inquiries with:
    - Input sanitization & length limits
    - RFC-compliant email validation
    - Phone number validation (10-15 digits, international friendly)
    - Anti-spam Honeypot field (hidden from humans, catches automated bots)
    """

    # Honeypot field — bots fill this out, humans don't see it
    website_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'aria-hidden': 'true',
            'style': 'display:none !important;',
        }),
    )

    class Meta:
        model = ContactEnquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'autocomplete': 'name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'autocomplete': 'email',
                'required': 'required',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 98765 43210',
                'autocomplete': 'tel',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject (e.g., HydraFacial inquiry)',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us how we can help you...',
                'required': 'required',
            }),
        }

    def clean_website_url(self):
        """Honeypot trap: if this hidden field is populated, flag as spam."""
        honeypot_value = self.cleaned_data.get('website_url')
        if honeypot_value:
            raise ValidationError("Spam bot detected.")
        return honeypot_value

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError("Please provide a valid name (at least 2 characters).")
        if len(name) > 100:
            raise ValidationError("Name is too long (maximum 100 characters).")
        # Ensure name doesn't contain suspicious protocol prefixes
        if any(bad in name.lower() for bad in ('http://', 'https://', '<script', '<')):
            raise ValidationError("Name contains invalid characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        validate_email(email)
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValidationError("Please provide a valid phone number (10 to 15 digits).")
        return phone

    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '').strip()
        if len(subject) > 200:
            raise ValidationError("Subject must be 200 characters or fewer.")
        return subject or 'General Inquiry'

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise ValidationError("Message is too short (at least 10 characters required).")
        if len(message) > 3000:
            raise ValidationError("Message is too long (maximum 3,000 characters).")
        return message
