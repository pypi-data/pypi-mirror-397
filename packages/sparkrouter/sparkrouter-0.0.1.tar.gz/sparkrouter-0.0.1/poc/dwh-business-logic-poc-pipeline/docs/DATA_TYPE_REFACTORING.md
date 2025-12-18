# Data Type Refactoring - Preserve Actual Processor Values

## Overview

Refactored the data_type logic to preserve actual processor values from `__meta__.savedproject.processor` instead of mapping them to just "nautilus" or "savedproject". This enables richer metrics collection and moves the S3 path routing logic to the loader where it belongs.

## Problem Statement

### Before Refactoring

**Transform Phase** (business logic):
```python
# Hard-coded mapping in transformer
if processor contains "nautilus":
    data_type = "nautilus"
else:
    data_type = "savedproject"
```

**Issues**:
1. Lost actual processor information
2. Metrics only showed 2 types (nautilus/savedproject)
3. Couldn't track individual processor performance
4. S3 routing logic mixed with transform logic

### After Refactoring

**Transform Phase** (business logic):
```python
# Preserve actual value
data_type = lower(__meta__.savedproject.processor) or "unknown"
```

**Load Phase** (infrastructure logic):
```python
# Map processors to S3 paths
if processor in NAUTILUS_PROCESSORS:
    s3_path = "nautilus/transformed_images"
else:
    s3_path = "savedproject/transformed_images"
```

**Benefits**:
1. Preserves all processor information
2. Metrics show every processor type
3. Can track performance per processor
4. Clear separation of concerns

## Implementation

### 1. Transform Phase - Preserve Actual Processor Value

**File**: `src/dwh/jobs/transform_images/transform/image_transformer.py`

```python
df_partitioned = df_flattened.withColumn(
    "data_type",
    when(
        col("__meta__.savedproject.processor").isNotNull(),
        lower(col("__meta__.savedproject.processor"))
    ).otherwise(lit("unknown"))
).drop("__meta__")
```

**Changes**:
- Removed hardcoded "nautilus"/"savedproject" mapping
- Preserves actual processor value (lowercase for consistency)
- Falls back to "unknown" if processor is null

### 2. Load Phase - Map Processors to S3 Paths

**File**: `src/dwh/jobs/transform_images/load/image_loader.py`

```python
class ImageLoader:
    # Map processor types to S3 path prefixes
    NAUTILUS_PROCESSORS = {"nautilus"}

    @staticmethod
    def get_s3_path_for_processor(base_path: str, processor: str) -> str:
        """Map processor value to S3 path."""
        if processor in ImageLoader.NAUTILUS_PROCESSORS:
            return f"{base_path}/nautilus/transformed_images"
        else:
            return f"{base_path}/savedproject/transformed_images"
```

**Changes**:
- Added `NAUTILUS_PROCESSORS` set (configurable)
- Created `get_s3_path_for_processor()` method
- Loader handles S3 path routing logic
- Easy to add more high-priority processors

### 3. Metrics Structure - Nested by Data Type

**File**: `src/dwh/jobs/transform_images/metrics/job_metrics.py`

**Before**:
```python
{
    "transform_records_nautilus": 150000,
    "transform_images_nautilus": 45000,
    "transform_records_savedproject": 1860154,
    "transform_images_savedproject": 620000,
    "load_records_nautilus": 150000,
    "load_files_nautilus": 36,
    ...
}
```

**After**:
```python
{
    "data_types": {
        "nautilus": {
            "transform_records": 150000,
            "transform_images": 45000,
            "load_records": 150000,
            "load_files": 36,
            "load_partitions": 12,
            "load_output_paths": [...],
            "s3_path": "s3://bucket/nautilus/transformed_images",
            "path_category": "nautilus"
        },
        "web_processor": {
            "transform_records": 500000,
            "transform_images": 200000,
            "load_records": 500000,
            "load_files": 120,
            "load_partitions": 25,
            "load_output_paths": [...],
            "s3_path": "s3://bucket/savedproject/transformed_images",
            "path_category": "savedproject"
        },
        "mobile_app": {
            "transform_records": 600000,
            "transform_images": 180000,
            "load_records": 600000,
            "load_files": 150,
            "load_partitions": 30,
            "load_output_paths": [...],
            "s3_path": "s3://bucket/savedproject/transformed_images",
            "path_category": "savedproject"
        }
    }
}
```

**Benefits**:
- All metrics for a processor grouped together
- Easy to understand records vs images
- Shows S3 path routing decision
- Scalable to any number of processors

## Metrics Explanation

### Records vs Images

**Question**: Why two metrics per data_type?

**Answer**:
- **`transform_records`**: Total number of **records** (data rows)
  - May include multiple versions of same image
  - Includes duplicates, historical snapshots
  - Example: 1,107,078 records

- **`transform_images`**: Count of **unique images** by `productimageid`
  - Distinct images only
  - Example: 11,475 unique images
  - Ratio: 1,107,078 / 11,475 = **~96.5 records per image**

