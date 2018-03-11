from django.core.exceptions import ValidationError


def validate_not_new_line(value):
    """Value must not have new line symbols"""
    if '\r' in value or '\n' in value:
        raise ValidationError('Header Injection attempt, delete the new line symbols')
