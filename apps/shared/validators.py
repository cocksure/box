from django.core.exceptions import ValidationError


def code_name_validate(instance):
    if instance.code == instance.name:
        raise ValidationError("Код и имя не должны быть одинаковыми.")
