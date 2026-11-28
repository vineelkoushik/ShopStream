
import json
import signal
import time

from confluent_kafka import Consumer, KafkaError, Producer

from app.config import settings
from app.events.handlers import handle_product_event


class AIProductConsumer:
    def __init__(self):
        self.consumer = Consumer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP,
            "group.id": "ai-group",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })

        self.producer = Producer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP
        })

        self.consumer.subscribe([
            "product.created",
            "product.updated",
            "product.deleted"
        ])

        self.running = True

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        print("Shutting down AI product consumer...", flush=True)
        self.running = False

    def publish_to_dlq(self, msg):
        dlq_topic = f"{msg.topic()}.dlq"
        delivery_result = {"delivered": False, "error": None}

        def on_delivery(err, delivered_msg):
            if err:
                delivery_result["error"] = err
            else:
                delivery_result["delivered"] = True

        self.producer.produce(
            topic=dlq_topic,
            key=msg.key(),
            value=msg.value(),
            callback=on_delivery,
        )

        remaining = self.producer.flush(10)

        if remaining > 0:
            raise RuntimeError("DLQ delivery timed out")

        if delivery_result["error"]:
            raise RuntimeError(
                f"DLQ delivery failed: {delivery_result['error']}"
            )

        if not delivery_result["delivered"]:
            raise RuntimeError("DLQ delivery was not confirmed")

        print(
            f"Message successfully published to {dlq_topic}",
            flush=True,
        )

    def start(self):
        print(
            "AI product consumer started. Listening...",
            flush=True
        )

        try:
            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue

                    print(
                        f"Consumer error: {msg.error()}",
                        flush=True
                    )
                    continue

                success = False

                for attempt in range(3):
                    try:
                        event = json.loads(msg.value())
                        handle_product_event(event)

                        success = True
                        break

                    except Exception as e:
                        print(
                            f"Attempt {attempt + 1} failed: {e}",
                            flush=True
                        )

                        if attempt < 2:
                            wait_time = 2 ** attempt

                            print(
                                f"Retrying after {wait_time} seconds...",
                                flush=True
                            )

                            time.sleep(wait_time)

                if success:
                    try:
                        self.consumer.commit(
                            message=msg,
                            asynchronous=False
                        )

                        print(
                            "Product event processed successfully. "
                            "Offset committed.",
                            flush=True
                        )

                    except Exception as e:
                        print(
                            f"Offset commit failed: {e}",
                            flush=True
                        )

                        self.running = False
                        break

                else:
                    print(
                        f"Moving failed message to {msg.topic()}.dlq",
                        flush=True
                    )

                    try:
                        self.publish_to_dlq(msg)

                        self.consumer.commit(
                            message=msg,
                            asynchronous=False
                        )

                        print(
                            "Original offset committed after DLQ delivery.",
                            flush=True
                        )

                    except Exception as e:
                        print(
                            f"DLQ handling failed: {e}. "
                            "Stopping without committing offset.",
                            flush=True
                        )

                        self.running = False
                        break

        finally:
            self.consumer.close()
            print("AI product consumer closed.", flush=True)


if __name__ == "__main__":
    AIProductConsumer().start()
