import json

from django.conf import settings
from kafka import KafkaProducer


def kafka_publish(topic, message: dict):
    producer = KafkaProducer(bootstrap_servers=[settings.KAFKA_BROKER_URL])
    producer.send(topic, json.dumps(message).encode("utf-8"))
    producer.flush()
    producer.close()
