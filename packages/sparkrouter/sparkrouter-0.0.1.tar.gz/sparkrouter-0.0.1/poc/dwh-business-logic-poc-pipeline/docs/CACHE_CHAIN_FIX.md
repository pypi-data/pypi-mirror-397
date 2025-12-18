# Cache Chain Fix - Load Phase Optimization

## Problem: Cache Chain Broken in Load Phase

After implementing caching optimizations, the job experienced a **5-second slowdown** despite processing **2 million records** (a large dataset where caching should help significantly).

### Root Cause: New DataFrames Break Cache Lineage

The load phase receives a cached DataFrame from transform but then creates new DataFrames:

```python
# Transform phase returns cached df_transformed
df = df_transformed  # Cached from transform

# Load phase creates NEW DataFrames
df_with_event_time = df.withColumn(...)  # NEW - breaks cache chain
df_with_pk = df_with_event_time.withColumn(...)  # NEW
out_df = df_with_pk.select(...)  # NEW

# These operations re-execute the entire lineage
partition_summary = out_df.groupBy(...).count()  # Re-executes transform UDF!
s3_data_sink.write_json(out_df, ...)  # Re-executes transform UDF again!
```

**Impact**: The expensive decryption UDF from transform phase executes **3 times** instead of once:
1. Transform phase count (materializes cache)
2. Load phase partition aggregation (re-executes UDF)
3. Load phase write operation (re-executes UDF)

## Solution: Cache Final Output DataFrame

Cache the final `out_df` after all load transformations are complete:

```python
# Create final output DataFrame
out_df = df_with_pk.select(
    col("updated").alias("eventTime"),
    col("updated").alias("event_time"),
    col("pk"),
    out_data.alias("data"),
    col("5min"),
    col("year"),
    col("month"),
    col("day"),
    col("hour"),
    col("min")
).drop("event_timestamp")

# OPTIMIZATION: Cache the final output DataFrame
# This DataFrame will be used multiple times:
# 1. Partition aggregation (groupBy)
# 2. Write operation
# Caching prevents re-executing the entire transform chain twice
if input_count >= 10000:  # Only cache large datasets
    out_df.cache()
    print(f"[LOAD] Output DataFrame cached (large dataset)")

# Get partition distribution - materializes the cache
partition_summary = out_df.groupBy(*partition_columns).count().collect()

# Write operation - uses the cache
output_file_paths = s3_data_sink.write_json(out_df, output_path, partition_columns)
```

## Why This Works

### Spark DataFrame Lineage

Spark DataFrames maintain a lineage (execution plan). Each transformation creates a new DataFrame with extended lineage:

```
Transform Phase:
df_input [cached]
  → decrypt UDF applied
  → df_transformed [cached]

Load Phase (BEFORE fix):
df_transformed [cached from transform]
  → withColumn (event_timestamp)
  → df_with_event_time [NEW lineage - cache broken]
    → withColumn (pk)
    → df_with_pk [NEW lineage]
      → select + drop
      → out_df [NEW lineage]
        → groupBy (re-executes entire lineage from df_input!)
        → write (re-executes entire lineage from df_input!)

Load Phase (AFTER fix):
df_transformed [cached from transform]
  → withColumn (event_timestamp)
  → df_with_event_time [NEW lineage]
    → withColumn (pk)
    → df_with_pk [NEW lineage]
      → select + drop
      → out_df [NEW lineage, but CACHED!]
        → groupBy (uses out_df cache)
        → write (uses out_df cache)
```

### Key Insight

When you apply transformations to a cached DataFrame, the new DataFrame has a lineage that includes the cache:

```
out_df lineage = transform(df_transformed)
```

If `df_transformed` is cached, Spark will use that cache when computing `out_df`. However, once `out_df` is computed, subsequent uses of `out_df` will re-execute its transformations unless we **also cache `out_df`**.

## Performance Analysis

### Your Production Workload: 2 Million Records

**Before Cache Chain Fix**:
```
Transform Phase:
  UDF execution #1: 41.8s (cached)

Load Phase:
  UDF execution #2: 41.8s (partition aggregation re-executes)
  UDF execution #3: 41.8s (write operation re-executes)

Total: ~125s
Observed: 104.7s (some optimizations helped partially)
```

**After Cache Chain Fix**:
```
Transform Phase:
  UDF execution #1: 41.8s (cached)

Load Phase:
  Load transformations: 2-3s (event_timestamp, pk, select)
  Cache out_df: <1s
  Partition aggregation: uses cache (~instant)
  Write operation: uses cache (~instant)

Total: ~50s (expected)
```

**Expected Improvement**: **104.7s → ~50s** = **2x faster**

## Conditional Caching Strategy

We only cache `out_df` for large datasets (>= 10,000 records) because:

- **Small datasets (<10K)**: Caching overhead > re-execution cost
- **Large datasets (>=10K)**: Re-execution cost > caching overhead

For your 2M record workload:
- Threshold: 2,010,154 >= 10,000 ✓
- Caching enabled: YES
- Expected benefit: Significant (avoids 2 UDF re-executions)

