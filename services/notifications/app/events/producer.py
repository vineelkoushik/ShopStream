import json
from confluent_kafka import Producer
from app.config import settings

producer = Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP})

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")

def publish(topic: str, key: int, event: dict):
    producer.produce(
        topic,
        key=str(key),
        value=json.dumps(event),
        on_delivery=delivery_report
    )
    producer.poll(0)