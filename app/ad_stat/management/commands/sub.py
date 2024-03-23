import json
import logging

from ad_stat.tasks import state_notify
from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.debug("Starting consumer")
        consumer = KafkaConsumer(
            bootstrap_servers=[settings.KAFKA_BROKER_URL],
            auto_offset_reset="earliest",
            group_id="my-group",  # Change as needed
        )
        consumer.subscribe(["state_notify"])

        try:
            while True:
                logger.debug("Consuming")
                msg = consumer.poll(1.0)

                if not msg:
                    continue

                msg = list(msg.values())[0][0]
                print("aaaaaaa", msg)
                json_message = json.loads(msg.value.decode())
                try:
                    state_notify(
                        start_date=json_message["start_date"],
                        end_date=json_message["end_date"],
                        builder_name=json_message["builder_name"],
                        company_id=json_message["company_id"],
                    )
                except Exception as e:
                    print(e)
        finally:
            consumer.close()
