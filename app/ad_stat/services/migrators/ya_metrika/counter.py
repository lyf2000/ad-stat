import logging

from ad_stat.models.company import Company
from ad_stat.services.cache.yametrika.manager import YaMetrikaDataCacheManager
from common.migrators import BaseMigrator

logger = logging.getLogger(__name__)


class _YaMetrikaCounterMigrator(BaseMigrator):
    """Миграция данных Я.Директ по Счетчикам с ad_stat.Company"""

    def migrate(self):  # TODO: ограничить по яндекс профилям
        counters = YaMetrikaDataCacheManager.get_counters()
        companies = list(Company.objects.all())

        for counter in counters:
            company = next((company for company in companies if counter.site.lower() == company.site_url.lower()), None)

            if not company:
                logger.info(f"Counter {counter.name}({counter.site}) not found company by site")
                continue

            company.ya_counter_id = counter.id

        result = Company.objects.bulk_update(companies, fields=("ya_counter_id",))
        logger.info(f"Counters migrated! Result: {result}")


YaMetrikaCounterMigrator = _YaMetrikaCounterMigrator()
