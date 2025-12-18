# Transform Images - OpenSearch Dashboards

OpenSearch Dashboards v2.11 setup guide for transform_images job monitoring.

---

## Prerequisites

1. OpenSearch cluster is running and accessible
2. Job events are being indexed to `job-events` and `job-events-transform-images`
3. You have access to OpenSearch Dashboards

---

## Step 1: Create Index Patterns

Index patterns tell OpenSearch Dashboards which indices to query.

### Create `job-events-transform-images` Index Pattern

1. Navigate to **Stack Management** > **Index Patterns**
2. Click **Create index pattern**
3. Enter `job-events-transform-images` as the pattern
4. Click **Next step**
5. Select `timestamp` as the **Time field**
6. Click **Create index pattern**

### Create `job-events` Index Pattern (for cross-job comparison)

Repeat the above steps with pattern `job-events`.

---

## Step 2: Add Scripted Fields

Scripted fields let you compute values from existing fields.

**Note**: These scripted fields work identically in both `job-events` and `job-events-transform-images` indices since they use the same `metrics.*` field paths.

### Navigate to Scripted Fields

1. Go to **Stack Management** > **Index Patterns**
2. Click on the index pattern (either `job-events` or `job-events-transform-images`)
3. Click the **Scripted fields** tab
4. Click **Add scripted field**

### Add `throughput_per_second`

| Setting | Value |
|---------|-------|
| Name | `throughput_per_second` |
| Language | `painless` |
| Type | `number` |
| Format | `Number` (default) |
| Script | See below |

```painless
if (doc['metrics.duration_seconds'].size() > 0 && doc['metrics.duration_seconds'].value > 0) {
  return doc['metrics.records_written'].value / doc['metrics.duration_seconds'].value;
}
return 0;
```

Click **Create field**.

### Add `success_rate_percent`

| Setting | Value |
|---------|-------|
| Name | `success_rate_percent` |
| Language | `painless` |
| Type | `number` |
| Format | `Percent` (or Number) |
| Script | See below |

```painless
if (doc['metrics.records_read'].size() > 0 && doc['metrics.records_read'].value > 0) {
  double rate = (double)doc['metrics.records_written'].value / doc['metrics.records_read'].value;
  return rate * 100;
}
return 0;
```

---

## Step 3: Create Visualizations

### Field Paths (Consistent Across All Indices)

**Both indices use the same natural structure** from `AbstractJobMetrics.get_json()`. This means:
- Scripted fields work identically in both indices
- Visualizations can be reused across indices
- One schema to remember

| Field Path | Description |
|------------|-------------|
| `metrics.duration_seconds` | Total job duration |
| `metrics.records_read` | Records extracted |
| `metrics.records_written` | Records loaded |
| `metrics.records_dropped` | Records dropped |
| `metrics.bytes_written` | Bytes written |
| `metrics.phases.extract.duration_seconds` | Extract phase duration |
| `metrics.phases.transform.duration_seconds` | Transform phase duration |
| `metrics.phases.load.duration_seconds` | Load phase duration |
| `metrics.drop_reasons` | Array of `{reason, count}` |
| `quality.status` | GREEN, YELLOW, RED |
| `quality.checks` | Array of quality check results |
| `error.type` | Error type (if failed) |
| `error.message` | Error message (if failed) |

The only difference between indices:
- **`job-events`**: Excludes `metrics.payload` (job-specific fields)
- **`job-events-transform-images`**: Includes `metrics.payload` with job-specific details

### Navigate to Visualize

1. Click **Visualize** in the left sidebar (or **OpenSearch Dashboards** > **Visualize**)
2. Click **Create visualization**

---

### Visualization 1: Job Duration Over Time (Line Chart)

**Purpose**: Track how long jobs take over time.

1. Click **Create visualization** > **Line**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)**:
1. Click **Y-axis** > **Aggregation**: `Average`
2. **Field**: `metrics.duration_seconds`
3. **Custom label**: `Duration (seconds)`

**Buckets (X-axis)**:
1. Click **Add** > **X-axis**
2. **Aggregation**: `Date Histogram`
3. **Field**: `timestamp`
4. **Minimum interval**: `Auto`

Click **Update** (play button) to preview. Then **Save** as `Job Duration Over Time`.

---

### Visualization 2: Phase Duration Stacked (Area Chart)

**Purpose**: Show extract/transform/load duration as stacked layers.

1. Click **Create visualization** > **Area**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)** - Add three metrics:

