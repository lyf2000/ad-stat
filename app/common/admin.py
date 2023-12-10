from typing import Any

from django import forms
from django.core import validators

SUCCESS_NOTIE_SEND_MSG = "Уведомление в процессе отправки!"
SUCCESS_NOTIE_SEND_MSG_MULTIPLE = "Уведомления в процессе отправки!"
SUCCESS_DATA_LOAD_SENT = "Данные в процессе выгрзки!"
SUCCESS_DATA_LOADED = "Данные успешно выгружены!"


class CommaSeparatedCharField(forms.Field):
    def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
        super().__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(max_length))

    def to_python(self, value: str):
        return ",".join([id.strip() for id in value.split(",")])


class IntegerChoiceField(forms.ChoiceField):
    def to_python(self, value: Any | None) -> Any | None:
        return int(value)


class MultipleIntegerChoiceField(forms.MultipleChoiceField):
    def to_python(self, value: Any | None) -> Any | None:
        return [int(value_) for value_ in super().to_python(value)]
