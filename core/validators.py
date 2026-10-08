import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from PIL import Image


@deconstructible
class MaxFileSizeValidator:
    """
    Validator to enforce maximum file size on uploads.
    Defends against disk space exhaustion and memory exhaustion DoS.
    """

    def __init__(self, max_size_mb=5):
        self.max_size_mb = max_size_mb
        self.max_bytes = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value and value.size > self.max_bytes:
            raise ValidationError(
                f"File size exceeds the maximum limit of {self.max_size_mb} MB. "
                f"Your file size: {value.size / (1024 * 1024):.1f} MB."
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_size_mb == other.max_size_mb


@deconstructible
class SafeImageValidator:
    """
    Validator to ensure uploaded image files:
    1. Have an approved image file extension.
    2. Contain valid image data verified via Pillow.
    3. Do not exceed extreme resolution limits (prevent Pillow decompression bombs).
    """

    ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.avif')
    MAX_DIMENSION = 5000  # pixels

    def __call__(self, value):
        if not value:
            return

        # 1. Extension Check
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(self.ALLOWED_EXTENSIONS)}."
            )

        # 2. Pillow Content Verification
        try:
            # Copy position or rewind if possible
            if hasattr(value, 'seek'):
                value.seek(0)
            img = Image.open(value)
            img.verify()

            # 3. Dimension Check (reopen since verify() invalidates the image object)
            if hasattr(value, 'seek'):
                value.seek(0)
            img = Image.open(value)
            width, height = img.size
            if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
                raise ValidationError(
                    f"Image resolution ({width}x{height}px) exceeds safe limits of {self.MAX_DIMENSION}x{self.MAX_DIMENSION}px."
                )

            # Rewind file pointer for downstream storage operations
            if hasattr(value, 'seek'):
                value.seek(0)

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError("Invalid or corrupted image file.")

    def __eq__(self, other):
        return isinstance(other, SafeImageValidator)
