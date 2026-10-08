import re
import datetime
from django import forms
from django.utils import timezone
from .models import Appointment
from treatments.models import Treatment


class AppointmentForm(forms.ModelForm):
    """
    Patient-facing appointment booking ModelForm with comprehensive
    server-side validation:
    - Patient Name (required, min 2 chars, letters check)
    - Phone Number (required, format regex, 10-15 digits)
    - Email (required, valid RFC format)
    - Treatment (required, active treatments only)
    - Preferred Date (required, today or future, up to 180 days)
    - Preferred Time (required, valid slot choice, not in past if today)
    - Message (optional, patient notes or concerns)
    """

    class Meta:
        model = Appointment
        fields = [
            'patient_name',
            'patient_phone',
            'patient_email',
            'treatment',
            'preferred_date',
            'preferred_time',
            'message',
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name (e.g. Jane Doe)',
                'autocomplete': 'name',
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 98765 43210 or 10-digit number',
                'autocomplete': 'tel',
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'autocomplete': 'email',
            }),
            'treatment': forms.Select(attrs={
                'class': 'form-select',
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'preferred_time': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us briefly about your skin or hair concern, symptoms, or any specific requests (optional)...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Explicitly configure required fields
        self.fields['patient_name'].required = True
        self.fields['patient_phone'].required = True
        self.fields['patient_email'].required = True
        self.fields['treatment'].required = True
        self.fields['preferred_date'].required = True
        self.fields['preferred_time'].required = True
        self.fields['message'].required = False

        # Restrict treatment dropdown to active treatments ordered by category
        self.fields['treatment'].queryset = (
            Treatment.objects.filter(is_active=True)
            .select_related('category')
            .order_by('category__name', 'name')
        )
        self.fields['treatment'].empty_label = "-- Select Treatment / Service --"

        # Time slot choices with placeholder
        self.fields['preferred_time'].choices = [
            ('', '-- Select Preferred Time Slot --')
        ] + list(Appointment.TIME_SLOT_CHOICES)

        # Restrict date picker in HTML
        today = timezone.localdate()
        self.fields['preferred_date'].widget.attrs['min'] = today.isoformat()
        max_date = today + datetime.timedelta(days=180)
        self.fields['preferred_date'].widget.attrs['max'] = max_date.isoformat()

        # Apply Bootstrap .is-invalid class to fields with validation errors when bound
        if self.is_bound:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    css_class = field.widget.attrs.get('class', '')
                    if 'is-invalid' not in css_class:
                        field.widget.attrs['class'] = f"{css_class} is-invalid".strip()

    def clean_patient_name(self):
        name = self.cleaned_data.get('patient_name', '').strip()
        if not name:
            raise forms.ValidationError("Please provide your full name.")
        if len(name) < 2:
            raise forms.ValidationError("Full name must be at least 2 characters long.")
        if not any(char.isalpha() for char in name):
            raise forms.ValidationError("Please enter a valid name containing letters.")
        return name

    def clean_patient_phone(self):
        phone = self.cleaned_data.get('patient_phone', '').strip()
        if not phone:
            raise forms.ValidationError("Please provide a valid contact phone number.")

        # Ensure allowed characters: digits, spaces, hyphens, parentheses, and leading '+'
        if not re.match(r'^\+?[0-9\s\-()]{7,25}$', phone):
            raise forms.ValidationError(
                "Please enter a valid phone number. Allowed characters: digits, spaces, hyphens, parentheses, and optional '+' prefix."
            )

        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10:
            raise forms.ValidationError(
                f"Phone number must contain at least 10 digits (you entered {len(digits_only)} digits)."
            )
        if len(digits_only) > 15:
            raise forms.ValidationError(
                f"Phone number cannot exceed 15 digits according to international standards (you entered {len(digits_only)} digits)."
            )
        if len(set(digits_only)) == 1:
            raise forms.ValidationError("Please enter a legitimate phone number, not repeated identical digits.")

        return phone

    def clean_patient_email(self):
        email = self.cleaned_data.get('patient_email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email address is required for appointment confirmation.")
        return email

    def clean_treatment(self):
        treatment = self.cleaned_data.get('treatment')
        if not treatment:
            raise forms.ValidationError("Please select the treatment or clinical service you wish to book.")
        if not treatment.is_active:
            raise forms.ValidationError("The selected treatment is currently unavailable. Please select another treatment.")
        return treatment

    def clean_preferred_date(self):
        date = self.cleaned_data.get('preferred_date')
        if not date:
            raise forms.ValidationError("Please select your preferred consultation date.")

        today = timezone.localdate()
        if date < today:
            raise forms.ValidationError("Appointment date cannot be in the past. Please choose today or an upcoming date.")

        max_allowed = today + datetime.timedelta(days=180)
        if date > max_allowed:
            raise forms.ValidationError(
                f"Appointments can only be scheduled up to 6 months in advance (on or before {max_allowed.strftime('%B %d, %Y')})."
            )
        return date

    def clean_preferred_time(self):
        time_slot = self.cleaned_data.get('preferred_time', '').strip()
        if not time_slot:
            raise forms.ValidationError("Please select a preferred time slot.")

        valid_slots = [choice[0] for choice in Appointment.TIME_SLOT_CHOICES]
        if time_slot not in valid_slots:
            raise forms.ValidationError("Please select a valid time slot from the schedule.")
        return time_slot

    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        preferred_time = cleaned_data.get('preferred_time')

        # If booking for today, verify the selected time slot has not already passed
        if preferred_date and preferred_time:
            today = timezone.localdate()
            if preferred_date == today:
                now = timezone.localtime()
                try:
                    slot_hour, slot_minute = map(int, preferred_time.split(':'))
                    slot_time = datetime.time(slot_hour, slot_minute)
                    if slot_time <= now.time():
                        self.add_error(
                            'preferred_time',
                            f"The {preferred_time} slot has already passed for today. Please select a later time slot or an upcoming date."
                        )
                except (ValueError, TypeError):
                    pass

        return cleaned_data
