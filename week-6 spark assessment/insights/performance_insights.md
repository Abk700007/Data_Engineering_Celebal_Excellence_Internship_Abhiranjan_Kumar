# Spark Performance Insights

## 1. Lazy Evaluation
Spark does not execute `filter()`, `select()`, `withColumn()`, or `groupBy()` the moment they're
called. It only builds up a **logical plan** (lineage). Execution is triggered only when an
**action** is called — `count()`, `show()`, `collect()`, or `write()`.

This matters because it lets Spark's **Catalyst optimizer** see the *entire* chain of operations
before running anything, so it can:
- Reorder operations (e.g. push filters before joins/aggregations)
- Combine multiple narrow transformations into a single task (pipelining)
- Skip work that isn't needed for the final output (e.g. unused columns are never read)

In this pipeline, everything from `df_clean = df.dropna(...)` down through `final_df =
renamed_df.withColumn(...)` was **not** executed until `.show()` or `.count()` or `.write()`
was called further down — confirmed by the fact that no Spark jobs ran in the logs until those
calls.

## 2. DAG / Lineage Graph & Fault Tolerance
Every transformation creates a new node in a **Directed Acyclic Graph (DAG)** that records how
each RDD/DataFrame partition was derived from its parent. If a worker/executor dies mid-job,
Spark doesn't need to replicate data — it simply **recomputes the lost partitions** by replaying
the relevant portion of the lineage graph on another executor. This is what gives Spark fault
tolerance without needing synchronous data replication like a traditional distributed database.

## 3. Narrow vs Wide Transformations (Shuffle)
- **Narrow transformations** (`filter`, `select`, `withColumn`, `withColumnRenamed`) — each output
  partition depends on exactly one input partition. No data movement across the network is
  required.
- **Wide transformations** (`groupBy().agg()`, joins, `distinct()`, `repartition()`) — output
  partitions depend on *multiple* input partitions, which forces a **shuffle**: data with the
  same key has to be redistributed across the cluster. This is by far the most expensive
  operation type in Spark (network I/O + disk spill + serialization).

  In this pipeline, `final_df.groupBy("category").agg(...)` triggered a shuffle stage — visible
  in the execution logs as a separate stage boundary, unlike the single-stage `filter`/`select`
  operations before it.

## 4. CSV vs Parquet
| | CSV | Parquet |
|---|---|---|
| Storage layout | Row-based | Columnar |
| Compression | Minimal (plain text) | Efficient (per-column, snappy by default) |
| Schema | Not stored — must be inferred or supplied every read | Stored in file metadata |
| Predicate Pushdown | Not supported | Supported |
| Column pruning | Not possible — full row must be read | Only requested columns are read |
| Best for | Interop / human-readable exports | Analytical workloads, large datasets |

**Note on file size in this run:** on our small 18-row demo dataset, the Parquet output
(3,830 bytes) was actually *larger* than the CSV output (1,499 bytes). This is expected at
small scale — Parquet's footer, schema metadata, and column-chunk headers are a fixed overhead
that a 20-row file can't amortize. On real datasets (hundreds of thousands of rows or more),
Parquet's columnar compression consistently wins by a wide margin, and the fixed metadata
overhead becomes negligible.

## 5. Predicate Pushdown
When Spark reads a Parquet file with a filter applied (e.g. `.filter(col("final_price") > 1000)`),
it pushes that condition down into the file scan itself rather than reading every row into memory
and filtering afterward. Confirmed in this pipeline's `explain(True)` output:

```
PushedFilters: [IsNotNull(final_price), GreaterThan(final_price,1000.0)]
```

This means Spark can skip entire row groups (or files, in a partitioned table) that can't
possibly match the filter, based on min/max statistics stored in the Parquet metadata — reducing
both I/O and memory pressure. CSV has no such metadata, so a filtered CSV read always requires a
full scan of every row.

## 6. Schema Handling
- `inferSchema=True` requires Spark to make an *extra pass* over the file just to guess column
  types, which is expensive on large files.
- Supplying an **explicit `StructType` schema** (as done for the primary read in this pipeline)
  avoids that extra pass entirely and guarantees consistent types — the recommended approach for
  production pipelines and large datasets.

## 7. Optimization Choices Made in This Pipeline
- Avoided `.collect()` entirely — used `.show()` for all inspection, which only pulls a bounded
  number of rows to the driver instead of the whole dataset.
- Used an explicit schema on the main read path instead of relying solely on `inferSchema`.
- Cleaned nulls (`dropna`/`fillna`) *before* transformations and aggregations, so downstream
  calculations (like `avg_final_price`) aren't skewed by missing values.
- Used `coalesce(1)` only for the CSV output, since this is a small demo dataset meant to produce
  one readable file. On genuinely large datasets, this would be avoided (or replaced with a
  right-sized `repartition`) since forcing a single output file removes write parallelism and can
  create a giant single file that's slow to write and read back.
- Wrote the final result in Parquet as the primary analytical format, keeping CSV only as a
  human-readable secondary export — reflecting standard practice for downstream analytics
  pipelines.
