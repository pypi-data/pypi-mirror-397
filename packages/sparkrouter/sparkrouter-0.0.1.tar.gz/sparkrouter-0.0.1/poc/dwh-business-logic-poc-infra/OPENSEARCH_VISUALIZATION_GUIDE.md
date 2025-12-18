# OpenSearch Visualization Guide - Job Metrics

Complete guide to creating professional dashboards for tracking job performance, throughput, and data quality.

> **Note**: This guide was written for OpenSearch Dashboards 2.11.x. UI locations may vary slightly between versions. The key concepts (index patterns, aggregations, field names) remain the same.

---

## Overview

### Index Structure

The Lambda processor indexes metrics to **two indices**:

| Index | Purpose | Use Case |
|-------|---------|----------|
| `job-metrics` | Common fields across ALL jobs | Cross-job dashboards, SLA monitoring, cost analysis |
| `job-metrics-{job_name}` | Full metrics including job-specific payload | Deep-dive analysis for specific jobs |

For example, `transform_images` job data is in:
- `job-metrics` - common metrics only
- `job-metrics-transform-images` - full metrics including payload

### Field Structure

**Common Fields** (top-level in both indices):

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | date | When metrics were published |
| `job_name` | keyword | Job identifier (e.g., `transform_images`) |
| `job_run_id` | keyword | Unique run ID (Spark application ID) |
| `job_status` | keyword | SUCCESS, FAILED |
| `start_time` | date | Job start timestamp |
| `end_time` | date | Job end timestamp |
| `duration_seconds` | float | Total job duration |
| `service_provider` | keyword | GLUE, DATABRICKS, EMR, CONTAINER |
| `environment` | keyword | sandbox, dev, prod |
| `region` | keyword | AWS region |
| `created_by` | keyword | User/system that triggered job |
| `data_start_datetime` | date | Data range start (for time-based indexing) |
| `data_end_datetime` | date | Data range end |
| `source_base_path` | keyword | Source data path |
| `sink_base_path` | keyword | Output data path |
| `records_read` | long | Total records extracted |
| `records_written` | long | Total records written |
| `records_dropped` | long | Total records dropped |
| `bytes_written` | long | Total bytes written |
| `extract_duration_seconds` | float | Extract phase duration |
| `transform_duration_seconds` | float | Transform phase duration |
| `load_duration_seconds` | float | Load phase duration |
| `spark_executor_count` | integer | Number of Spark executors |
| `spark_executor_memory_gb` | integer | Executor memory (GB) |
| `glue_dpu_seconds` | float | Glue DPU-seconds consumed |

**Job-Specific Fields** (in `job-metrics-{job_name}` only):

| Field Path | Description |
|------------|-------------|
| `payload.extract.*` | Job-specific extract metrics |
| `payload.transform.*` | Job-specific transform metrics |
| `payload.load.*` | Job-specific load metrics |
| `phases.*` | Detailed phase timing |
| `resources.*` | Resource utilization details |
| `drop_reasons.*` | Breakdown of drop reasons |

### Transform Images Payload Fields

For `job-metrics-transform-images` index:

| Field Path | Type | Description |
|------------|------|-------------|
| `payload.extract.partitions_requested` | int | Partitions requested |
| `payload.extract.partitions_found` | int | Partitions with data |
| `payload.extract.partitions_empty` | int | Empty partitions |
| `payload.extract.records_after_filter` | int | Valid records after filtering |
| `payload.extract.corrupt_records` | int | Corrupt JSON records |
| `payload.extract.null_eventtime` | int | Records with null eventTime |
| `payload.extract.null_data` | int | Records with null data |
| `payload.extract.min_event_time` | string | Earliest event timestamp |
| `payload.extract.max_event_time` | string | Latest event timestamp |
| `payload.extract.event_time_range_hours` | float | Time span of data |
| `payload.transform.records_input` | int | Records entering transform |
| `payload.transform.records_output` | int | Records after transform |
| `payload.transform.decryption_failures` | int | Decryption failures |
| `payload.transform.data_types.*` | object | Per-data-type breakdown |
| `payload.load.records_input` | int | Records entering load |
| `payload.load.partitions_written` | int | Output partitions |
| `payload.load.files_written` | int | Output files |
| `payload.load.cleanup_duration_seconds` | float | Cleanup phase duration |
| `payload.load.serialization_duration_seconds` | float | Serialization duration |
| `payload.load.bytes_by_category.*` | object | Bytes per category |
| `payload.load.output_summary.*` | object | Per-category summary |
| `payload.dropped_records.records_written` | int | Dropped records saved |
| `payload.dropped_records.files_written` | int | Dropped record files |
| `payload.dropped_records.bytes_written` | int | Dropped records bytes |

