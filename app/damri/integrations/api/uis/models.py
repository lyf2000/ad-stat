from damri.models.base import BaseModel
from pydantic import Field


class CallReportItemModel(BaseModel):
    """
    Данные звонка.
    """

    id: int
    is_lost: bool
    finish_reason: str
    contact_phone_number: str | None = None
    virtual_phone_number: str
    call_records: list[str] = Field(default_factory=list)
    total_duration: int
