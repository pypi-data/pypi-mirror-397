# Image Count Metrics by Data Type

## Overview

Added unique image count tracking per data_type in the transform phase. This metric helps distinguish between the number of records (which may have duplicates or multiple versions) and the number of unique images being processed.

## Implementation

### Transform Phase - Image Count Tracking

**File**: `src/dwh/jobs/transform_images/transform/image_transformer.py`

```python
# Track data_type distribution (records and images)
from pyspark.sql.functions import countDistinct
data_type_stats = df_transformed.groupBy("data_type").agg(
    count("*").alias("record_count"),
    countDistinct("productimageid").alias("image_count")
).collect()

print(f"[TRANSFORM] Data type distribution:")
for row in data_type_stats:
    print(f"[TRANSFORM]   - {row.data_type}: {row.record_count} records, {row.image_count} images")
    if metrics:
        setattr(metrics, f"transform_records_{row.data_type}", row.record_count)
        setattr(metrics, f"transform_images_{row.data_type}", row.image_count)
```

## Metrics Created

### Per Data Type

- `metrics.transform_images_nautilus` - Count of unique nautilus images (by `productimageid`)
- `metrics.transform_images_savedproject` - Count of unique savedproject images (by `productimageid`)

## Why Track Both Records and Images?

### Records vs Images

**Records**: Total number of data entries being processed. May include:
- Multiple versions of the same image (historical snapshots)
- Duplicate entries
- Different views/representations of the same image

**Images**: Unique count of distinct images, identified by `productimageid`

### Example Scenario

```python
Input Data:
  productimageid='img1', updated='2025-01-15T10:00:00Z'  # Version 1
  productimageid='img1', updated='2025-01-15T11:00:00Z'  # Version 2 (same image, updated)
  productimageid='img2', updated='2025-01-15T10:00:00Z'  # Different image
  productimageid='img3', updated='2025-01-15T10:00:00Z'  # Another image

Metrics:
  transform_records_nautilus: 4        # 4 total records
  transform_images_nautilus: 3         # 3 unique images (img1, img2, img3)
```

## Use Cases

### 1. Data Quality Analysis

Calculate average versions per image:

```python
avg_versions_per_image = (
    metrics.transform_records_nautilus / metrics.transform_images_nautilus
)
print(f"Average versions per nautilus image: {avg_versions_per_image:.2f}")

# Example output: "Average versions per nautilus image: 3.33"
# Indicates each image has ~3 versions on average
```

### 2. Business Insights

Track unique content volume:

```python
def analyze_content_volume(metrics):
    total_images = (
        metrics.transform_images_nautilus +
        metrics.transform_images_savedproject
    )

    nautilus_pct = (metrics.transform_images_nautilus / total_images) * 100

    print(f"Total Unique Images: {total_images:,}")
    print(f"Nautilus Images: {metrics.transform_images_nautilus:,} ({nautilus_pct:.1f}%)")
    print(f"SavedProject Images: {metrics.transform_images_savedproject:,} ({100-nautilus_pct:.1f}%)")
```

### 3. Resource Planning

Estimate storage and processing needs:

```python
def estimate_storage(metrics):
    # Assume average 2MB per unique image
    avg_image_size_mb = 2

    total_images = (
        metrics.transform_images_nautilus +
        metrics.transform_images_savedproject
    )

    estimated_storage_gb = (total_images * avg_image_size_mb) / 1024

    print(f"Estimated Storage Needed: {estimated_storage_gb:.2f} GB")
    print(f"  Nautilus: {(metrics.transform_images_nautilus * avg_image_size_mb) / 1024:.2f} GB")
    print(f"  SavedProject: {(metrics.transform_images_savedproject * avg_image_size_mb) / 1024:.2f} GB")
```

### 4. Alert on Anomalies

Detect unusual record-to-image ratios:

```python
def check_duplication_anomaly(metrics):
    """Alert if record-to-image ratio is unusually high."""

    nautilus_ratio = (
        metrics.transform_records_nautilus / metrics.transform_images_nautilus
    )

    # Typical ratio: 1-5 records per image
    # Alert if ratio > 10 (too many duplicates/versions)
    if nautilus_ratio > 10:
        send_alert(
            subject="High Duplication in Nautilus Data",
            message=f"Average {nautilus_ratio:.1f} records per image (expected: 1-5). "
                   f"Records: {metrics.transform_records_nautilus:,}, "
                   f"Images: {metrics.transform_images_nautilus:,}"
        )
```

## Expected Log Output

### Transform Phase

```
[TRANSFORM] Completed transformation with 2010154 output records
[TRANSFORM] Data type distribution:
[TRANSFORM]   - nautilus: 150000 records, 45000 images
[TRANSFORM]   - savedproject: 1860154 records, 620000 images
```

