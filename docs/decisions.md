# Architecture Decisions & Known Problems

## Day 12: Synchronous Order Flow (Phase 2)

We have implemented a synchronous checkout flow using HTTP calls. 
Here are the critical problems with this design that we will solve using Kafka and the Saga pattern in Phase 6.

### Problem 1: The Dual-Write Problem
**Scenario:** The Order service saves an order to the database, and then calls the Payment service. 
**The Flaw:** If the Order service successfully saves the order to the database, but then crashes *before* it can call the Payment service, the user is never charged, and the order is stuck in `PENDING` forever. There is no retry mechanism. 
**The Kafka Fix:** We will use the Transactional Outbox pattern. The order will be saved to an "outbox" table in the same database transaction. A separate relay process will read the outbox and publish the event to Kafka.

### Problem 2: Refund Failure on Cancellation
**Scenario:** A user places an order, the payment succeeds, and the order is `CONFIRMED`. The user then decides to cancel the order.
**The Flaw:** Our `cancel_order` function simply changes the order status to `CANCELLED`. It does not call the Payment service to issue a refund. The user loses their money.
**The Kafka Fix:** When an order is cancelled, the Order service will publish an `order.cancelled` event to Kafka. The Payment service will consume this event and automatically issue a refund.

### Problem 3: Cascading Failures
**Scenario:** The Payment service is slow or offline.
**The Flaw:** The Order service's HTTP call will time out. The order stays in `PENDING`, but there is no background retry. The user experiences a failure during checkout.
**The Kafka Fix:** The Order service will publish `order.created` to Kafka. The Payment service will consume it at its own pace. If the Payment service is down, the message stays safely in Kafka until it recovers.

### Problem 4: Inventory Not Released on Payment Failure
**Scenario:** The Product service reserves stock for an order. The Payment service then declines the card.
**The Flaw:** The Order service cancels the order, but the Product service's `reserved` count is never released. The stock is locked up forever.
**The Kafka Fix:** When the Payment service publishes a `payment.failed` event, the Product service will consume it and release the reserved stock.