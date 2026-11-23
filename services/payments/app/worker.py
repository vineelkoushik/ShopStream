from app.events.consumer import BaseConsumer
from app.events.handlers import handle_inventory_reserved

def main():
    consumer = BaseConsumer(
        group_id="payment-group",
        topics=["inventory.reserved"]
    )
    consumer.start(handle_inventory_reserved)

if __name__ == "__main__":
    main()