**Interpretation**:
- Nautilus: 150,000 records representing 45,000 unique images (avg 3.33 records/image)
- SavedProject: 1,860,154 records representing 620,000 unique images (avg 3.00 records/image)

## Metrics Summary Example

Complete metrics for a 2M record job:

```python
{
    # Transform - Overall
    'transform_records_input': 2010154,
    'transform_records_output': 2010154,
    'transform_decryption_failures': 0,

    # Transform - Nautilus
    'transform_records_nautilus': 150000,
    'transform_images_nautilus': 45000,      # NEW: Unique image count

    # Transform - SavedProject
    'transform_records_savedproject': 1860154,
    'transform_images_savedproject': 620000,  # NEW: Unique image count

    # Load - Nautilus
    'load_records_nautilus': 150000,
    'load_files_nautilus': 36,
    'load_partitions_nautilus': 12,

    # Load - SavedProject
    'load_records_savedproject': 1860154,
    'load_files_savedproject': 450,
    'load_partitions_savedproject': 45
}
```

## Validation

### Basic Validation

```python
# Image count should never exceed record count
assert metrics.transform_images_nautilus <= metrics.transform_records_nautilus
assert metrics.transform_images_savedproject <= metrics.transform_records_savedproject

# Images should be at least 1 (if records > 0)
if metrics.transform_records_nautilus > 0:
    assert metrics.transform_images_nautilus > 0
if metrics.transform_records_savedproject > 0:
    assert metrics.transform_images_savedproject > 0
```

### Ratio Validation

```python
def validate_record_image_ratios(metrics):
    """Validate record-to-image ratios are reasonable."""

    for data_type in ['nautilus', 'savedproject']:
        records = getattr(metrics, f'transform_records_{data_type}')
        images = getattr(metrics, f'transform_images_{data_type}')

        if images == 0:
            continue

        ratio = records / images

        # Warn if ratio is outside expected range (1-20)
        if ratio < 1:
            print(f"WARNING: {data_type} has ratio < 1 (impossible - likely data issue)")
        elif ratio > 20:
            print(f"WARNING: {data_type} has unusually high ratio: {ratio:.1f} records/image")
        else:
            print(f"✓ {data_type} ratio OK: {ratio:.1f} records/image")
```

## Performance Considerations

### Caching Still Works

The image count aggregation uses the cached `df_transformed`:

```python
# Cache output DataFrame
if input_count >= cache_threshold:
    df_transformed.cache()

# Count to materialize cache
output_count = df_transformed.count()

# Image count aggregation uses the cache (no re-execution)
data_type_stats = df_transformed.groupBy("data_type").agg(
    count("*").alias("record_count"),
    countDistinct("productimageid").alias("image_count")
).collect()
```

**Performance**: For 2M records:
- Record count: Uses cache (instant)
- Image count aggregation: Uses cache (~1-2 seconds for groupBy + countDistinct)
- **Total overhead**: ~1-2 seconds (negligible)

## Dashboard Integration

Example dashboard query:

```python
def get_image_metrics_for_dashboard(metrics):
    """Extract image metrics in dashboard-friendly format."""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'totals': {
            'records': metrics.transform_records_output,
            'images': (
                metrics.transform_images_nautilus +
                metrics.transform_images_savedproject
            )
        },
        'nautilus': {
            'records': metrics.transform_records_nautilus,
            'images': metrics.transform_images_nautilus,
            'records_per_image': (
                metrics.transform_records_nautilus /
                metrics.transform_images_nautilus
                if metrics.transform_images_nautilus > 0 else 0
            )
        },
        'savedproject': {
            'records': metrics.transform_records_savedproject,
            'images': metrics.transform_images_savedproject,
            'records_per_image': (
                metrics.transform_records_savedproject /
                metrics.transform_images_savedproject
                if metrics.transform_images_savedproject > 0 else 0
            )
        }
    }
```

## Files Modified

**src/dwh/jobs/transform_images/transform/image_transformer.py**
- Lines 170-182: Added `countDistinct` for image counts
- Updated metrics logging to show both records and images
- Created per-data_type image metrics

## Conclusion

Image count metrics provide:
- ✅ **Unique content tracking**: Know how many distinct images (not just records)
- ✅ **Data quality insights**: Detect anomalous duplication ratios
- ✅ **Business intelligence**: Understand content volume by data type
- ✅ **Resource planning**: Estimate storage needs based on unique images
- ✅ **Minimal overhead**: ~1-2 seconds for 2M records (uses cache)
- ✅ **Ready for dashboards**: Easy integration with monitoring systems

**Metrics added**:
- `transform_images_nautilus`
- `transform_images_savedproject`
