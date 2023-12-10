from typing import TypeVar

from django.db.models import Model as Model_

Model = TypeVar("Model", bound=Model_)


class ModelService:
    MODEL: Model = None

    def create(obj: Model, *args, **kwargs) -> Model:
        obj.save()

        return obj