---

## Step 1: Create Index Patterns (One-Time Setup)

### Create Common Index Pattern (Cross-Job Analysis)

1. Log into OpenSearch Dashboards
   - URL: `terraform output opensearch_dashboard_endpoint`
   - Username: `admin`
   - Password: from `infra/local.tf`

2. Navigate to Index Patterns:
   - Click hamburger menu (☰) → **Management** → **Dashboards Management** → **Index patterns**

3. Create pattern:
   - Click **Create index pattern**
   - Index pattern name: `job-metrics`
   - Click **Next step**
   - Time field: Select `data_start_datetime` (recommended for data-centric view) or `timestamp`
   - Click **Create index pattern**

### Create Job-Specific Index Pattern (Deep Dive)

Repeat for job-specific index:
- Index pattern name: `job-metrics-transform-images`
- Time field: `data_start_datetime`

---

## Step 2: Create Calculated Fields (Optional but Recommended)

### Create Throughput Field

1. Go to: **Management** → **Dashboards Management** → **Index patterns** → **job-metrics-transform-images**
2. Click the **Scripted fields** tab
3. Click **Add scripted field**
4. Fill in:
   - **Name**: `throughput_per_second`
   - **Language**: `painless`
   - **Type**: `number`
   - **Script**:
     ```
     if (doc['duration_seconds'].size() > 0 && doc['duration_seconds'].value > 0) {
       return doc['records_written'].value / doc['duration_seconds'].value;
     }
     return 0;
     ```
5. Click **Create field**

### Create Success Rate Field

1. Click **Add scripted field** again
2. Fill in:
   - **Name**: `success_rate_percent`
   - **Language**: `painless`
   - **Type**: `number`
   - **Script**:
     ```
     if (doc['records_read'].size() > 0 && doc['records_read'].value > 0) {
       double rate = (double)doc['records_written'].value / doc['records_read'].value;
       return rate * 100;
     }
     return 0;
     ```
3. Click **Create field**

---

## Step 3: Create Visualizations

> **OpenSearch 2.11+ UI Note**: The visualization editor has a left panel for configuration. Look for:
> - **Data** tab for metrics and buckets
> - **Metrics & Axes** or **Style** tabs for visual options
> - Some options from older guides may be in different locations or renamed

### Core Visualizations to Create

For each visualization below, the essential configuration is:
- **Chart Type**: What kind of chart
- **Y-axis**: The metric to display (aggregation + field)
- **X-axis**: How to group/bucket the data
- **Index**: `job-metrics-transform-images`
- **Time field for X-axis**: `data_start_datetime`

| # | Title | Chart Type | Y-axis (Aggregation → Field) | Notes |
|---|-------|------------|------------------------------|-------|
| 1 | Images Extracted - Volume Trends | Line | Sum → `records_read` | Shows data volume over time |
| 2 | Processing Throughput | Line | Average → `throughput_per_second` | Requires scripted field |
| 3 | Images Dropped - Data Quality | Area | Sum → `records_dropped` | Use red/orange color if possible |
| 4 | Job Duration Over Time | Line | Average → `duration_seconds` | Track performance trends |
| 5 | Processing Success Rate | Line | Average → `success_rate_percent` | Requires scripted field |

