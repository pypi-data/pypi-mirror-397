# Data Type Metrics - Complete Structure

## Overview

The transform_images_job now tracks comprehensive metrics grouped by data_type, allowing detailed monitoring of nautilus vs savedproject data processing.

## Complete Metrics Structure

After a successful job execution, the metrics object contains:

### Transform Phase Metrics

```python
{
    # Overall transform metrics
    'transform_records_input': 2010154,
    'transform_records_output': 2010154,
    'transform_decryption_failures': 0,  # If any records lost during UDF execution

    # Per data_type metrics (records)
    'transform_records_nautilus': 150000,
    'transform_records_savedproject': 1860154,

    # Per data_type metrics (unique images)
    'transform_images_nautilus': 45000,
    'transform_images_savedproject': 620000
}
```

### Load Phase Metrics

```python
{
    # Overall load metrics
    'load_records_input': 2010154,
    'load_records_written': 2010154,
    'load_files_written': 486,
    'load_partitions_written': 57,
    'load_cleanup_total_deleted': 114,

    # Flat list of all output paths (legacy compatibility)
    'load_output_paths': [
        's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00000.txt',
        's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00001.txt',
        # ... all nautilus files ...
        's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00000.txt',
        's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00001.txt',
        # ... all savedproject files ...
    ],

    # Grouped by data_type (new)
    'load_output_paths_by_type': {
        'nautilus': [
            's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00000.txt',
            's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00001.txt',
            # ... nautilus files only ...
        ],
        'savedproject': [
            's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00000.txt',
            's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00001.txt',
            # ... savedproject files only ...
        ]
    },

    # Per data_type metrics (nautilus)
    'load_records_nautilus': 150000,
    'load_files_nautilus': 36,
    'load_partitions_nautilus': 12,
    'load_output_paths_nautilus': [
        's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00000.txt',
        's3://bucket/nautilus/transformed_images/year=2025/month=01/.../part-00001.txt',
        # ... nautilus files only ...
    ],

    # Per data_type metrics (savedproject)
    'load_records_savedproject': 1860154,
    'load_files_savedproject': 450,
    'load_partitions_savedproject': 45,
    'load_output_paths_savedproject': [
        's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00000.txt',
        's3://bucket/savedproject/transformed_images/year=2025/month=01/.../part-00001.txt',
        # ... savedproject files only ...
    ]
}
```

## Metrics Breakdown

### Overall Metrics

| Metric | Description | Example Value |
|--------|-------------|---------------|
| `transform_records_input` | Records entering transform phase | 2010154 |
| `transform_records_output` | Records successfully transformed | 2010154 |
| `transform_decryption_failures` | Records lost to UDF failures | 0 |
| `load_records_input` | Records entering load phase | 2010154 |
| `load_records_written` | Total records written across all data_types | 2010154 |
| `load_files_written` | Total files written across all data_types | 486 |
| `load_partitions_written` | Total partitions written across all data_types | 57 |
| `load_cleanup_total_deleted` | Total S3 objects deleted during cleanup | 114 |
| `load_output_paths` | Flat list of all S3 file paths written | `[...]` |
| `load_output_paths_by_type` | Dict of S3 paths grouped by data_type | `{...}` |

### Per Data Type Metrics

For each data_type (e.g., `nautilus`, `savedproject`):

| Metric Pattern | Description | Example (nautilus) |
|----------------|-------------|--------------------|
| `transform_records_{data_type}` | Records of this type after transform | 150000 |
| `transform_images_{data_type}` | Unique images of this type (by productimageid) | 45000 |
| `load_records_{data_type}` | Records of this type written to S3 | 150000 |
| `load_files_{data_type}` | Files written for this type | 36 |
| `load_partitions_{data_type}` | Partitions written for this type | 12 |
| `load_output_paths_{data_type}` | S3 paths for this type only | `[...]` |

## Validation Checks

### Transform Phase Validation

