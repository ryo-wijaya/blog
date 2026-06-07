---
layout: post
title: "Apache Spark (Java) Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Apache Spark with Java. Covers SparkSession, RDDs, DataFrames, Datasets, transformations, Spark SQL, reading/writing data, partitioning, caching, UDFs, tuning, and structured streaming.
author: ryo
date: 2026-01-25 10:20:04 +0800
categories: [Software Engineering]
tags: [spark, java, data, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Architecture Overview

```
+--------------------+
|   Driver Program   |  - runs main(), creates SparkContext/SparkSession
|  (your app code)   |  - builds the DAG of transformations
+--------------------+
         |
   Cluster Manager     (standalone / YARN / Kubernetes / Mesos)
         |
  +------+------+
  |             |
Executor      Executor  - JVM processes on worker nodes
(tasks/cache) (tasks/cache)
```

Key concepts:

| Term | Meaning |
|---|---|
| **Job** | Triggered by an action (e.g. `collect`, `count`) |
| **Stage** | Group of tasks separated by a shuffle boundary |
| **Task** | Unit of work on one partition |
| **DAG** | Directed Acyclic Graph of transformations - Spark's execution plan |
| **Partition** | Chunk of data processed by one task |
| **Shuffle** | Redistribution of data across partitions (expensive) |

---

## 2. SparkSession

`SparkSession` is the entry point for all Spark functionality. In Spark 2+, it wraps `SparkContext`, `SQLContext`, and `HiveContext`.

```java
import org.apache.spark.sql.SparkSession;

SparkSession spark = SparkSession.builder()
    .appName("MyApp")
    .master("local[*]")      // local: use all cores. For cluster: "yarn" or "k8s://..."
    .config("spark.sql.shuffle.partitions", "50")   // default 200
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .getOrCreate();

spark.stop();   // always call on exit
```

---

## 3. RDD Basics

RDDs (Resilient Distributed Datasets) are the low-level API. Prefer DataFrames/Datasets for new code - they benefit from the Catalyst optimizer.

```java
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.api.java.JavaRDD;
import scala.Tuple2;

JavaSparkContext jsc = new JavaSparkContext(spark.sparkContext());

// Create
JavaRDD<Integer> rdd = jsc.parallelize(Arrays.asList(1, 2, 3, 4, 5));
JavaRDD<String> fromFile = jsc.textFile("hdfs:///data/input.txt");

// Transformations (lazy)
JavaRDD<Integer> doubled = rdd.map(x -> x * 2);
JavaRDD<Integer> evens   = rdd.filter(x -> x % 2 == 0);
JavaRDD<Integer> flat    = rdd.flatMap(x -> Arrays.asList(x, x * 2).iterator());

// PairRDD (key-value)
JavaPairRDD<String, Integer> pairs = rdd.mapToPair(x -> new Tuple2<>("key" + x, x));
pairs.groupByKey();
pairs.reduceByKey(Integer::sum);
pairs.sortByKey();

// Actions (trigger execution)
List<Integer> collected = rdd.collect();
long count    = rdd.count();
int total     = rdd.reduce(Integer::sum);
List<Integer> top3 = rdd.take(3);
rdd.foreach(x -> System.out.println(x));
rdd.saveAsTextFile("hdfs:///output/");
```

---

## 4. DataFrame API

A DataFrame is a distributed collection of `Row` objects with a schema. Think of it as a distributed table.

```java
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import static org.apache.spark.sql.functions.*;

// Create from CSV
Dataset<Row> df = spark.read()
    .option("header", "true")
    .option("inferSchema", "true")
    .csv("data.csv");

// Inspect
df.printSchema();
df.show(5);
df.show(5, false);   // don't truncate columns
df.count();
df.describe("age", "salary").show();

// Select
df.select("name", "age");
df.select(col("name"), col("age").plus(1).as("age_plus_one"));

// Filter
df.filter(col("age").gt(18));
df.filter("age > 18");                       // SQL-style string expression
df.filter(col("dept").isin("Eng", "Sales"));

// GroupBy / Agg
df.groupBy("department")
  .agg(
      count("*").as("headcount"),
      avg("salary").as("avg_salary"),
      max("salary").as("max_salary")
  );

// Join
df.join(deptDf, df.col("dept_id").equalTo(deptDf.col("id")), "left");
// join types: inner, left, right, outer, left_semi, left_anti, cross

// OrderBy
df.orderBy(col("age").desc(), col("name").asc());

// Column operations
df.withColumn("is_senior", col("age").gt(50));
df.withColumnRenamed("old_name", "new_name");
df.drop("unwanted_col");
df.distinct();
df.dropDuplicates("email");

// Null handling
df.na().drop();                                      // drop rows with any null
df.na().drop("any", new String[]{"name", "email"}); // drop if null in these cols
df.na().fill(0, new String[]{"age"});                // fill nulls with 0
df.na().replace("city", Map.of("NYC", "New York"));
```

### 4.1. Common Functions

Built-in column functions from `org.apache.spark.sql.functions`. Import statically with `import static org.apache.spark.sql.functions.*` to avoid prefixing every call.

```java
import static org.apache.spark.sql.functions.*;

col("name")
lit("constant_value")
when(col("age").lt(18), "minor").otherwise("adult")
coalesce(col("a"), col("b"), lit("default"))    // first non-null
concat(col("first_name"), lit(" "), col("last_name"))
upper(col("name"))
lower(col("name"))
trim(col("name"))
length(col("name"))
substring(col("name"), 1, 3)                    // 1-indexed
to_date(col("str_col"), "yyyy-MM-dd")
date_format(col("dt"), "MM/dd/yyyy")
year(col("date_col"))
month(col("date_col"))
date_add(col("date_col"), 7)
unix_timestamp(col("ts_col"))
current_timestamp()
explode(col("array_col"))                       // array -> multiple rows
array_contains(col("arr"), "value")
size(col("array_col"))
struct(col("a"), col("b"))                      // combine into struct
cast(col("str_num"), DataTypes.IntegerType)
```

---

## 5. Dataset API (Typed)

A `Dataset<T>` is a typed version of a DataFrame. In Java you define a Java bean (POJO with getters/setters) and encode it.

```java
import org.apache.spark.sql.Encoder;
import org.apache.spark.sql.Encoders;

// Java bean
public class User implements Serializable {
    private String name;
    private int age;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}

Encoder<User> encoder = Encoders.bean(User.class);
Dataset<User> users = spark.read().json("users.json").as(encoder);

// Typed operations
Dataset<String> names = users
    .filter(u -> u.getAge() > 18)
    .map(u -> u.getName(), Encoders.STRING());

// Convert back to DataFrame
Dataset<Row> df = users.toDF();
```

When Java bean encoding is verbose, stick with `Dataset<Row>` (DataFrame) and use `Encoders.STRING()`, `Encoders.INT()` etc. for simple typed datasets.

---

## 6. Transformations vs Actions

**Transformations** are lazy - they build the execution plan but do not run.
**Actions** trigger the actual execution.

| Transformations (lazy) | Actions (execute) |
|---|---|
| `map`, `flatMap`, `filter` | `collect`, `collectAsList` |
| `groupBy`, `agg`, `orderBy` | `count`, `first`, `take(n)` |
| `select`, `withColumn` | `show`, `foreach` |
| `join`, `union` | `write` / `save` |
| `distinct`, `repartition` | `reduce` (RDD only) |

---

## 7. Spark SQL

Register a DataFrame as a temporary view and query it with standard SQL. Useful for complex multi-join logic or window functions.

```java
// Register as temp view
df.createOrReplaceTempView("users");

// Run SQL
Dataset<Row> result = spark.sql(
    "SELECT name, age FROM users WHERE age > 18 ORDER BY age DESC"
);

// Joins in SQL
spark.sql("""
    SELECT u.name, d.dept_name
    FROM users u
    LEFT JOIN departments d ON u.dept_id = d.id
""");

// Window functions
spark.sql("""
    SELECT name, salary,
           RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank
    FROM users
""");

// List available tables
spark.catalog().listTables().show();
```

---

## 8. Reading & Writing Data

Common formats: CSV, JSON, Parquet, JDBC. Write modes: `overwrite`, `append`, `ignore`, `errorIfExists`.

```java
// Read CSV
Dataset<Row> df = spark.read()
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("delimiter", ",")
    .load("hdfs:///data/*.csv");

// Read JSON (one JSON object per line)
Dataset<Row> json = spark.read().json("hdfs:///data/events.json");

// Read Parquet (schema auto-detected)
Dataset<Row> parquet = spark.read().parquet("hdfs:///data/users/");

// Read JDBC
Properties props = new Properties();
props.put("user", "admin");
props.put("password", "secret");
Dataset<Row> jdbc = spark.read()
    .jdbc("jdbc:postgresql://host:5432/mydb", "users", props);

// Write
df.write()
    .format("parquet")
    .mode("overwrite")          // overwrite, append, ignore, errorIfExists
    .partitionBy("year", "month")
    .save("hdfs:///output/users/");

df.write().format("json").mode("append").save("hdfs:///output/logs/");

df.coalesce(1).write().option("header", "true").csv("output/single.csv");

df.write().jdbc(url, "target_table", props);
```

---

## 9. Partitioning & Shuffle

Control partition count with `repartition` (full shuffle, can increase) or `coalesce` (no shuffle, can only decrease). Partition count should match cluster parallelism.

```java
df.rdd().getNumPartitions()           // check current partition count
df.repartition(100)                    // full shuffle - increase partitions
df.coalesce(10)                        // no full shuffle - decrease partitions only
df.repartition(col("country"))         // shuffle by column - good before joins

// Broadcast join - avoids shuffle for small tables
import org.apache.spark.sql.functions.broadcast;
df.join(broadcast(smallDf), "country_id")
```

| | `repartition` | `coalesce` |
|---|---|---|
| Full shuffle | yes | no |
| Can increase partitions | yes | no (only decrease) |
| Resulting partitions | roughly equal size | may be unequal |

**Tuning shuffle partitions:**
- Default `spark.sql.shuffle.partitions = 200` (set at SparkSession or per-query).
- For small data: set to `~2x number of cores`.
- For large data (>100GB): `200-2000` depending on data size.

---

## 10. Caching & Persistence

Cache a DataFrame or RDD when it will be reused multiple times in the same job. Call `unpersist()` when done to free memory.

```java
import org.apache.spark.storage.StorageLevel;

df.cache();                                    // MEMORY_AND_DISK
df.persist(StorageLevel.MEMORY_ONLY());
df.persist(StorageLevel.MEMORY_AND_DISK_SER()); // serialised - less memory, more CPU
df.persist(StorageLevel.DISK_ONLY());
df.unpersist();                                // free memory

// RDD
rdd.cache();
rdd.persist(StorageLevel.MEMORY_ONLY());
```

---

## 11. UDFs

UDFs are a black box to the Catalyst optimizer. Prefer built-in functions from `functions.*` when possible, and `Dataset.map()` for typed operations.

```java
import org.apache.spark.sql.api.java.UDF1;
import org.apache.spark.sql.types.DataTypes;

// Register
spark.udf().register(
    "toUpper",
    (UDF1<String, String>) s -> s == null ? null : s.toUpperCase(),
    DataTypes.StringType
);

// Use in SQL
spark.sql("SELECT toUpper(name) FROM users").show();

// Use in DataFrame API
df.withColumn("upper_name", callUDF("toUpper", col("name")));
```

---

## 12. Configuration & Tuning

Set in `SparkConf`, `SparkSession.builder().config()`, `spark-defaults.conf`, or via `--conf` on `spark-submit`.

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 10 \
  --executor-cores 4 \
  --executor-memory 8g \
  --driver-memory 4g \
  --conf spark.sql.shuffle.partitions=400 \
  --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
  --class com.example.MyApp \
  my-app.jar
```

| Config | Default | Notes |
|---|---|---|
| `spark.sql.shuffle.partitions` | 200 | Reduce for small jobs |
| `spark.executor.memory` | 1g | Include overhead (~10%) |
| `spark.executor.cores` | 1 | 4-5 per executor is typical |
| `spark.default.parallelism` | varies | For RDD operations |
| `spark.serializer` | Java | Set KryoSerializer for speed |
| `spark.memory.fraction` | 0.6 | Fraction for execution + storage |
| `spark.memory.storageFraction` | 0.5 | Fraction of above for caching |
| `spark.speculation` | false | Re-launch slow tasks |

**Common performance tips:**
- Avoid `collect()` on large datasets - bring only what you need.
- Use `filter` early to reduce data volume before joins.
- Broadcast small tables in joins.
- Use Parquet or ORC - columnar formats skip irrelevant columns.
- Prefer `reduceByKey` over `groupByKey` for RDDs (less shuffle).
- Use Kryo serializer.

---

## 13. Structured Streaming

Structured Streaming treats a live data stream as an unbounded table.

### 13.1. Kafka Source

Read from Kafka as a streaming source. The value column arrives as bytes; cast and parse with `from_json`.

```java
Dataset<Row> raw = spark.readStream()
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "events")           // or "topic1,topic2" or "topic.*"
    .option("startingOffsets", "latest")     // latest or earliest or JSON offsets
    .load();

