import json
from typing import Hashable

from django.db import models
from pydantic import BaseModel as PydanticBaseModel

null = dict(null=True, blank=True)


# region django


class BaseDjangoModel(models.Model):
    class Meta:
        abstract = True


class TimeStampModel(BaseDjangoModel):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# endregion


# region pydantic


class BaseModel(PydanticBaseModel):
    class Config:
        use_enum_values = True

    def jsonable_dict(self) -> dict:
        return json.loads(self.json())

    def values(self) -> list:
        return list(self.dict().values())

    def keys(self) -> list[str]:
        return list(self.dict().keys())


class BaseFrozenModel(BaseModel):
    class Config(BaseModel.Config):
        frozen = True

    def __hash__(self):
        return hash((type(self),) + tuple([field for field in self.__dict__.values() if isinstance(field, Hashable)]))


# endregion
