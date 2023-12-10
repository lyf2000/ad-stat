from django.db.models import IntegerChoices as DjangoIntegerChoices


class BaseChoices:
    @classmethod
    def as_dict(cls) -> dict:
        return dict(cls.choices)

    @classmethod
    def keys(cls):
        return list(cls.as_dict().keys())


class IntegerChoices(BaseChoices, DjangoIntegerChoices):
    pass
