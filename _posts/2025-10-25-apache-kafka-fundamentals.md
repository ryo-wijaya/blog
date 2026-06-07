---
layout: post
title: "Apache Kafka Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Apache Kafka. Covers brokers, topics, partitions, offsets, producers, consumers, consumer groups, Java client examples, Spring Boot Kafka, Confluent Platform, Schema Registry, and key tuning settings.
author: ryo
date: 2025-10-25 00:02:40 +0800
categories: [Software Engineering]
tags: [kafka, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Core Concepts

Kafka stores messages in ordered, append-only partitions. Each consumer group tracks its own position via per-partition offsets and reads independently of other groups.

```
Producer --> [Topic: orders]
              Partition 0: [msg0] [msg3] [msg6]  ...
              Partition 1: [msg1] [msg4] [msg7]  ...
              Partition 2: [msg2] [msg5] [msg8]  ...
                              ^
                         offset (position)
                              ^
             Consumer Group A reads from all partitions
```

| Concept | Description |
|---|---|
| **Broker** | A single Kafka server. A cluster has multiple brokers. |
| **Topic** | A named, ordered, append-only log. Messages are never deleted on consume. |
| **Partition** | A topic is split into N partitions for parallelism and scalability. |
| **Offset** | The position of a message within a partition. Monotonically increasing. |
| **Replication factor** | How many copies of each partition exist across brokers. |
| **Leader** | The broker handling reads/writes for a partition. |
| **ISR** | In-Sync Replicas - replicas that are caught up with the leader. |
| **KRaft** | Kafka's built-in consensus (replaces ZooKeeper from Kafka 3.3+). |

**Ordering guarantee:** Messages within a single partition are strictly ordered. There is no ordering guarantee across partitions.

---

## 2. Topic Configuration

Use `kafka-topics.sh` to create and inspect topics, and `kafka-configs.sh` to modify topic-level settings after creation.

```bash
# Create a topic
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic orders \
  --partitions 6 \
  --replication-factor 3

# Describe a topic
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders

# List topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Alter topic config
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name orders \
  --alter --add-config retention.ms=86400000
```

Key topic-level configs:

| Config | Default | Description |
|---|---|---|
| `retention.ms` | 7 days | How long messages are kept |
| `retention.bytes` | -1 (unlimited) | Max size per partition before old messages are dropped |
| `cleanup.policy` | `delete` | `delete` = expire by time/size; `compact` = keep latest value per key |
| `replication.factor` | set at creation | Number of replicas (should be >= 3 in production) |
| `min.insync.replicas` | 1 | Minimum ISR count for a produce to be acknowledged |
| `max.message.bytes` | 1MB | Maximum message size |
| `compression.type` | `producer` | Accept whatever the producer sent; or set `gzip`, `snappy`, `lz4`, `zstd` |

---

## 3. Producers

### 3.1. How Producers Work

1. Producer serialises key and value to bytes
2. Partitioner decides which partition to write to (default: hash of key, or round-robin if no key)
3. Message goes into an in-memory record accumulator (batch buffer)
4. Sender thread drains batches and sends to the leader broker
5. Broker acknowledges (based on `acks` setting)

### 3.2. Key Producer Configs

| Config | Default | Description |
|---|---|---|
| `acks` | `1` | `0` = no ack; `1` = leader ack only; `all` (`-1`) = all ISR must ack |
| `retries` | `2147483647` | Number of retries on transient failure |
| `enable.idempotence` | `true` (Kafka 3+) | Exactly-once delivery per partition; requires `acks=all` |
| `max.in.flight.requests.per.connection` | `5` | Set to `1` if ordering matters and idempotence is off |
| `batch.size` | 16KB | Max bytes per batch per partition |
| `linger.ms` | `0` | How long to wait for more messages before sending a batch |
| `compression.type` | `none` | Compress batches: `gzip`, `snappy`, `lz4`, `zstd` |
| `buffer.memory` | 32MB | Total memory for all buffered records |

**`linger.ms` vs throughput:** A small non-zero `linger.ms` (e.g. 5-20ms) allows batches to fill up, increasing throughput at the cost of a small latency increase.

---

## 4. Consumers & Consumer Groups

### 4.1. How Consumer Groups Work

- All consumers sharing the same `group.id` form a consumer group.
- Kafka assigns each partition to exactly one consumer in the group.
- If there are more consumers than partitions, some consumers are idle.
- If a consumer leaves or joins, a **rebalance** occurs and partitions are reassigned.

```
Topic: orders (6 partitions)

Consumer Group A (3 consumers):
  Consumer 1 -> Partition 0, 1
  Consumer 2 -> Partition 2, 3
  Consumer 3 -> Partition 4, 5

Consumer Group B (1 consumer):
  Consumer 1 -> Partition 0, 1, 2, 3, 4, 5   (all partitions)
```

### 4.2. Key Consumer Configs

| Config | Default | Description |
|---|---|---|
| `group.id` | (none) | Required. Identifies the consumer group. |
| `auto.offset.reset` | `latest` | Where to start if no committed offset: `latest` or `earliest` |
| `enable.auto.commit` | `true` | Auto-commit offsets every `auto.commit.interval.ms` |
| `auto.commit.interval.ms` | 5000 | How often to auto-commit |
| `max.poll.records` | 500 | Max records returned per `poll()` call |
| `session.timeout.ms` | 45000 | If broker hears nothing from consumer in this time, it's considered dead and rebalance triggers |
| `heartbeat.interval.ms` | 3000 | How often consumer sends heartbeat. Should be < 1/3 of `session.timeout.ms` |
| `fetch.min.bytes` | 1 | Min data to fetch before returning. Increase for throughput. |
| `fetch.max.wait.ms` | 500 | Max wait if `fetch.min.bytes` not met |

---

## 5. Offsets

Offsets track how far a consumer group has read in each partition. Stored in the internal `__consumer_offsets` topic.

### 5.1. Delivery Semantics

| Semantic | How | Risk |
|---|---|---|
| **At-most-once** | Commit offset before processing | Message lost if consumer crashes before processing |
| **At-least-once** | Commit offset after processing (default approach) | Message processed again if consumer crashes after processing but before commit |
| **Exactly-once** | Transactional producer + idempotent consumer | Requires Kafka transactions or idempotent consumers |

### 5.2. Auto vs Manual Commit

Auto-commit is convenient but risks at-most-once delivery on crash. Manual commit gives you control over exactly when offsets are persisted.

```java
// Auto commit - simplest, risk of at-most-once on crash
props.put("enable.auto.commit", "true");
props.put("auto.commit.interval.ms", "1000");

// Manual commit - gives full control
props.put("enable.auto.commit", "false");
// After processing:
consumer.commitSync();                  // block until committed
consumer.commitAsync((offsets, ex) -> { // non-blocking
    if (ex != null) log.error("commit failed", ex);
});
```

### 5.3. Kafka CLI - Consumer Groups

Use `kafka-consumer-groups.sh` to inspect per-partition lag and reset offsets when needed.

```bash
# List all consumer groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe group - shows lag per partition
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-group

# Reset offsets to earliest (requires group to be inactive)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group --topic orders \
  --reset-offsets --to-earliest --execute

# Reset to specific offset
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group --topic orders \
  --reset-offsets --to-offset 1000 --execute
```

---

## 6. Kafka CLI - Produce & Consume

The console producer and consumer are useful for manual testing and debugging topics without writing any code.

```bash
# Produce messages (console)
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders
# Type messages, one per line. Ctrl+C to stop.

# Produce with key
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic orders \
  --property key.separator=: \
  --property parse.key=true
# Input: mykey:myvalue

# Consume from beginning
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --from-beginning

# Consume with key/value display
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders \
  --property print.key=true \
  --property key.separator=:

# Consume as part of a group
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --group my-group
```

---

## 7. Java Producer (Vanilla)

Add the Kafka client dependency, then configure a `KafkaProducer` with serializers and reliability settings.

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.7.0</version>
</dependency>
```

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {

    // Fire and forget
    producer.send(new ProducerRecord<>("orders", "key1", "value1"));

    // With callback (async - runs in background thread when ack received)
    ProducerRecord<String, String> record = new ProducerRecord<>("orders", "key2", "value2");
    producer.send(record, (metadata, exception) -> {
        if (exception != null) {
            System.err.println("Send failed: " + exception.getMessage());
        } else {
            System.out.printf("Sent to %s partition %d offset %d%n",
                metadata.topic(), metadata.partition(), metadata.offset());
        }
    });

    // Synchronous send (blocks until ack)
    RecordMetadata meta = producer.send(record).get();

    producer.flush(); // ensure all buffered records are sent
}
```

---

## 8. Java Consumer (Vanilla)

Subscribe to topics with a `KafkaConsumer`, poll in a loop, and commit offsets manually for at-least-once processing.

```java
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

try (KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props)) {
    consumer.subscribe(List.of("orders"));

    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

        for (ConsumerRecord<String, String> record : records) {
            System.out.printf("topic=%s partition=%d offset=%d key=%s value=%s%n",
                record.topic(), record.partition(), record.offset(),
                record.key(), record.value());

            process(record);
        }

        // Commit after processing the whole batch
        consumer.commitSync();
    }
}
```

---

## 9. Spring Boot Kafka

Add `spring-kafka`, then configure brokers, serializers, and consumer group in `application.yml`.

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
    consumer:
      group-id: my-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      auto-offset-reset: earliest
      enable-auto-commit: false
    listener:
      ack-mode: MANUAL_IMMEDIATE   # commit manually after each record
```

### 9.1. Producer with `KafkaTemplate`

`KafkaTemplate` wraps the Kafka producer and returns a `CompletableFuture` for attaching completion callbacks.

```java
@Service
@RequiredArgsConstructor
public class OrderProducerService {

    private final KafkaTemplate<String, String> kafkaTemplate;

    public void sendOrder(String orderId, String orderJson) {
        kafkaTemplate.send("orders", orderId, orderJson)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to send order {}", orderId, ex);
                } else {
                    log.info("Sent order {} to partition {}",
                        orderId, result.getRecordMetadata().partition());
                }
            });
    }
}
```

### 9.2. Consumer with `@KafkaListener`

`@KafkaListener` methods are invoked per record (or batch). Inject `Acknowledgment` to commit offsets only after successful processing.

```java
@Component
@Slf4j
public class OrderConsumer {

