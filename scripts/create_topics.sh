#!/bin/bash

KAFKA_CONTAINER="shopstream-kafka-1"
BOOTSTRAP="localhost:9092"

create_topic() {
    docker exec $KAFKA_CONTAINER /opt/kafka/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP --create --if-not-exists --topic $1 --partitions $2 --replication-factor 1
}

create_topic "order.created" 3
create_topic "order.confirmed" 3
create_topic "order.cancelled" 3
create_topic "inventory.reserved" 3
create_topic "inventory.rejected" 3
create_topic "inventory.released" 3
create_topic "payment.completed" 3
create_topic "payment.failed" 3
create_topic "payment.refunded" 1
create_topic "product.created" 1
create_topic "product.updated" 1
create_topic "product.deleted" 1

echo "All topics created."