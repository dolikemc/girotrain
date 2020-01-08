from django.utils import translation


class TranslatedField:
    def __init__(self, de_field, it_field):
        self.de_field = de_field
        self.it_field = it_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'it':
            return getattr(instance, self.it_field)
        else:
            return getattr(instance, self.de_field)