This ratio indicates heavy versioning/duplication - each image has ~97 versions on average!

### Additional Metrics Per Data Type

- **`load_records`**: Records written to S3
- **`load_files`**: Number of files written
- **`load_partitions`**: Number of partitions written
- **`load_output_paths`**: List of S3 file paths
- **`s3_path`**: Base S3 path for this processor
- **`path_category`**: Which category (nautilus/savedproject)

## Expected Log Output

### Transform Phase

```
[TRANSFORM] Data type distribution:
[TRANSFORM]   - nautilus: 150000 records, 45000 images
[TRANSFORM]   - web_processor: 500000 records, 200000 images
[TRANSFORM]   - mobile_app: 600000 records, 180000 images
[TRANSFORM]   - desktop_app: 760154 records, 195000 images
```

### Load Phase

```
[LOAD] Data types to process: ['nautilus', 'web_processor', 'mobile_app', 'desktop_app']

[LOAD] Processing data_type: nautilus
[LOAD] Processor: nautilus → nautilus
[LOAD] Output path: s3://bucket/nautilus/transformed_images
[LOAD] Successfully wrote 150000 nautilus records

[LOAD] Processing data_type: web_processor
[LOAD] Processor: web_processor → savedproject
[LOAD] Output path: s3://bucket/savedproject/transformed_images
[LOAD] Successfully wrote 500000 web_processor records

[LOAD] Processing data_type: mobile_app
[LOAD] Processor: mobile_app → savedproject
[LOAD] Output path: s3://bucket/savedproject/transformed_images
[LOAD] Successfully wrote 600000 mobile_app records

[LOAD] Processing data_type: desktop_app
[LOAD] Processor: desktop_app → savedproject
[LOAD] Output path: s3://bucket/savedproject/transformed_images
[LOAD] Successfully wrote 760154 desktop_app records
```

### Metrics Summary

```
================================================================================
JOB METRICS SUMMARY: TransformImagesJob
================================================================================
Total Duration: 120.50 seconds

EXTRACT PHASE:
  Duration: 15.20 seconds
  Records read: 2,010,154
  Records after filtering: 2,010,154

TRANSFORM PHASE:
  Duration: 50.30 seconds
  Records input: 2,010,154
  Records output: 2,010,154
  By data type:
    - desktop_app: 760,154 records, 195,000 images
    - mobile_app: 600,000 records, 180,000 images
    - nautilus: 150,000 records, 45,000 images
    - web_processor: 500,000 records, 200,000 images

LOAD PHASE:
  Duration: 55.00 seconds
  Records written: 2,010,154
  Output files: 486
  By data type:
    - desktop_app → savedproject: 760,154 records, 190 files, 38 partitions
    - mobile_app → savedproject: 600,000 records, 150 files, 30 partitions
    - nautilus → nautilus: 150,000 records, 36 files, 12 partitions
    - web_processor → savedproject: 500,000 records, 110 files, 22 partitions
================================================================================
```

## JSON Metrics Structure

```json
{
  "job_name": "TransformImagesJob",
  "duration_seconds": 120.50,
  "extract": {
    "duration_seconds": 15.20,
    "records_read": 2010154,
    "records_after_filter": 2010154
  },
  "transform": {
    "duration_seconds": 50.30,
    "records_input": 2010154,
    "records_output": 2010154
  },
  "load": {
    "duration_seconds": 55.00,
    "records_written": 2010154,
    "files_written": 486
  },
  "data_types": {
    "nautilus": {
      "transform_records": 150000,
      "transform_images": 45000,
      "load_records": 150000,
      "load_files": 36,
      "load_partitions": 12,
      "load_output_paths": ["s3://bucket/nautilus/..."],
      "s3_path": "s3://bucket/nautilus/transformed_images",
      "path_category": "nautilus"
    },
    "web_processor": {
      "transform_records": 500000,
      "transform_images": 200000,
      "load_records": 500000,
      "load_files": 110,
      "load_partitions": 22,
      "load_output_paths": ["s3://bucket/savedproject/..."],
      "s3_path": "s3://bucket/savedproject/transformed_images",
      "path_category": "savedproject"
    },
    "mobile_app": {
      "transform_records": 600000,
      "transform_images": 180000,
      "load_records": 600000,
      "load_files": 150,
      "load_partitions": 30,
      "load_output_paths": ["s3://bucket/savedproject/..."],
      "s3_path": "s3://bucket/savedproject/transformed_images",
      "path_category": "savedproject"
    },
    "desktop_app": {
      "transform_records": 760154,
      "transform_images": 195000,
      "load_records": 760154,
      "load_files": 190,
      "load_partitions": 38,
      "load_output_paths": ["s3://bucket/savedproject/..."],
      "s3_path": "s3://bucket/savedproject/transformed_images",
      "path_category": "savedproject"
    }
  }
}
```

## Configuration

### Adding High-Priority Processors

To route additional processors to the nautilus path:

```python
class ImageLoader:
    NAUTILUS_PROCESSORS = {
        "nautilus",
        "high_priority_processor",  # Add here
        "real_time_processor"       # Add here
    }
```

### Custom Path Mappings

For more complex routing:

```python
@staticmethod
def get_s3_path_for_processor(base_path: str, processor: str) -> str:
    """Map processor value to S3 path."""
    if processor in ImageLoader.NAUTILUS_PROCESSORS:
        return f"{base_path}/nautilus/transformed_images"
    elif processor in {"batch_processor", "scheduled_job"}:
        return f"{base_path}/batch/transformed_images"
    else:
        return f"{base_path}/savedproject/transformed_images"
```

## Use Cases

### 1. Performance Analysis by Processor

```python
def analyze_processor_performance(metrics):
    """Analyze which processors have highest versioning."""
    for processor, data in metrics.data_types.items():
        records = data['transform_records']
        images = data['transform_images']
        ratio = records / images if images > 0 else 0

        print(f"{processor}:")
        print(f"  Records/Image ratio: {ratio:.2f}")
        print(f"  Category: {data['path_category']}")

# Output:
# desktop_app:
#   Records/Image ratio: 3.90
#   Category: savedproject
# mobile_app:
#   Records/Image ratio: 3.33
#   Category: savedproject
# nautilus:
#   Records/Image ratio: 3.33
#   Category: nautilus
# web_processor:
#   Records/Image ratio: 2.50
#   Category: savedproject
```

### 2. Alert on Unusual Processor Activity

```python
def check_unusual_processors(metrics):
    """Alert if new/unexpected processors appear."""
    expected_processors = {"nautilus", "web_processor", "mobile_app", "desktop_app"}
    actual_processors = set(metrics.data_types.keys())

    new_processors = actual_processors - expected_processors
    if new_processors:
        send_alert(
            subject="New Processor Types Detected",
            message=f"Unexpected processors: {', '.join(new_processors)}"
        )
```

### 3. Resource Planning

```python
def estimate_storage_by_processor(metrics):
    """Estimate storage needs per processor."""
    for processor, data in metrics.data_types.items():
        images = data['transform_images']
        storage_gb = (images * 2) / 1024  # 2MB per image

        print(f"{processor}: {storage_gb:.2f} GB")
```

## Files Modified

1. **src/dwh/jobs/transform_images/transform/image_transformer.py**
   - Removed hardcoded "nautilus"/"savedproject" mapping
   - Preserves actual processor value

2. **src/dwh/jobs/transform_images/load/image_loader.py**
   - Added `NAUTILUS_PROCESSORS` configuration
   - Added `get_s3_path_for_processor()` method
   - Updated loop to use mapping function

3. **src/dwh/jobs/transform_images/metrics/job_metrics.py**
   - Added `data_types` dictionary field
   - Updated `get_summary()` to display nested structure
   - Updated `get_json()` to export nested structure

4. **Transformer metrics setting**:
   - Changed from `setattr(metrics, f"transform_records_{data_type}", ...)`
   - To `metrics.data_types[data_type]['transform_records'] = ...`

5. **Loader metrics setting**:
   - Changed from `setattr(metrics, f"load_records_{data_type}", ...)`
   - To `metrics.data_types[data_type]['load_records'] = ...`

## Backward Compatibility

**Breaking Changes**:
- Metrics structure changed from flat to nested
- `transform_records_nautilus` → `data_types.nautilus.transform_records`
- Dashboards/monitoring need to be updated

**Migration**:
```python
# Old code
nautilus_records = metrics.transform_records_nautilus

# New code
nautilus_records = metrics.data_types.get('nautilus', {}).get('transform_records', 0)
```

## Testing

Test with various processor values:

```python
def test_preserves_processor_value():
    # Input with specific processor
    df = create_test_df(processor="custom_processor")

    # Transform
    result = transformer.transform(df, "test", metrics)

    # Verify processor preserved
    assert "custom_processor" in metrics.data_types
    assert metrics.data_types["custom_processor"]["transform_records"] > 0

def test_maps_to_correct_s3_path():
    # Nautilus processor → nautilus path
    path = ImageLoader.get_s3_path_for_processor("/base", "nautilus")
    assert path == "/base/nautilus/transformed_images"

    # Other processor → savedproject path
    path = ImageLoader.get_s3_path_for_processor("/base", "web_processor")
    assert path == "/base/savedproject/transformed_images"
```

## Conclusion

The refactoring:
- ✅ **Preserves all processor information** (not just nautilus/savedproject)
- ✅ **Enables richer metrics** (track every processor type)
- ✅ **Separates concerns** (business logic vs infrastructure routing)
- ✅ **Configurable routing** (easy to add high-priority processors)
- ✅ **Better organized metrics** (nested by data_type)
- ✅ **Scalable** (works with any number of processors)

**Key Insight**: Records vs Images ratio reveals versioning/duplication patterns per processor type, enabling better performance tuning and resource planning.
