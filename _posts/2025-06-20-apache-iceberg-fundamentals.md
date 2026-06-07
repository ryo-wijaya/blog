---
layout: post
title: "Apache Iceberg Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Apache Iceberg. Covers core concepts, catalog types, Hadoop and REST catalog setup, Spark integration, reading and writing, time travel, schema evolution, and partitioning.
author: ryo
date: 2025-06-20 23:10:20 +0800
categories: [Software Engineering]
tags: [iceberg, spark, data, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. What Is Apache Iceberg

Apache Iceberg is an open **table format** for large analytic datasets on distributed storage (S3, HDFS, GCS). It sits on top of your storage layer and gives it table-like behaviour.

**What it provides on top of raw files:**
- ACID transactions on object storage
- Schema evolution (add, rename, drop columns safely)
- Partition evolution (change partitioning without rewriting data)
- Time travel and rollback (query historical snapshots)
- Hidden partitioning (queries don't need partition predicates)
- Consistent reads and writes even with concurrent writers
- Full table statistics for query planning

---

## 2. Core Concepts

The Iceberg metadata hierarchy: each write creates a new snapshot, tracked by manifest lists and manifest files that record the actual data files with their statistics.

```
Table
 |
 +-- Metadata file (JSON)         <- current table state
      |
      +-- Snapshot                <- each write creates a new snapshot
           |
           +-- Manifest list      <- lists all manifest files in this snapshot
                |
                +-- Manifest file <- lists data files + their stats (min/max, null counts)
                     |
                     +-- Data files (Parquet, ORC, Avro)
```

| Concept | Description |
|---|---|
| **Snapshot** | Point-in-time state of a table after a write. Each commit creates a new snapshot. |
| **Manifest file** | A file tracking a subset of data files with their stats. |
| **Manifest list** | An index of all manifest files for a snapshot. |
| **Metadata file** | JSON file tracking the current and historical snapshots, schema, and partition spec. |
| **Catalog** | Tracks where each table's current metadata file lives. |

---

## 3. Catalog Types

A catalog stores the mapping from table name to the current metadata file location. Without a catalog, Iceberg can't find your tables.

| Catalog | Backend | Notes |
|---|---|---|
| **Hive Metastore** | Hive Metastore (HMS) | Traditional. Requires HMS running. Common in Hadoop/Hive environments. |
| **REST Catalog** | Any HTTP server implementing the Iceberg REST spec | Cloud-native, decoupled. Works with Polaris, Nessie, or custom servers. |
| **Hadoop Catalog** | Filesystem (HDFS, S3, local) | Simplest. Stores catalog info in the filesystem itself. Good for dev/testing. |
| **AWS Glue** | AWS Glue Data Catalog | Managed, AWS-native. Replaces HMS on AWS. |
| **JDBC Catalog** | Any JDBC database (Postgres, MySQL) | Stores metadata in a relational DB. Good for small deployments. |
| **Nessie** | Git-like catalog (Project Nessie) | Supports branching, tagging, and merging of table changes. |

---

## 4. Hadoop Catalog

The simplest catalog - stores table metadata directly in the filesystem. Good for local development, HDFS, or S3.

### 4.1. Maven Dependency

```xml
<dependency>
    <groupId>org.apache.iceberg</groupId>
    <artifactId>iceberg-spark-runtime-3.5_2.12</artifactId>
    <version>1.5.2</version>
</dependency>
```

### 4.2. Spark Configuration

Register the Hadoop catalog in SparkSession config by setting the catalog class, type, and warehouse path.

```java
SparkSession spark = SparkSession.builder()
    .appName("IcebergHadoop")
    .master("local[*]")
    // Register a catalog named "hadoop_catalog" using the Hadoop catalog type
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.hadoop_catalog", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.hadoop_catalog.type", "hadoop")
    .config("spark.sql.catalog.hadoop_catalog.warehouse", "hdfs:///iceberg/warehouse")
    // For local/S3:
    // .config("spark.sql.catalog.hadoop_catalog.warehouse", "s3://my-bucket/iceberg/")
    .getOrCreate();
```

### 4.3. Create and Use

Create a namespace and table using SQL, then write and query.

```sql
-- Create a namespace (database)
CREATE NAMESPACE IF NOT EXISTS hadoop_catalog.my_db;

-- Create a table
CREATE TABLE hadoop_catalog.my_db.users (
    id     BIGINT,
    name   STRING,
    email  STRING,
    signup DATE
) USING iceberg
PARTITIONED BY (months(signup));

-- Write
INSERT INTO hadoop_catalog.my_db.users VALUES (1, 'Ryo', 'ryo@example.com', DATE '2024-01-15');

-- Read
SELECT * FROM hadoop_catalog.my_db.users WHERE signup > '2024-01-01';
```

---

## 5. REST Catalog

The REST catalog communicates with an HTTP server that implements the Iceberg REST Catalog API. The server manages table metadata centrally.

Common REST catalog servers:
- **Apache Polaris** (incubating) - open source, Snowflake-donated
- **Project Nessie** - adds Git-like branching on top of the REST API
- **Gravitino** - open source, Apache incubating
- Lakeformation, Tabular (hosted)

### 5.1. Spark Configuration

Register the REST catalog and point it at the REST server URI. Credentials and warehouse path are optional depending on the server.

```java
SparkSession spark = SparkSession.builder()
    .appName("IcebergREST")
    .master("local[*]")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    // Register a catalog named "rest_catalog"
    .config("spark.sql.catalog.rest_catalog", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.rest_catalog.type", "rest")
    .config("spark.sql.catalog.rest_catalog.uri", "http://iceberg-rest-server:8181")
    // Optional auth
    .config("spark.sql.catalog.rest_catalog.credential", "client_id:client_secret")
    .config("spark.sql.catalog.rest_catalog.warehouse", "s3://my-bucket/warehouse")
    .getOrCreate();
```

---

## 6. Using Both Catalogs Together

You can register multiple catalogs in the same Spark session under different names. Reference tables with the fully-qualified name `<catalog>.<namespace>.<table>`.

```java
SparkSession spark = SparkSession.builder()
    .appName("MultiCatalog")
    .master("local[*]")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

    // Hadoop catalog - for raw/staging data
    .config("spark.sql.catalog.raw", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.raw.type", "hadoop")
    .config("spark.sql.catalog.raw.warehouse", "hdfs:///warehouse/raw")

    // REST catalog - for curated/production data
    .config("spark.sql.catalog.prod", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.prod.type", "rest")
    .config("spark.sql.catalog.prod.uri", "http://catalog-server:8181")
    .config("spark.sql.catalog.prod.warehouse", "s3://prod-bucket/warehouse")

    .getOrCreate();
```

```sql
-- Read from Hadoop catalog (raw), write to REST catalog (prod)
INSERT INTO prod.analytics.daily_summary
SELECT date, count(*) AS events
FROM raw.events.clickstream
WHERE date = current_date()
GROUP BY date;
```

---

## 7. Spark + Iceberg: Reading & Writing

### 7.1. DataFrame Write

Use `writeTo()` for Iceberg-specific write semantics including per-partition dynamic overwrite.

```java
// Append
df.writeTo("hadoop_catalog.my_db.users").append();

// Overwrite matching partitions (dynamic overwrite)
df.writeTo("hadoop_catalog.my_db.users").overwritePartitions();

// Overwrite entire table
df.writeTo("hadoop_catalog.my_db.users").overwrite(lit(true));

// Create table from DataFrame (infers schema and writes in one step)
df.writeTo("hadoop_catalog.my_db.new_table")
  .partitionedBy(months(col("signup")))
  .create();
```

### 7.2. DataFrame Read

Read an Iceberg table via `spark.table()` with the fully-qualified name or via the `iceberg` format in the read API.

```java
Dataset<Row> df = spark.table("hadoop_catalog.my_db.users");

// Or via read API
Dataset<Row> df = spark.read()
    .format("iceberg")
    .load("hadoop_catalog.my_db.users");
```

### 7.3. SQL DML

Iceberg supports MERGE (upsert), UPDATE, and DELETE as first-class SQL DML statements.

```sql
-- Merge (upsert)
MERGE INTO prod.db.users t
USING updates s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.email = s.email
WHEN NOT MATCHED THEN INSERT *;

-- Update
UPDATE prod.db.users SET email = 'new@example.com' WHERE id = 1;

-- Delete
DELETE FROM prod.db.users WHERE signup < '2020-01-01';
```

---

## 8. Time Travel

Every write creates a new snapshot. You can query any historical snapshot.

```sql
-- By snapshot ID
SELECT * FROM hadoop_catalog.my_db.users
VERSION AS OF 123456789;

-- By timestamp
SELECT * FROM hadoop_catalog.my_db.users
TIMESTAMP AS OF '2024-01-15 10:00:00';
```

```java
// In DataFrame API
Dataset<Row> historical = spark.read()
    .format("iceberg")
    .option("snapshot-id", "123456789")
    .load("hadoop_catalog.my_db.users");

Dataset<Row> asOf = spark.read()
    .format("iceberg")
    .option("as-of-timestamp", "1705312800000")   // epoch ms
    .load("hadoop_catalog.my_db.users");
```

### 8.1. Snapshot Management

Iceberg exposes metadata tables (`.snapshots`, `.files`, `.history`) and stored procedures (`CALL`) for rollback and snapshot expiry.

```sql
-- List snapshots
SELECT * FROM hadoop_catalog.my_db.users.snapshots;

-- List data files
SELECT * FROM hadoop_catalog.my_db.users.files;

-- Show history
SELECT * FROM hadoop_catalog.my_db.users.history;

-- Rollback to a snapshot
CALL hadoop_catalog.system.rollback_to_snapshot('my_db.users', 123456789);

-- Expire old snapshots (frees storage)
CALL hadoop_catalog.system.expire_snapshots('my_db.users', TIMESTAMP '2024-01-01 00:00:00');
```

---

## 9. Schema Evolution

Schema changes in Iceberg are metadata-only operations - no data rewrite required.

```sql
-- Add a column
ALTER TABLE hadoop_catalog.my_db.users ADD COLUMN phone STRING;

-- Rename a column
ALTER TABLE hadoop_catalog.my_db.users RENAME COLUMN phone TO phone_number;

-- Drop a column
ALTER TABLE hadoop_catalog.my_db.users DROP COLUMN phone_number;

-- Change type (supported widening: int->long, float->double, decimal precision increase)
ALTER TABLE hadoop_catalog.my_db.users ALTER COLUMN age TYPE BIGINT;

-- Add a nested field
ALTER TABLE hadoop_catalog.my_db.users ADD COLUMN address STRUCT<city: STRING, country: STRING>;
```

Old data files are not rewritten. Iceberg uses column IDs (not names) internally, so renaming a column does not break existing files.

---

## 10. Partitioning

### 10.1. Partition Transforms

Iceberg supports **hidden partitioning** - queries do not need to include partition predicates; the engine prunes automatically.

| Transform | Example | Use case |
|---|---|---|
| `identity(col)` | `PARTITIONED BY (country)` | Low-cardinality columns |
| `years(col)` | `PARTITIONED BY (years(signup))` | Date/timestamp columns by year |
| `months(col)` | `PARTITIONED BY (months(signup))` | Date/timestamp by month |
| `days(col)` | `PARTITIONED BY (days(signup))` | Date/timestamp by day |
| `hours(col)` | `PARTITIONED BY (hours(event_time))` | Timestamp by hour |
| `bucket(n, col)` | `PARTITIONED BY (bucket(16, user_id))` | High-cardinality columns |
| `truncate(n, col)` | `PARTITIONED BY (truncate(4, zip_code))` | String prefix bucketing |

### 10.2. Partition Evolution

Change partitioning without rewriting existing data:

```sql
-- Old partitioning was by years - evolve to months for finer granularity
ALTER TABLE hadoop_catalog.my_db.events
REPLACE PARTITION FIELD years(event_time) WITH months(event_time);
```

Existing files keep their old partitioning. New writes use the new spec. The query engine handles both transparently.

### 10.3. Example: Create Table with Partitioning

Full CREATE TABLE combining bucket and day partitioning.

```sql
CREATE TABLE hadoop_catalog.my_db.events (
    event_id  BIGINT,
    user_id   BIGINT,
    event     STRING,
    ts        TIMESTAMP
) USING iceberg
PARTITIONED BY (bucket(16, user_id), days(ts));
```
