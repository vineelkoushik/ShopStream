import json
import signal
import sys
from confluent_kafka import Consumer, KafkaError
from app.config import settings

class BaseConsumer:
    def __init__(self, group_id: str, topics: list[str]):
        self.consumer = Consumer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        self.consumer.subscribe(topics)
        self.running = True
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        print("Shutting down consumer...", flush=True)
        self.running = False

    def start(self, handler_func):
        print(f"Consumer started. Listening...", flush=True)
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    print(f"Consumer error: {msg.error()}", flush=True)
                    continue

                event = json.loads(msg.value())
                try:
                    handler_func(event)
                    self.consumer.commit(message=msg)
                except Exception as e:
                    print(f"Error processing message: {e}", flush=True)
        finally:
            self.consumer.close()