// Kafka produces: key, value, topic, partition, offset, timestamp
// value is bytes - cast and parse
import org.apache.spark.sql.types.*;

StructType schema = new StructType()
    .add("user_id", DataTypes.LongType)
    .add("event", DataTypes.StringType)
    .add("event_time", DataTypes.TimestampType);

Dataset<Row> parsed = raw
    .select(from_json(col("value").cast("string"), schema).as("data"))
    .select("data.*");
```

### 13.2. Windowed Aggregations & Watermark

Watermarks bound how late out-of-order data is accepted. Events older than `(max event time - watermark duration)` are discarded. Combine with `window()` to group events into fixed time buckets.

```java
// Watermark tells Spark how late data can arrive
// It will discard events older than (max event time - watermark duration)
Dataset<Row> result = parsed
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        window(col("event_time"), "5 minutes"),   // tumbling window
        col("user_id")
    )
    .agg(count("*").as("event_count"));
```

### 13.3. Output Sinks & Modes

Three output modes: `append` (new rows only), `update` (changed rows since last trigger), `complete` (full result table, aggregations only). Not all modes are supported by every sink.

```java
// Output modes
// append   - only new rows added since last trigger (default for non-aggregated streams)
// update   - only rows that changed since last trigger
// complete - full result table every trigger (only for aggregations)