    @KafkaListener(topics = "orders", groupId = "my-group")
    public void consume(ConsumerRecord<String, String> record, Acknowledgment ack) {
        log.info("Received: key={} value={} offset={}",
            record.key(), record.value(), record.offset());

        try {
            processOrder(record.value());
            ack.acknowledge();   // commit offset only after successful processing
        } catch (Exception e) {
            log.error("Processing failed, not committing offset", e);
            // record will be re-delivered
        }
    }

    // Listen to multiple topics
    @KafkaListener(topics = {"orders", "returns"}, groupId = "my-group")
    public void consumeMultiple(String message) { ... }

    // Listen to a specific partition
    @KafkaListener(topicPartitions = @TopicPartition(
        topic = "orders", partitions = {"0", "1"}))
    public void consumePartitions(String message) { ... }
}
```

### 9.3. Dead Letter Topic (DLT)

When a message keeps failing, send it to a DLT for later inspection instead of blocking the consumer.

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
        ConsumerFactory<String, String> consumerFactory,
        KafkaTemplate<String, String> kafkaTemplate) {

    var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
    factory.setConsumerFactory(consumerFactory);

    // Retry 3 times, then send to <topic>.DLT
    factory.setCommonErrorHandler(new DefaultErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate),
        new FixedBackOff(1000L, 3L)   // 1s interval, 3 retries
    ));
    return factory;
}
```

