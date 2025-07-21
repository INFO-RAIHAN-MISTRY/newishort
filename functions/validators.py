from django.core.exceptions import ValidationError
import os

def validate_xlsx_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extension = ['.xlsx']

    if not ext.lower() in valid_extension:
        raise ValidationError('only .xlsx files are allowed')