First metric:
- **Aggregation**: `Average`
- **Field**: `metrics.phases.extract.duration_seconds`
- **Custom label**: `Extract`

Click **Add** to add second metric:
- **Aggregation**: `Average`
- **Field**: `metrics.phases.transform.duration_seconds`
- **Custom label**: `Transform`

Click **Add** to add third metric:
- **Aggregation**: `Average`
- **Field**: `metrics.phases.load.duration_seconds`
- **Custom label**: `Load`

**Buckets (X-axis)**:
- **Aggregation**: `Date Histogram`
- **Field**: `timestamp`

**Options** (gear icon):
- **Chart type**: `Stacked`

Click **Update** then **Save** as `Phase Duration Stacked`.

---

### Visualization 3: Records Over Time (Line Chart)

**Purpose**: Track records read, written, and dropped.

1. Click **Create visualization** > **Line**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)** - Add three metrics:

- Metric 1: `Sum` of `metrics.records_read`, label: `Records Read`
- Metric 2: `Sum` of `metrics.records_written`, label: `Records Written`
- Metric 3: `Sum` of `metrics.records_dropped`, label: `Records Dropped`

**Buckets (X-axis)**:
- **Aggregation**: `Date Histogram`
- **Field**: `timestamp`

**Save** as `Records Over Time`.

---

### Visualization 4: Latest Job Metrics (Metric)

**Purpose**: Show key metrics from the most recent job run.

1. Click **Create visualization** > **Metric**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- Metric 1: `Top Hit` > **Field**: `metrics.records_written`, **Aggregate with**: `Max`, **Sort on**: `timestamp`, **Order**: `Descending`
  - Custom label: `Records Written`

For multiple metrics in one visualization, you may need to create separate Metric visualizations or use TSVB.

**Alternative using Top Hit**:
- **Aggregation**: `Top Hit`
- **Field**: `metrics.duration_seconds`
- **Aggregate with**: `Concatenate`
- **Size**: `1`
- **Sort on**: `timestamp` (Descending)

**Save** as `Latest Duration`.

---

### Visualization 5: Throughput Over Time (Line Chart)

**Purpose**: Track images processed per second.

1. Click **Create visualization** > **Line**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)**:
- **Aggregation**: `Average`
- **Field**: `throughput_per_second` (scripted field)
- **Custom label**: `Images/Second`

**Buckets (X-axis)**:
- **Aggregation**: `Date Histogram`
- **Field**: `timestamp`

**Save** as `Throughput Over Time`.

---

### Visualization 6: Data Type Distribution (Pie Chart)

**Purpose**: Show proportion of each parser type.

Data is stored in array format: `metrics.payload.transform.data_types` is a nested array with `name`, `records`, and `dropped` fields.

> **Note**: Since `data_types` uses the `nested` type, the standard Pie chart UI doesn't support it directly. Use **Vega** instead.