// File sink
result.writeStream()
    .outputMode("append")
    .format("parquet")
    .option("path", "hdfs:///output/events")
    .option("checkpointLocation", "hdfs:///checkpoints/events")  // required
    .trigger(Trigger.ProcessingTime("1 minute"))
    .start()
    .awaitTermination();

// Kafka sink
result.selectExpr("CAST(user_id AS STRING) AS key", "to_json(struct(*)) AS value")
    .writeStream()
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("topic", "output-topic")
    .option("checkpointLocation", "hdfs:///checkpoints/output")
    .start();

// Console sink (debug only)
parsed.writeStream()
    .outputMode("append")
    .format("console")
    .start();

// Foreach sink (custom output)
result.writeStream()
    .foreach(new ForeachWriter<Row>() {
        public boolean open(long partitionId, long epochId) { return true; }
        public void process(Row value) { /* write to DB or API */ }
        public void close(Throwable errorOrNull) { /* cleanup */ }
    })
    .start();
```

### 13.4. Checkpointing

Checkpointing is **mandatory** for all streaming queries with fault tolerance. It stores the query progress (offsets) and aggregation state to a durable location (HDFS, S3, GCS).

```java
.option("checkpointLocation", "hdfs:///checkpoints/my-query")
```

Each streaming query must have a unique checkpoint location.

### 13.5. Triggers

| Trigger | Behaviour |
|---|---|
| `Trigger.ProcessingTime("1 minute")` | Micro-batch every N time units |
| `Trigger.Once()` | Process all available data once, then stop |
| `Trigger.AvailableNow()` | Like Once but uses multiple micro-batches |
| `Trigger.Continuous("1 second")` | Experimental continuous processing (low latency) |
