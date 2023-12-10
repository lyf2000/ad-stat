
from common.models import BaseModel


class UserModel(BaseModel):
    """Модель Пользователя"""

    id: int
    login: str
    client_id: str  # 'd933ecf8230942f1851ae2dd074ef6cd'
    display_name: str  # 'rdwork'
    real_name: str
    first_name: str
    last_name: str
    sex: str | None  # 'male'
    default_email: str