Or with `@RetryableTopic` (simpler annotation-based approach):

```java
@RetryableTopic(
    attempts = "4",                     // 1 original + 3 retries
    backoff = @Backoff(delay = 1000),
    dltTopicSuffix = ".DLT"
)
@KafkaListener(topics = "orders")
public void consume(String message) {
    process(message);   // if this throws, message is retried then sent to orders.DLT
}
```

---

## 10. Confluent Platform

Confluent is a commercial distribution of Kafka that adds:

| Feature | Description |
|---|---|
| **Confluent Cloud** | Fully managed Kafka-as-a-service |
| **Schema Registry** | Central registry for Avro/JSON/Protobuf schemas (also open-source) |
| **ksqlDB** | SQL-like streaming queries over Kafka topics |
| **Kafka Connect** | Framework for moving data between Kafka and external systems (DBs, object storage, APIs) |
| **Control Center** | GUI for monitoring clusters, topics, consumer lag, connectors |
| **RBAC** | Role-based access control at topic/cluster level |
| **Tiered Storage** | Offload old log segments to object storage (S3, GCS) |
| **Cluster Linking** | Replicate topics across clusters with automatic offset translation |

### 10.1. Confluent CLI

The Confluent CLI connects to Confluent Cloud to manage environments, clusters, and topics.