### Creating a Visualization (General Steps)

1. **Visualize** → **Create visualization**
2. Select chart type (Line, Area, etc.)
3. Select index: `job-metrics-transform-images`
4. In the configuration panel:
   - **Metrics** section: Set aggregation and field for Y-axis
   - **Buckets** section: Add X-axis → Date Histogram → `data_start_datetime`
5. Click **Update** or **Apply** to preview
6. **Save** with descriptive title

### Key Metric Visualizations (Single Values)

These show values as big numbers on your dashboard.

#### Latest Run Metrics

Show metrics from the most recent run only:

| Title | Aggregation | Field |
|-------|-------------|-------|
| Latest Run - Images Processed | Sum | `records_written` |
| Latest Run - Images Dropped | Sum | `records_dropped` |
| Latest Run - Duration | Sum | `duration_seconds` |

**Bucket configuration (same for all):**
- Split group → Terms → `job_run_id` → Size: **1**
- Order by: **Custom metric**
  - Aggregation: `Max`
  - Field: `data_start_datetime`
  - Order: Descending

#### Average Metrics (Last N Runs)

Show averages over the most recent N runs:

| Title | Aggregation | Field |
|-------|-------------|-------|
| Avg Duration (Last 10 Runs) | Average | `duration_seconds` |
| Avg Success Rate (Last 10 Runs) | Average | `success_rate_percent` |

**Bucket configuration (same for all):**
- Split group → Terms → `job_run_id` → Size: **10** (adjust N as needed)
- Order by: **Custom metric**
  - Aggregation: `Max`
  - Field: `data_start_datetime`
  - Order: Descending

This gets the N most recent runs by `job_run_id`, then calculates the average across them.

---

## Step 4: Create Executive Dashboard

Combine your saved visualizations into a single dashboard.

1. **Dashboard** → **Create dashboard** (or **Create new**)

2. **Add visualizations**: Click **Add** or **Add panel** → Select your saved visualizations

3. **Arrange**: Drag and resize panels to create your layout

4. **Set time range**: Top right time picker - ensure it covers your data dates

5. **Save**: Give it a descriptive title like `Transform Images Job - Dashboard`

