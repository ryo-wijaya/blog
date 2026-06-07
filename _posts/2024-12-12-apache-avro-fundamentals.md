---
layout: post
title: "Apache Avro Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Apache Avro. Covers schema design, type system, doc fields, JSON-to-Avro conversion, schema evolution, Java serialization, Confluent Schema Registry integration, compatibility modes, and Spark Avro.
author: ryo
date: 2024-12-12 01:04:29 +0800
categories: [Software Engineering]
tags: [data, avro, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. What Is Avro

Apache Avro is a binary serialization format that requires a schema to read or write data. The schema is always present, either embedded in the file or looked up from a registry.

| | Avro | JSON | Protobuf | Parquet |
|---|---|---|---|---|
| Format | Binary | Text | Binary | Binary columnar |
| Schema required | yes | no | yes (`.proto`) | yes (embedded) |
| Schema evolution | yes (built-in) | n/a | yes | limited |
| Row vs columnar | Row | Row | Row | Columnar |
| Kafka use | yes (primary) | yes | yes | no (file format) |
| Readable without schema | no | yes | no | no |
| Self-describing files | yes (`.avro` embeds schema) | yes | no | yes |

---

## 2. Schema Design

Avro schemas are written in JSON. A schema describes a single type.

### 2.1. Primitive Types

| Type | Java equivalent | Notes |
|---|---|---|
| `"null"` | `null` | Only value is `null` |
| `"boolean"` | `boolean` | |
| `"int"` | `int` | 32-bit signed |
| `"long"` | `long` | 64-bit signed |
| `"float"` | `float` | 32-bit IEEE 754 |
| `"double"` | `double` | 64-bit IEEE 754 |
| `"bytes"` | `ByteBuffer` | Sequence of 8-bit bytes |
| `"string"` | `String` | Unicode char sequence |

### 2.2. Record

The most common top-level type. Every field has a name and type.

```json
{
  "type": "record",
  "name": "User",
  "namespace": "com.example.events",
  "doc": "Represents a registered user.",
  "fields": [
    {
      "name": "id",
      "type": "long",
      "doc": "Unique user identifier."
    },
    {
      "name": "name",
      "type": "string",
      "doc": "Full display name of the user."
    },
    {
      "name": "email",
      "type": ["null", "string"],
      "default": null,
      "doc": "Email address. Null if not provided."
    },
    {
      "name": "role",
      "type": {
        "type": "enum",
        "name": "UserRole",
        "symbols": ["ADMIN", "USER", "GUEST"],
        "doc": "Access role of the user."
      },
      "default": "USER"
    },
    {
      "name": "tags",
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": [],
      "doc": "Free-form tags associated with the user."
    },
    {
      "name": "metadata",
      "type": {
        "type": "map",
        "values": "string"
      },
      "default": {},
      "doc": "Key-value metadata pairs."
    },
    {
      "name": "address",
      "type": {
        "type": "record",
        "name": "Address",
        "fields": [
          {"name": "city", "type": "string"},
          {"name": "country", "type": "string"}
        ]
      },
      "doc": "Physical address of the user."
    }
  ]
}
```

### 2.3. Union (Nullable Fields)

Unions are expressed as a JSON array of types. The first type in the union is the default type.

```json
"type": ["null", "string"]   // nullable string - default must be null
"type": ["null", "long"]     // nullable long
"type": ["string", "int"]    // string or int - default is string
```

**Convention:** Always put `"null"` first for nullable fields so you can set `"default": null`.

### 2.4. Logical Types

Built on top of primitives - add semantic meaning:

```json
{"type": "long",  "logicalType": "timestamp-millis"}   // epoch ms
{"type": "long",  "logicalType": "timestamp-micros"}   // epoch us
{"type": "int",   "logicalType": "date"}               // days since epoch
{"type": "int",   "logicalType": "time-millis"}        // ms since midnight
{"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}  // BigDecimal
{"type": "string","logicalType": "uuid"}
```

### 2.5. `doc` Fields

Every schema, record, and field can have a `"doc"` string. It is stored in the schema but ignored during serialization. Use it to document business meaning.

```json
{
  "type": "record",
  "name": "OrderEvent",
  "doc": "Emitted whenever an order transitions to a new status. Consumed by the billing and fulfillment services.",
  "fields": [
    {
      "name": "orderId",
      "type": "string",
      "doc": "UUID of the order. Maps to orders.id in the orders database."
    },
    {
      "name": "totalAmountCents",
      "type": "long",
      "doc": "Total order value in cents (USD). Divide by 100 for display."
    }
  ]
}
```

`doc` fields are particularly useful for data catalog tools like **Collibra** or **DataHub**: you can export Avro schemas and import the `doc` strings as business glossary descriptions, data lineage annotations, or data dictionary entries. This makes Avro the source of truth for both technical schema and business metadata.

---

## 3. JSON to Avro Schema Conversion

Common patterns when converting a JSON payload to an Avro schema:

| JSON | Avro |
|---|---|
| `"name": "Ryo"` (string) | `{"name": "name", "type": "string"}` |
| `"age": 25` (integer) | `{"name": "age", "type": "int"}` |
| `"price": 9.99` (float) | `{"name": "price", "type": "double"}` |
| `"active": true` (boolean) | `{"name": "active", "type": "boolean"}` |
| `"note": null` or sometimes null | `{"name": "note", "type": ["null", "string"], "default": null}` |
| `"tags": ["a", "b"]` (array) | `{"name": "tags", "type": {"type": "array", "items": "string"}, "default": []}` |
| `"meta": {"k": "v"}` (object) | `{"name": "meta", "type": {"type": "map", "values": "string"}, "default": {}}` |
| Nested object | Nested `"type": "record"` |
| Enum-like string field | `{"type": "enum", "symbols": [...]}` if values are fixed |
| Monetary value | `"long"` (store as cents) or `"bytes"` with `decimal` logicalType |
| Timestamp | `"long"` with `timestamp-millis` logicalType |
| UUID | `"string"` with `uuid` logicalType |

**Example:**

```json
// JSON payload
{
  "userId": "abc-123",
  "amount": 49.99,
  "currency": "USD",
  "createdAt": "2024-01-15T10:30:00Z",
  "tags": ["premium", "promo"],
  "refundReason": null
}
```

```json
// Avro schema
{
  "type": "record",
  "name": "PaymentEvent",
  "namespace": "com.example.payments",
  "fields": [
    {"name": "userId",       "type": "string"},
    {"name": "amountCents",  "type": "long",   "doc": "Amount in cents. Original JSON had float 'amount'."},
    {"name": "currency",     "type": "string"},
    {"name": "createdAt",    "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "tags",         "type": {"type": "array", "items": "string"}, "default": []},
    {"name": "refundReason", "type": ["null", "string"], "default": null}
  ]
}
```

---

## 4. Schema Evolution

Avro supports schema evolution - the schema used to write data (writer schema) and the schema used to read it (reader schema) can differ.

### 4.1. What Is and Isn't Allowed

**Safe changes (backward compatible - new schema can read old data):**
- Add a field with a default value
- Remove a field that had a default value
- Change a field type to a wider type (`int` -> `long`, `float` -> `double`)

**Forward compatible (old schema can read new data):**
- Add a field that the old reader can ignore (old reader skips unknown fields)
- Remove a field - old reader uses its default for the missing field

**Breaking changes (avoid):**
- Add a field without a default (old data has no value for it)
- Remove a field that had no default (reader can't fill in the missing value)
- Rename a field without an alias
- Change a field to an incompatible type (`string` -> `int`)
- Change enum symbols

### 4.2. Aliases for Renames

Avro supports field aliases to handle renames without breaking compatibility:

```json
{
  "name": "fullName",
  "aliases": ["name"],   // previously called "name"
  "type": "string"
}
```

---

## 5. Java: `GenericRecord`

Use when you don't want to generate Java classes. Schema is loaded at runtime.

```xml
<dependency>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro</artifactId>
    <version>1.11.3</version>
</dependency>
```

```java
// Parse schema
Schema schema = new Schema.Parser().parse(new File("user.avsc"));

// Write
GenericRecord user = new GenericData.Record(schema);
user.put("id", 1L);
user.put("name", "Ryo");
user.put("email", null);

// Serialize to bytes
ByteArrayOutputStream out = new ByteArrayOutputStream();
DatumWriter<GenericRecord> writer = new GenericDatumWriter<>(schema);
Encoder encoder = EncoderFactory.get().binaryEncoder(out, null);
writer.write(user, encoder);
encoder.flush();
byte[] bytes = out.toByteArray();

// Deserialize from bytes
DatumReader<GenericRecord> reader = new GenericDatumReader<>(schema);
Decoder decoder = DecoderFactory.get().binaryDecoder(bytes, null);
GenericRecord deserialized = reader.read(null, decoder);
System.out.println(deserialized.get("name"));  // "Ryo"

// Write to .avro file (includes schema in file header)
DataFileWriter<GenericRecord> fileWriter = new DataFileWriter<>(writer);
fileWriter.create(schema, new File("users.avro"));
fileWriter.append(user);
fileWriter.close();

// Read .avro file
DataFileReader<GenericRecord> fileReader =
    new DataFileReader<>(new File("users.avro"), new GenericDatumReader<>());
for (GenericRecord r : fileReader) {
    System.out.println(r);
}
```

---

## 6. Java: `SpecificRecord` (Code Generation)

Generate Java classes from `.avsc` schema files using the Avro Maven plugin. The generated class implements `SpecificRecord` and has typed getters/setters.

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.apache.avro</groupId>
    <artifactId>avro-maven-plugin</artifactId>
    <version>1.11.3</version>
    <executions>
        <execution>
            <phase>generate-sources</phase>
            <goals><goal>schema</goal></goals>
            <configuration>
                <sourceDirectory>${project.basedir}/src/main/avro</sourceDirectory>
                <outputDirectory>${project.build.directory}/generated-sources/avro</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

Place schema files in `src/main/avro/`. Run `mvn generate-sources` - the plugin generates a Java class per record.

```java
// Generated class: com.example.events.User
User user = User.newBuilder()
    .setId(1L)
    .setName("Ryo")
    .setEmail(null)
    .setRole(UserRole.USER)
    .setTags(List.of("premium"))
    .setMetadata(Map.of("source", "web"))
    .build();

// Serialize
DatumWriter<User> writer = new SpecificDatumWriter<>(User.class);
// ... same encode/decode pattern as GenericRecord
```

`SpecificRecord` is preferred for production code - compile-time type safety and IDE support. `GenericRecord` is useful for generic ETL tools or when the schema is not known at compile time.

---

## 7. Avro with Confluent Schema Registry

Add the Confluent Avro serializer dependency, then point producers and consumers at the Schema Registry URL. The serializer handles schema registration and the 5-byte wire format header automatically.

```xml
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.6.0</version>
</dependency>
```

```java
// Producer
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
props.put("schema.registry.url", "http://schema-registry:8081");
// Optional: auto-register schema on first produce
props.put("auto.register.schemas", true);

KafkaProducer<String, User> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("users", "key1", userSpecificRecord));

// Consumer
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class);
props.put("schema.registry.url", "http://schema-registry:8081");
props.put("specific.avro.reader", true);   // return SpecificRecord instead of GenericRecord

KafkaConsumer<String, User> consumer = new KafkaConsumer<>(props);
```

The serializer automatically:
1. Registers the schema with Schema Registry (if `auto.register.schemas=true`)
2. Prepends the 5-byte magic header (0x00 + schema ID) to each message

The deserializer automatically:
1. Reads the schema ID from the message header
2. Fetches the writer schema from Schema Registry
3. Resolves writer schema vs reader schema for evolution

---

## 8. Schema Registry REST API

The Schema Registry exposes a REST API for registering schemas, checking compatibility, and managing subjects.

```bash
REGISTRY=http://schema-registry:8081

# List all subjects
curl $REGISTRY/subjects

# Register a schema
curl -X POST $REGISTRY/subjects/users-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{\"type\":\"record\",\"name\":\"User\",\"fields\":[{\"name\":\"id\",\"type\":\"long\"},{\"name\":\"name\",\"type\":\"string\"}]}"}'
# Returns: {"id": 1}

# Get latest schema for a subject
curl $REGISTRY/subjects/users-value/versions/latest

# Get schema by global ID
curl $REGISTRY/schemas/ids/1

# Check compatibility before registering
curl -X POST $REGISTRY/compatibility/subjects/users-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'
# Returns: {"is_compatible": true}

# Update compatibility mode for a subject
curl -X PUT $REGISTRY/config/users-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility": "FULL"}'

# Get global default compatibility mode
curl $REGISTRY/config

# Delete a subject (all versions)
curl -X DELETE $REGISTRY/subjects/users-value
```

---

## 9. Avro with Spark

Add `spark-avro` as a dependency to read and write `.avro` files or use Avro serialization in Spark Structured Streaming.

```xml
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-avro_2.12</artifactId>
    <version>3.5.0</version>
</dependency>
```

```java
// Read .avro files
Dataset<Row> df = spark.read()
    .format("avro")
    .load("hdfs:///data/users/*.avro");

// Write .avro files
df.write()
    .format("avro")
    .mode("overwrite")
    .save("hdfs:///output/users/");

// Write with a specific schema (useful for evolution control)
df.write()
    .format("avro")
    .option("avroSchema", schemaJson)   // JSON string of the Avro schema
    .save("hdfs:///output/users/");
```

### 9.1. `from_avro` / `to_avro` for Kafka + Spark Streaming

`from_avro` deserializes a binary Avro column into a struct; `to_avro` does the reverse. Pass the schema as a JSON string, or use the Confluent variant with a registry URL.

```java
import org.apache.spark.sql.avro.functions.*;

// Kafka message value is raw Avro bytes (with Schema Registry 5-byte header stripped)
String userSchemaJson = new String(Files.readAllBytes(Path.of("user.avsc")));

Dataset<Row> parsed = kafkaStream
    .select(from_avro(col("value"), userSchemaJson).as("user"))
    .select("user.*");

// Serialize back to Avro bytes for writing to Kafka
Dataset<Row> serialized = df
    .select(to_avro(struct(col("id"), col("name"))).as("value"));
```

For Schema Registry integration with Spark Streaming, use the Confluent `from_avro`/`to_avro` variant that accepts a registry URL and subject instead of an inline schema string:

```java
// Confluent's spark-avro with Schema Registry support
import io.confluent.spark.sql.SchemaRegistryAvroData;

Map<String, String> opts = Map.of(
    "schema.registry.url", "http://schema-registry:8081",
    "subject", "users-value"
);
Dataset<Row> parsed = kafkaStream
    .select(from_avro(col("value"), "users-value", opts).as("user"))
    .select("user.*");
```

---

## 10. Data Catalogs & Collibra

`doc` fields in Avro schemas serve as the primary place to embed business metadata alongside technical schema definitions.

A typical workflow for integration with a data catalog like Collibra or DataHub:

1. Engineers define Avro schemas with detailed `doc` fields (field descriptions, business terms, data owner, PII flags)
2. A CI job runs on schema changes and exports the schemas from Schema Registry via the REST API
3. The exported schemas are parsed and the `doc` strings are pushed to the catalog's API as business attribute descriptions or glossary mappings
4. The catalog links the technical schema (from Avro) to the business glossary (curated in Collibra)

This makes the Avro schema the **single source of truth** for both producers/consumers and the data governance layer, avoiding documentation drift.

**Example `doc` conventions to support this:**

```json
{
  "name": "customerId",
  "type": "string",
  "doc": "PII:true | Owner:CRM-team | GlossaryTerm:Customer.ID | Description: UUID of the customer as stored in the CRM system."
}
```
