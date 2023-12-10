from damri.models.base import BaseFrozenModel
from pydantic import Field


class BaseLimitOffsetFilterParams(BaseFrozenModel):
    PAGE_SIZE_FIELD_NAME: str = Field(default="limit", exclude=True)

    offset: int = 1

    def next_page_filter(self) -> "BaseLimitOffsetFilterParams":
        next_offset = self.offset + getattr(self, self.PAGE_SIZE_FIELD_NAME)
        return self.copy(update={"offset": next_offset})

    # def dict(self, *args, exclude=None, **kwagrs):
    #     return super().dict(*args, exclude=set("PAGE_SIZE_FIELD_NAME"), **kwagrs)
