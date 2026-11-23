from app.events.consumer import BaseConsumer
from app.events.handlers import handle_order_created

def main():
    consumer = BaseConsumer(
        group_id="product-group",
        topics=["order.created"]
    )
    consumer.start(handle_order_created)

if __name__ == "__main__":
    main()