```python
# Check for UDF failures
if metrics.transform_records_output != metrics.transform_records_input:
    failures = metrics.transform_records_input - metrics.transform_records_output
    print(f"WARNING: {failures} records lost to decryption failures")

# Validate data_type distribution sums to total
type_sum = metrics.transform_records_nautilus + metrics.transform_records_savedproject
assert type_sum == metrics.transform_records_output
```

### Load Phase Validation

```python
# Validate per-type sums to total
type_sum = metrics.load_records_nautilus + metrics.load_records_savedproject
assert type_sum == metrics.load_records_written

# Validate output paths consistency
assert len(metrics.load_output_paths) == metrics.load_files_written

# Validate grouped paths match per-type paths
assert metrics.load_output_paths_by_type['nautilus'] == metrics.load_output_paths_nautilus
assert metrics.load_output_paths_by_type['savedproject'] == metrics.load_output_paths_savedproject

# Validate grouped paths sum to total
nautilus_count = len(metrics.load_output_paths_by_type['nautilus'])
savedproject_count = len(metrics.load_output_paths_by_type['savedproject'])
assert nautilus_count + savedproject_count == metrics.load_files_written
```

## Usage Examples

### Monitoring Dashboard

```python
def display_job_metrics(metrics):
    print("=== TRANSFORM PHASE ===")
    print(f"Input Records: {metrics.transform_records_input:,}")
    print(f"Output Records: {metrics.transform_records_output:,}")
    if metrics.transform_decryption_failures:
        print(f"⚠️  Decryption Failures: {metrics.transform_decryption_failures:,}")

    print("\nData Type Distribution:")
    print(f"  Nautilus:")
    print(f"    Records: {metrics.transform_records_nautilus:,}")
    print(f"    Images:  {metrics.transform_images_nautilus:,}")
    print(f"  SavedProject:")
    print(f"    Records: {metrics.transform_records_savedproject:,}")
    print(f"    Images:  {metrics.transform_images_savedproject:,}")

    print("\n=== LOAD PHASE ===")
    print(f"Total Records Written: {metrics.load_records_written:,}")
    print(f"Total Files Written: {metrics.load_files_written:,}")
    print(f"Total Partitions: {metrics.load_partitions_written:,}")

    print("\nBy Data Type:")
    print(f"  Nautilus:")
    print(f"    Records:    {metrics.load_records_nautilus:,}")
    print(f"    Files:      {metrics.load_files_nautilus:,}")
    print(f"    Partitions: {metrics.load_partitions_nautilus:,}")

    print(f"  SavedProject:")
    print(f"    Records:    {metrics.load_records_savedproject:,}")
    print(f"    Files:      {metrics.load_files_savedproject:,}")
    print(f"    Partitions: {metrics.load_partitions_savedproject:,}")

    if metrics.load_cleanup_total_deleted:
        print(f"\nCleanup: Deleted {metrics.load_cleanup_total_deleted:,} objects")
```

### Alerting on Data Type Ratios

```python
def check_data_type_ratio(metrics):
    """Alert if nautilus data exceeds expected threshold."""
    total = metrics.transform_records_output
    nautilus_pct = (metrics.transform_records_nautilus / total) * 100

    if nautilus_pct > 20:  # Alert if >20% nautilus
        send_alert(
            subject="High Nautilus Data Volume",
            message=f"Nautilus represents {nautilus_pct:.1f}% of total data ({metrics.transform_records_nautilus:,} records)"
        )
```

### Downstream Processing

```python
def process_output_files(metrics):
    """Process files by data_type with different priorities."""

    # High-priority: Process nautilus files first
    print("Processing high-priority nautilus data...")
    for file_path in metrics.load_output_paths_nautilus:
        process_file(file_path, priority="high")

    # Standard priority: Process savedproject files
    print("Processing standard savedproject data...")
    for file_path in metrics.load_output_paths_savedproject:
        process_file(file_path, priority="standard")
```

### Data Quality Report

