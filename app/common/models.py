import json
from io import BytesIO
from typing import Hashable

from django.core.files.base import ContentFile
from django.db import models
from pydantic import BaseModel as PydanticBaseModel

null = dict(null=True, blank=True)


# region pydantic


class BaseModel(PydanticBaseModel):
    class Config:
        use_enum_values = True

    def jsonable_dict(self) -> dict:
        return json.loads(self.json())


class BaseFrozenModel(BaseModel):
    class Config(BaseModel.Config):
        frozen = True

    def __hash__(self):
        return hash((type(self),) + tuple([field for field in self.__dict__.values() if isinstance(field, Hashable)]))


# endregion


# region django


class BaseDjangoModel(models.Model):
    class Meta:
        abstract = True


class TimeStampModel(BaseDjangoModel):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def save_to_file_field(content: bytes | BytesIO, name) -> ContentFile:
    if type(content) is BytesIO:
        content = content.read()
    return ContentFile(content, name)


# endregion