## Complete Caching Flow

### End-to-End Pipeline with All Optimizations

```
EXTRACT PHASE:
  Read JSON partitions: [Lazy]
  Single aggregation: [SCAN 1] - All metrics at once
  Filter valid records: [Lazy]
  Result: df_filtered [uncached]

TRANSFORM PHASE:
  Input count check:
    - If input_count >= 10,000: df_filtered.cache()
  Count input: [SCAN 2] - Materializes input cache if large dataset
  Apply UDF transformations: [Lazy]
  Output count check:
    - If input_count >= 10,000: df_transformed.cache()
  Count output: [SCAN 3] - Executes UDF once + caches if large dataset
  Result: df_transformed [cached for large datasets]

LOAD PHASE:
  Input count: [NO SCAN] - Uses metrics.transform_records_output
  Create output DataFrame: [Lazy]
    - withColumn (event_timestamp)
    - withColumn (pk)
    - select final columns
    → out_df
  Cache check:
    - If input_count >= 10,000: out_df.cache()
  Partition aggregation: [SCAN 4] - Materializes out_df cache
  Write operation: [NO SCAN] - Uses out_df cache

TOTAL SCANS: 4 (extract agg, transform input, transform output, load out_df)
UDF EXECUTIONS: 1 (transform phase only)
```

### Before All Optimizations (Baseline)

```
EXTRACT: 5N+1 scans (N partitions, each counted 5 times + 1 final)
TRANSFORM: 3 scans (input, UDF execution, output)
LOAD: 3 scans (input, partition agg, write) - each re-executes UDF

TOTAL SCANS: 50-100+ (depending on partitions)
UDF EXECUTIONS: 4-5 times
Duration: 200-300s (estimated)
```

### After All Optimizations

```
EXTRACT: 1 scan (single aggregation)
TRANSFORM: 2 scans (input cache, UDF + output cache)
LOAD: 1 scan (out_df cache materialization)

TOTAL SCANS: 4
UDF EXECUTIONS: 1 time
Duration: 50-60s (expected for 2M records)
```

**Overall Improvement**: **4-6x faster end-to-end**

## Expected Log Output

When running with 2M records, you should see:

```
[EXTRACT] Starting extract phase...
[EXTRACT] Single-pass metrics aggregation (optimized)...
[EXTRACT] Extracted 2010154 records after filter

[TRANSFORM] Starting with 2010154 records (from extract metrics)
[TRANSFORM] Caching enabled (records >= 10000)
[TRANSFORM] Output caching enabled
[TRANSFORM] Completed transformation with 2010154 output records

[LOAD] Starting load with 2010154 input records (from transform metrics)
[LOAD] clean_sink=True
[LOAD] Output path: s3://bucket/transformed_images
[LOAD] Partition columns: ['year', 'month', 'day', 'hour', 'min']
[LOAD] Output DataFrame partitions: 200
[LOAD] Output DataFrame cached (large dataset)  ← NEW LINE
[LOAD] Unique partition combinations: 45
[LOAD] Validation: Partition total matches input count (2010154 records)
[LOAD] Successfully wrote 2010154 records to s3://bucket/transformed_images
```

## Validation in Spark UI

Check Spark UI to confirm caching behavior:

### Storage Tab
Should show **3 cached DataFrames** for large datasets:
1. `df_filtered` (transform input) - from extract phase
2. `df_transformed` (transform output) - from transform phase
3. `out_df` (load output) - from load phase

### SQL Tab
- Extract aggregation: 1 job
- Transform count (input): 1 job
- Transform count (output): 1 job (executes UDF)
- Load partition aggregation: 0 new jobs (uses cache)
- Load write: 0 new jobs (uses cache)

### Stages
Load phase stages should show "InMemoryTableScan" indicating cache reuse

## Testing

Test the optimization:

```bash
# Run in AWS Glue with 2M records
# Monitor duration_seconds in metrics

# Expected results:
# - transform.duration_seconds: ~42s (UDF execution + caching)
# - load.duration_seconds: ~5-10s (uses cache)
# - total.duration_seconds: ~50-60s (down from 100-105s)
```

## Files Modified

**src/dwh/jobs/transform_images/load/image_loader.py**
- Lines 260-262: Added conditional caching of `out_df` for large datasets
- Comment explains why: prevents re-executing transform chain for partition aggregation and write

## Conclusion

The cache chain fix completes the optimization strategy:

1. ✅ **Extract Phase**: Single aggregation (1 scan instead of 5N+1)
2. ✅ **Transform Phase**: Conditional input/output caching (prevents UDF re-execution)
3. ✅ **Load Phase**: Output DataFrame caching (prevents breaking cache chain)

**For your 2M record workload**:
- Cache enabled at all stages (>= 10K threshold)
- UDF executes **once** instead of 3-5 times
- Expected duration: **~50s** (down from 100-105s)
- **2x improvement** from fixing the cache chain alone
- **4-6x improvement** from all optimizations combined

**Next Step**: Deploy and test in AWS Glue to validate the performance improvement.