```python
def generate_quality_report(metrics):
    """Generate data quality metrics report."""
    report = {
        'job_timestamp': datetime.utcnow().isoformat(),
        'total_records_processed': metrics.transform_records_input,
        'success_rate': (metrics.load_records_written / metrics.transform_records_input) * 100,
        'decryption_failure_rate': (
            metrics.transform_decryption_failures / metrics.transform_records_input * 100
            if metrics.transform_decryption_failures else 0
        ),
        'data_type_breakdown': {
            'nautilus': {
                'records': metrics.load_records_nautilus,
                'images': metrics.transform_images_nautilus,
                'percentage': (metrics.load_records_nautilus / metrics.load_records_written) * 100,
                'files': metrics.load_files_nautilus,
                'avg_records_per_file': metrics.load_records_nautilus / metrics.load_files_nautilus,
                'avg_records_per_image': metrics.load_records_nautilus / metrics.transform_images_nautilus
            },
            'savedproject': {
                'records': metrics.load_records_savedproject,
                'images': metrics.transform_images_savedproject,
                'percentage': (metrics.load_records_savedproject / metrics.load_records_written) * 100,
                'files': metrics.load_files_savedproject,
                'avg_records_per_file': metrics.load_records_savedproject / metrics.load_files_savedproject,
                'avg_records_per_image': metrics.load_records_savedproject / metrics.transform_images_savedproject
            }
        },
        'storage': {
            'total_files': metrics.load_files_written,
            'total_partitions': metrics.load_partitions_written,
            'cleanup_deleted_objects': metrics.load_cleanup_total_deleted
        }
    }
    return report
```

## Metrics Evolution

### Version 1 (Original)
```python
{
    'load_records_written': 2010154,
    'load_output_paths': [...]  # Flat list
}
```

### Version 2 (Data Type Support)
```python
{
    # Backward compatible
    'load_records_written': 2010154,
    'load_output_paths': [...]  # Flat list (all types combined)

    # New grouped metrics
    'load_output_paths_by_type': {
        'nautilus': [...],
        'savedproject': [...]
    },
    'load_records_nautilus': 150000,
    'load_records_savedproject': 1860154,
    # ... more per-type metrics
}
```

**Backward Compatibility**: Existing code using `load_output_paths` continues to work. New code can use the grouped `load_output_paths_by_type` for data_type-specific processing.

## Testing Metrics

In tests, validate the complete metrics structure:

```python
def test_metrics_structure(job_metrics):
    # Overall metrics
    assert hasattr(job_metrics, 'transform_records_input')
    assert hasattr(job_metrics, 'transform_records_output')
    assert hasattr(job_metrics, 'load_records_written')

    # Per data_type transform metrics
    assert hasattr(job_metrics, 'transform_records_nautilus')
    assert hasattr(job_metrics, 'transform_records_savedproject')

    # Per data_type load metrics
    assert hasattr(job_metrics, 'load_records_nautilus')
    assert hasattr(job_metrics, 'load_records_savedproject')
    assert hasattr(job_metrics, 'load_files_nautilus')
    assert hasattr(job_metrics, 'load_files_savedproject')
    assert hasattr(job_metrics, 'load_output_paths_nautilus')
    assert hasattr(job_metrics, 'load_output_paths_savedproject')

    # Grouped output paths
    assert hasattr(job_metrics, 'load_output_paths_by_type')
    assert isinstance(job_metrics.load_output_paths_by_type, dict)
    assert 'nautilus' in job_metrics.load_output_paths_by_type
    assert 'savedproject' in job_metrics.load_output_paths_by_type
```

## Summary

The enhanced metrics structure provides:
- ✅ **Backward compatibility**: Existing `load_output_paths` still works
- ✅ **Grouped paths**: `load_output_paths_by_type` for data_type-specific processing
- ✅ **Per-type details**: Individual metrics for each data_type
- ✅ **Comprehensive tracking**: Transform + Load metrics per data_type
- ✅ **Easy validation**: Simple sums to verify data integrity
- ✅ **Monitoring ready**: All metrics needed for dashboards and alerts