```bash
confluent login
confluent environment list
confluent kafka cluster list
confluent kafka topic list --cluster <id>
confluent kafka topic produce orders --cluster <id>
confluent kafka topic consume orders --from-beginning --cluster <id>
```

---

## 11. Schema Registry (Overview)

Schema Registry stores and versions schemas for Kafka messages. Producers register a schema; consumers fetch it by ID embedded in the message.

**Message wire format with Schema Registry:**

```
[magic byte: 0x00] [schema ID: 4 bytes] [serialized payload]
```

**Subject naming strategies:**

| Strategy | Subject name | Description |
|---|---|---|
| `TopicNameStrategy` (default) | `<topic>-key` / `<topic>-value` | One schema per topic per key/value |
| `RecordNameStrategy` | `<fully-qualified-record-name>` | Schema tied to the record type, not the topic |
| `TopicRecordNameStrategy` | `<topic>-<record-name>` | Combination of both |

**Compatibility modes:**

| Mode | Meaning |
|---|---|
| `BACKWARD` (default) | New schema can read data written by the previous schema |
| `FORWARD` | Previous schema can read data written by the new schema |
| `FULL` | Both backward and forward compatible |
| `NONE` | No compatibility check |
| `BACKWARD_TRANSITIVE` | Compatible with all previous versions (not just the last) |

See the Avro cheatsheet for full schema design and serialization details.

---

## 12. Transactions & Exactly-Once

Transactional producers wrap sends in atomic transactions. On the consumer side, set `isolation.level=read_committed` to skip uncommitted messages.

```java
// Transactional producer - exactly-once to Kafka
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-transactional-id");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("output-topic", key, value));
    producer.commitTransaction();
} catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException e) {
    producer.close();   // fatal - cannot recover
} catch (KafkaException e) {
    producer.abortTransaction();
}

// Consumer side: only read committed messages
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

Exactly-once semantics (EOS) is most useful in Kafka Streams or consumer-transform-produce pipelines. For consume-then-write-to-DB, you need idempotent DB writes or optimistic locking on the consumer side.

---

## 13. Key Metrics & Tuning

**Producer metrics to watch:**

| Metric | What it means |
|---|---|
| `record-send-rate` | Records sent per second |
| `request-latency-avg` | Average time from send to ack |
| `record-error-rate` | Failed sends (should be 0) |
| `batch-size-avg` | Average batch size - low means batching is not effective |

**Consumer metrics to watch:**

| Metric | What it means |
|---|---|
| `records-lag-max` | Max consumer lag across partitions - key health indicator |
| `fetch-rate` | Fetch requests per second |
| `commit-rate` | Offset commits per second |

**Broker metrics to watch:**

| Metric | What it means |
|---|---|
| `UnderReplicatedPartitions` | Partitions where ISR < replication factor - indicates broker issues |
| `ActiveControllerCount` | Should always be 1 |
| `OfflinePartitionsCount` | Partitions with no leader - critical alert |
| `BytesInPerSec` / `BytesOutPerSec` | Network throughput |

**Common tuning:**

- Increase `num.partitions` for higher throughput (more parallel consumers).
- Set `min.insync.replicas = replication.factor - 1` (e.g. 2 for RF=3) to tolerate one broker failure without rejecting writes.
- Increase `batch.size` and `linger.ms` on producers for higher throughput.
- Increase `fetch.min.bytes` on consumers to reduce fetch frequency.
- Use `compression.type=lz4` or `zstd` for good compression speed/ratio balance.