**Suggested Layout:**

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Images      │ Images      │ Duration    │ Success     │
│ Processed   │ Dropped     │ (seconds)   │ Rate (%)    │
└─────────────┴─────────────┴─────────────┴─────────────┘
┌───────────────────────────────────────────────────────┐
│ Images Extracted - Volume Trends                       │
└───────────────────────────────────────────────────────┘
┌──────────────────────────┬────────────────────────────┐
│ Processing Throughput    │ Job Duration Over Time     │
└──────────────────────────┴────────────────────────────┘
┌──────────────────────────┬────────────────────────────┐
│ Images Dropped           │ Success Rate               │
└──────────────────────────┴────────────────────────────┘
```

---

## Step 5: Advanced Visualizations

### Phase Duration Breakdown

Show which ETL phase takes the most time:

| Setting | Value |
|---------|-------|
| Chart Type | Horizontal Bar or Vertical Bar |
| Index | `job-metrics-transform-images` |
| Metrics | Add 3 metrics: Average of `extract_duration_seconds`, `transform_duration_seconds`, `load_duration_seconds` |
| X-axis | Date Histogram → `data_start_datetime` |
| Mode | Stacked (if available) |
| Title | `Job Phases - Duration Breakdown` |

---

## Step 6: Cross-Job Dashboard

Use the **common index** (`job-metrics`) to compare across different jobs:

| Visualization | Aggregation | Field | Split By |
|--------------|-------------|-------|----------|
| Records by Job | Sum | `records_written` | `job_name` |
| Duration by Job | Average | `duration_seconds` | `job_name` |

---

## Step 7: Filters

In dashboard view, click **Add filter** to filter by:
- `job_name` = `transform_images`
- `environment` = `prod`
- `job_status` = `SUCCESS`

---

## Step 8: Share

- **Export**: Management → Saved Objects → Export (JSON backup)
- **Share URL**: Open dashboard → Share → Copy link

---

## Troubleshooting

### No Data Showing

1. Check time range (top right) - expand to "Last 30 days"
2. Verify index pattern: **Management** → **Dashboards Management** → **Index patterns** → Refresh field list
3. Check data exists: **Dev Tools** → Console:
   ```json
   GET job-metrics-transform-images/_search
   {
     "size": 1,
     "sort": [{"data_start_datetime": "desc"}]
   }
   ```

### Field Not Found

If a field doesn't appear in the dropdown:

1. Go to index pattern: **Management** → **Dashboards Management** → **Index patterns** → Select your pattern
2. Click **Refresh field list** (circular arrow icon)
3. Check field list - if still missing, verify Lambda is sending that field

**Common field mappings:**
- Old: `extract.records_read` → New: `records_read` (top-level) or `payload.extract.records_after_filter`
- Old: `load.records_written` → New: `records_written` (top-level) or `payload.load.files_written`
- Old: `total_dropped` → New: `records_dropped`
- Old: `start_date` → New: `data_start_datetime`
- Old: `end_date` → New: `data_end_datetime`

### Scripted Fields Not Working

If scripted fields error:

1. Check field names match exactly (case-sensitive)
2. Use **Dev Tools** to verify field structure:
   ```json
   GET job-metrics-transform-images/_mapping
   ```
3. Update script to match actual field paths

### Dashboard Loads Slowly

1. Reduce time range (e.g., Last 7 days instead of Last 90 days)
2. Reduce visualization complexity (fewer aggregations)
3. Increase auto-refresh interval (10 minutes instead of 1 minute)

---

## Quick Reference Card

### Indices

| Index | Purpose | Time Field |
|-------|---------|------------|
| `job-metrics` | Cross-job comparison | `data_start_datetime` |
| `job-metrics-transform-images` | Transform images deep-dive | `data_start_datetime` |

### Common Fields (All Indices)

| Metric | Field |
|--------|-------|
| Images Extracted | `records_read` |
| Images Processed | `records_written` |
| Images Dropped | `records_dropped` |
| Duration | `duration_seconds` |
| Extract Duration | `extract_duration_seconds` |
| Transform Duration | `transform_duration_seconds` |
| Load Duration | `load_duration_seconds` |
| Glue Cost | `glue_dpu_seconds` |

### Job-Specific Fields (job-metrics-transform-images)

| Metric | Field Path |
|--------|------------|
| Partitions Found | `payload.extract.partitions_found` |
| Corrupt Records | `payload.extract.corrupt_records` |
| Transform Output | `payload.transform.records_output` |
| Files Written | `payload.load.files_written` |
| Dropped Records Saved | `payload.dropped_records.records_written` |

### Calculated Fields

| Field | Formula |
|-------|---------|
| `throughput_per_second` | `records_written / duration_seconds` |
| `success_rate_percent` | `(records_written / records_read) * 100` |

---

## Next Steps

1. ✅ Create index patterns (common + job-specific)
2. ✅ Create scripted fields (throughput, success rate)
3. ✅ Create core visualizations
4. ✅ Assemble into executive dashboard
5. ✅ Create cross-job comparison dashboard
6. ✅ Set up auto-refresh and time range
7. ✅ Share with management

### Future Enhancements

- **Alerting**: Set up monitors to email when success rate drops below threshold
- **Cost Tracking**: Visualization for `glue_dpu_seconds` to track compute costs
- **Data Type Breakdown**: Visualize `payload.transform.data_types` for image type distribution
- **Drop Reason Analysis**: Detailed breakdown using `drop_reasons` field
- **Environment Comparison**: Compare prod vs dev performance using `environment` filter
