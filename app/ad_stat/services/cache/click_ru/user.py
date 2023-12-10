from ad_stat.integrations.api.click_ru.api import ClickRuMasterAPIClient
from ad_stat.services.cache.click_ru.base import BaseClickRuDataCache
from common.models import BaseModel
from pydantic import Field


class UserData(BaseModel):
    id: int
    balance: float


class MasterData(BaseModel):
    users: list[UserData] = Field(default_factory=list)


class _MasterUserDataCache(BaseClickRuDataCache):
    KEY = "master_user"
    ITEM_CLASS = MasterData
    TIMEOUT = 1  # TODO move to collector

    def _collet_data(self) -> MasterData:
        return self.ITEM_CLASS(
            users=[
                UserData(id=user_data.id, balance=user_data.balance) for user_data in ClickRuMasterAPIClient().users()
            ]
        )


MasterUserDataCache = _MasterUserDataCache()