1. Click **Create visualization** > **Vega**
2. Replace the default spec with the following:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Data Type Distribution",
  "data": {
    "url": {
      "index": "job-events-transform-images",
      "body": {
        "size": 0,
        "aggs": {
          "data_types_nested": {
            "nested": {
              "path": "metrics.payload.transform.data_types"
            },
            "aggs": {
              "by_name": {
                "terms": {
                  "field": "metrics.payload.transform.data_types.name",
                  "size": 20
                },
                "aggs": {
                  "total_records": {
                    "sum": {
                      "field": "metrics.payload.transform.data_types.records"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.data_types_nested.by_name.buckets"}
  },
  "mark": {"type": "arc", "tooltip": true},
  "encoding": {
    "theta": {"field": "total_records.value", "type": "quantitative"},
    "color": {"field": "key", "type": "nominal", "title": "Parser Type"}
  }
}
```

3. Click the **play button** to render
4. **Save** as `Data Type Distribution`

---

### Visualization 7: Category Breakdown (Pie Chart)

**Purpose**: Show nautilus vs savedproject distribution by bytes.

Data is stored in array format: `metrics.payload.load.output_summary` is a nested array with `category`, `bytes`, `file_count`, and `base_path` fields.

> **Note**: Since `output_summary` uses the `nested` type, the standard Pie chart UI doesn't support it directly. Use **Vega** instead.

1. Click **Create visualization** > **Vega**
2. Replace the default spec with the following:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Category Breakdown (Bytes)",
  "data": {
    "url": {
      "index": "job-events-transform-images",
      "body": {
        "size": 0,
        "aggs": {
          "output_summary_nested": {
            "nested": {
              "path": "metrics.payload.load.output_summary"
            },
            "aggs": {
              "by_category": {
                "terms": {
                  "field": "metrics.payload.load.output_summary.category",
                  "size": 10
                },
                "aggs": {
                  "total_bytes": {
                    "sum": {
                      "field": "metrics.payload.load.output_summary.bytes"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.output_summary_nested.by_category.buckets"}
  },
  "mark": {"type": "arc", "tooltip": true},
  "encoding": {
    "theta": {"field": "total_bytes.value", "type": "quantitative"},
    "color": {"field": "key", "type": "nominal", "title": "Category"}
  }
}
```

3. Click the **play button** to render
4. **Save** as `Category Breakdown`

---

### Visualization 8: Job Status Distribution (Pie Chart)

**Purpose**: Show SUCCESS vs PENDING_APPROVAL vs FAILED.

1. Click **Create visualization** > **Pie**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- **Slice size**: `Count`

**Buckets**:
- **Split slices** > **Aggregation**: `Terms`
- **Field**: `status`
- **Order by**: `Count`
- **Size**: `5`

**Save** as `Job Status Distribution`.

---

### Visualization 9: Drop Reasons (Horizontal Bar)

**Purpose**: Show breakdown of why records were dropped.

Data is stored in array format: `metrics.drop_reasons` is a nested array with `reason` and `count` fields.

> **Note**: Since `drop_reasons` uses the `nested` type, the standard Bar chart UI doesn't support it directly. Use **Vega** instead.

1. Click **Create visualization** > **Vega**
2. Replace the default spec with the following:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Drop Reasons",
  "data": {
    "url": {
      "index": "job-events-transform-images",
      "body": {
        "size": 0,
        "aggs": {
          "drop_reasons_nested": {
            "nested": {
              "path": "metrics.drop_reasons"
            },
            "aggs": {
              "by_reason": {
                "terms": {
                  "field": "metrics.drop_reasons.reason",
                  "size": 20
                },
                "aggs": {
                  "total_count": {
                    "sum": {
                      "field": "metrics.drop_reasons.count"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.drop_reasons_nested.by_reason.buckets"}
  },
  "mark": {"type": "bar", "tooltip": true},
  "encoding": {
    "y": {"field": "key", "type": "nominal", "title": "Drop Reason", "sort": "-x"},
    "x": {"field": "total_count.value", "type": "quantitative", "title": "Dropped Records"},
    "color": {"field": "key", "type": "nominal", "legend": null}
  }
}
```

3. Click the **play button** to render
4. **Save** as `Drop Reasons`

---

### Visualization 10: Quality Status Distribution (Pie Chart)

**Purpose**: Show distribution of job quality outcomes (GREEN vs YELLOW vs RED).

Use Vega for proper color control (GREEN/YELLOW/RED):

1. Click **Create visualization** > **Vega**
2. Replace the default spec with:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Quality Status Distribution",
  "data": {
    "url": {
      "index": "job-events-transform-images",
      "body": {
        "size": 0,
        "aggs": {
          "by_status": {
            "terms": {
              "field": "quality.status",
              "size": 5
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.by_status.buckets"}
  },
  "mark": {"type": "arc", "tooltip": true},
  "encoding": {
    "theta": {"field": "doc_count", "type": "quantitative"},
    "color": {
      "field": "key",
      "type": "nominal",
      "title": "Quality Status",
      "scale": {
        "domain": ["GREEN", "YELLOW", "RED"],
        "range": ["#00C853", "#FFD600", "#FF1744"]
      }
    }
  }
}
```

3. Click the **play button** to render
4. **Save** as `Quality Status Distribution`

---

### Visualization 11: Quality Status Over Time (Line Chart)

**Purpose**: Track quality trends over time.

1. Click **Create visualization** > **Line**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)**:
- **Aggregation**: `Count`
- **Custom label**: `Job Count`

**Buckets (X-axis)**:
- **Aggregation**: `Date Histogram`
- **Field**: `timestamp`

**Split Series**:
- Click **Add** > **Split series**
- **Sub-aggregation**: `Terms`
- **Field**: `quality.status`
- **Order by**: `Count`
- **Size**: `5`

**Save** as `Quality Status Over Time`

---

### Visualization 12: Quality Checks Details (Vega)

**Purpose**: Show individual quality check results with values and thresholds.

Since `quality.checks` is a nested array, use Vega:

1. Click **Create visualization** > **Vega**
2. Replace the default spec with:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Quality Checks Summary",
  "data": {
    "url": {
      "index": "job-events-transform-images",
      "body": {
        "size": 0,
        "aggs": {
          "checks_nested": {
            "nested": {
              "path": "quality.checks"
            },
            "aggs": {
              "by_check": {
                "terms": {
                  "field": "quality.checks.name",
                  "size": 20
                },
                "aggs": {
                  "by_status": {
                    "terms": {
                      "field": "quality.checks.status",
                      "size": 5
                    }
                  },
                  "avg_value": {
                    "avg": {
                      "field": "quality.checks.value"
                    }
                  },
                  "avg_threshold": {
                    "avg": {
                      "field": "quality.checks.threshold"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.checks_nested.by_check.buckets"}
  },
  "mark": {"type": "bar", "tooltip": true},
  "encoding": {
    "y": {"field": "key", "type": "nominal", "title": "Quality Check"},
    "x": {"field": "doc_count", "type": "quantitative", "title": "Count"},
    "color": {
      "field": "by_status.buckets[0].key",
      "type": "nominal",
      "title": "Status",
      "scale": {
        "domain": ["GREEN", "YELLOW", "RED"],
        "range": ["#00C853", "#FFD600", "#FF1744"]
      }
    }
  }
}
```

3. Click the **play button** to render
4. **Save** as `Quality Checks Summary`

---

### Visualization 13: Jobs Requiring Attention (Data Table)

**Purpose**: List jobs with YELLOW or RED quality status for review.

1. Click **Create visualization** > **Data Table**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- **Aggregation**: `Count`

**Buckets** (Split rows):
1. First split:
   - **Aggregation**: `Terms`
   - **Field**: `job_run_id`
   - **Size**: `20`
   - **Order by**: `Count`

2. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `quality.status`

3. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `timestamp`

**Filter**: Add a filter at the top:
```
quality.status: YELLOW OR quality.status: RED
```

**Save** as `Jobs Requiring Attention`

---

## Step 4: Create Dashboard

1. Click **Dashboard** in left sidebar
2. Click **Create dashboard**
3. Click **Add** to add visualizations
4. Select each visualization you created
5. Drag and resize panels to match the layout below
6. Click **Save** as `Transform Images Operations`

### Recommended Layout

```
Row 1 (metrics - 4 panels):
+----------------+----------------+----------------+----------------+
| Latest Duration| Records Written| Records Dropped|   Throughput   |
+----------------+----------------+----------------+----------------+

Row 2 (quality overview - 3 panels):
+----------------------+----------------------+----------------------+
| Quality Status Dist. | Job Status Dist.     | Jobs Requiring       |
| (Pie)                | (Pie)                | Attention (Table)    |
+----------------------+----------------------+----------------------+

Row 3 (wide chart):
+------------------------------------------------------------------+
|              Quality Status Over Time                             |
+------------------------------------------------------------------+

Row 4 (wide chart):
+------------------------------------------------------------------+
|              Phase Duration Stacked                               |
+------------------------------------------------------------------+

Row 5 (two charts):
+--------------------------------+---------------------------------+
|       Records Over Time        |    Data Type Distribution       |
+--------------------------------+---------------------------------+

Row 6 (two charts):
+--------------------------------+---------------------------------+
|     Category Breakdown         |     Throughput Over Time        |
+--------------------------------+---------------------------------+

Row 7 (two charts):
+--------------------------------+---------------------------------+
|     Drop Reasons               |    Quality Checks Summary       |
+--------------------------------+---------------------------------+
```

---

## Step 5: Set Time Range

1. In the top-right, click the time picker
2. Select appropriate range:
   - **Quick select**: `Last 7 days` or `Last 30 days`
   - Or set custom **Absolute** range
3. Click **Refresh**

---

## Tips for OpenSearch Dashboards 2.11

### Accessing Nested Array Fields

For nested array fields like `metrics.payload.transform.data_types`:
- Use the dotted path to access fields within the array (e.g., `metrics.payload.transform.data_types.name`)
- For aggregations, you may need to use **Nested** aggregation type
- Refresh the index pattern after new data arrives to discover new fields

### Refreshing Index Pattern

If new fields aren't appearing:
1. Go to **Stack Management** > **Index Patterns**
2. Click your index pattern
3. Click the **Refresh field list** button (circular arrow icon)

### Using TSVB for Complex Visualizations

For nested objects or complex aggregations:
1. **Create visualization** > **TSVB** (Time Series Visual Builder)
2. TSVB allows more flexible field access and multiple index patterns

### Filtering

Add filters to focus on specific data:
1. Click **Add filter** below the search bar
2. Example: `status` `is` `SUCCESS` to show only successful jobs

---

## Schema Reference

Both indices use the **same natural structure** from `AbstractJobMetrics.get_json()`.
The only difference is that `job-events` excludes `metrics.payload`.

### Common Fields (Both Indices)

| Field Path | Type | Description |
|------------|------|-------------|
| `id` | keyword | Unique document ID |
| `timestamp` | date | Event timestamp |
| `event_type` | keyword | Event type (job_completed) |
| `job_name` | keyword | Job name |
| `job_run_id` | keyword | Unique run ID |
| `status` | keyword | SUCCESS, PENDING_APPROVAL, FAILED |
| `failure_type` | keyword | CATASTROPHIC, QUALITY, or null |
| `quality.status` | keyword | GREEN, YELLOW, RED |
| `quality.checks` | nested | Array of quality check results |
| `metrics.duration_seconds` | float | Total job duration |
| `metrics.records_read` | long | Records extracted |
| `metrics.records_written` | long | Records loaded |
| `metrics.records_dropped` | long | Records dropped |
| `metrics.bytes_written` | long | Bytes written |
| `metrics.phases.extract.duration_seconds` | float | Extract phase duration |
| `metrics.phases.transform.duration_seconds` | float | Transform phase duration |
| `metrics.phases.load.duration_seconds` | float | Load phase duration |
| `metrics.drop_reasons` | nested | Array of `{reason, count}` |
| `error.type` | keyword | Error type (if failed) |
| `error.message` | text | Error message (if failed) |

### Job-Specific Payload (Only in `job-events-transform-images`)

These fields are under `metrics.payload` and only exist in job-specific indices:

**`metrics.payload.transform.data_types`** (nested array):
| Field | Type | Description |
|-------|------|-------------|
| `name` | keyword | Parser name (e.g., nautilusbookparser) |
| `records` | long | Records processed by this parser |
| `dropped` | long | Records dropped by this parser |

**`metrics.payload.load.output_summary`** (nested array):
| Field | Type | Description |
|-------|------|-------------|
| `category` | keyword | Output category (nautilus, savedproject) |
| `file_count` | integer | Number of files written |
| `bytes` | long | Total bytes written |
| `base_path` | keyword | Base S3 path |

**`metrics.payload.load.bytes_by_category`** (nested array):
| Field | Type | Description |
|-------|------|-------------|
| `category` | keyword | Output category |
| `bytes` | long | Bytes written to this category |

---

## Migration Notes

### After Deploying Structure Changes

The lambda has been refactored to use consistent field paths across all indices. After deploying:

1. **Delete existing indices** (recommended for clean slate):
   ```
   DELETE job-events
   DELETE job-events-transform-images
   ```

2. **Delete existing index template** (it will be recreated):
   ```
   DELETE _index_template/job-events-template
   ```

3. **The index template will be recreated** automatically on next Lambda invocation

4. **Refresh index patterns** in OpenSearch Dashboards:
   - Go to **Stack Management** > **Index Patterns**
   - Click each index pattern
   - Click **Refresh field list**

5. **Recreate scripted fields** - they now work identically in both indices:
   - `throughput_per_second`
   - `success_rate_percent`

---

## Approval Workflow

Jobs that require human approval (status = `PENDING_APPROVAL`) follow this workflow:

### Architecture

```
Job Completion → SNS (job_events) → job_events_indexer → OpenSearch
                                                           ↓
                                              Dashboard shows PENDING_APPROVAL
                                                           ↓
                                              Human reviews in dashboard
                                                           ↓
Approval System → SNS (job_approvals) → approval_processor → Updates OpenSearch
                                                           ↓
                                              Dashboard shows APPROVED/REJECTED
```

### SNS Topics

| Topic | Purpose |
|-------|---------|
| `job_events` | Receives job completion events from Spark jobs |
| `job_approvals` | Receives human approval decisions |

### Lambdas

| Lambda | Subscribes To | Purpose |
|--------|--------------|---------|
| `job_events_indexer` | `job_events` | Indexes job events to OpenSearch |
| `approval_processor` | `job_approvals` | Updates job documents with approval status |

### Approval Fields

When a job requires approval, these fields are populated after the approval decision:

| Field | Type | Description |
|-------|------|-------------|
| `approval_status` | keyword | APPROVED or REJECTED |
| `approved_by` | keyword | Email or user ID of approver |
| `approval_reason` | text | Explanation for the decision |
| `approval_timestamp` | date | When the decision was made |

### Submitting Approval Decisions

To approve or reject a job, publish a message to the `job_approvals` SNS topic:

```json
{
  "event_type": "approval_decision",
  "job_name": "transform_images",
  "job_run_id": "spark-application-1234567890",
  "timestamp": "2025-12-15T18:00:00Z",
  "decision": "APPROVED",
  "decided_by": "user@example.com",
  "reason": "Quality metrics within acceptable range after manual review"
}
```

### Visualization 14: Pending Approvals (Data Table)

**Purpose**: List all jobs awaiting human approval.

1. Click **Create visualization** > **Data Table**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- **Aggregation**: `Count`

**Buckets** (Split rows):
1. First split:
   - **Aggregation**: `Terms`
   - **Field**: `job_run_id`
   - **Size**: `50`
   - **Order by**: `Custom metric` → `timestamp` (descending)

2. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `timestamp`

3. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `quality.status`

**Filter**: Add a filter at the top:
```
status: PENDING_APPROVAL AND NOT approval_status: *
```

**Save** as `Pending Approvals`

---

### Visualization 15: Approval History (Data Table)

**Purpose**: Show audit trail of all approval decisions.

1. Click **Create visualization** > **Data Table**
2. Select index pattern: `job-approvals`

**Note**: Create a new index pattern for `job-approvals` first:
1. Go to **Stack Management** > **Index Patterns**
2. Create pattern: `job-approvals`
3. Time field: `timestamp`

**Metrics**:
- **Aggregation**: `Count`

**Buckets** (Split rows):
1. First split:
   - **Aggregation**: `Terms`
   - **Field**: `job_run_id`
   - **Size**: `50`

2. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `decision`

3. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `decided_by`

4. Add sub-bucket:
   - **Sub-aggregation**: `Terms`
   - **Field**: `timestamp`

**Save** as `Approval History`

---

### Visualization 16: Approval Rate (Pie Chart)

**Purpose**: Show ratio of approved vs rejected jobs.

1. Click **Create visualization** > **Vega**
2. Replace the default spec with:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Approval Decisions",
  "data": {
    "url": {
      "index": "job-approvals",
      "body": {
        "size": 0,
        "aggs": {
          "by_decision": {
            "terms": {
              "field": "decision",
              "size": 5
            }
          }
        }
      }
    },
    "format": {"property": "aggregations.by_decision.buckets"}
  },
  "mark": {"type": "arc", "tooltip": true},
  "encoding": {
    "theta": {"field": "doc_count", "type": "quantitative"},
    "color": {
      "field": "key",
      "type": "nominal",
      "title": "Decision",
      "scale": {
        "domain": ["APPROVED", "REJECTED"],
        "range": ["#00C853", "#FF1744"]
      }
    }
  }
}
```

3. Click the **play button** to render
4. **Save** as `Approval Rate`

---

### Updated Dashboard Layout

Add a new section for approvals:

```
Row 8 (approval workflow - 3 panels):
+----------------------+----------------------+----------------------+
| Pending Approvals    | Approval History     | Approval Rate        |
| (Table)              | (Table)              | (Pie)                |
+----------------------+----------------------+----------------------+
```

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-15 | Added Approval Workflow section with architecture diagram and visualizations 14-16. |
| 2025-12-15 | Added quality visualizations (10-13) with proper color mapping for GREEN/YELLOW/RED. |
| 2025-12-12 | **BREAKING**: Unified structure - both indices now use same `metrics.*` field paths. |
| 2025-12-12 | Removed flattening in common index - uses natural structure from AbstractJobMetrics. |
| 2025-12-12 | Scripted fields now work identically in both indices. |
| 2025-12-12 | Restructured metrics to use array format for OpenSearch aggregation. |
| 2025-12-12 | `drop_reasons` now array: `[{"reason": "...", "count": N}]` |
| 2025-12-12 | `data_types` now array: `[{"name": "parser", "records": N, "dropped": M}]` |
| 2025-12-12 | `output_summary` now array: `[{"category": "...", "bytes": N, ...}]` |
| 2025-12-12 | Added explicit OpenSearch Dashboards 2.11 setup instructions. |
| 2025-12-12 | Initial documentation. |
