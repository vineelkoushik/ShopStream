
from app.events.consumer import BaseConsumer
from app.events.handlers import route_event


def main():
    consumer = BaseConsumer(
        group_id="notification-group",
        topics=[
            "order.confirmed",
            "order.cancelled"
        ]
    )

    consumer.start(route_event)


if __name__ == "__main__":
    main()

