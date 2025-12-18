# Quality & Approval Dashboards - OpenSearch Setup Guide

OpenSearch Dashboards setup guide for quality monitoring and approval workflow tracking.

---

## Prerequisites

1. OpenSearch cluster is running and accessible
2. Job events are being indexed to `job-events-transform-images`
3. Approval events are being indexed to `job-approvals`
4. You have access to OpenSearch Dashboards

---

## Step 1: Create Index Patterns

### Create `job-approvals` Index Pattern

1. Go to **Dashboards Management** > **Index patterns**
2. Click **Create index pattern**
3. Enter `job-approvals` as the pattern
4. Click **Next step**
5. Select `timestamp` as the Time field
6. Click **Create index pattern**

### Verify `job-events-transform-images` Index Pattern

Ensure this index pattern already exists (created in main DASHBOARDS.md setup).

---

## Step 2: Create Approval Visualizations

### Visualization A: Pending Approvals (Data Table)

**Purpose**: List all jobs awaiting human approval.

1. Go to **Visualize** > **Create visualization** > **Data Table**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- Aggregation: `Count`

**Buckets** (Split Rows):

1. First bucket:
   - Aggregation: `Terms`
   - Field: `job_run_id`
   - Size: `50`

2. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `timestamp`
   - Size: `1`

3. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `quality.status`
   - Size: `5`

**Filter** (in search bar at top):
```
status: PENDING_APPROVAL
```

Click **Update** then **Save** as `Pending Approvals`

---

### Visualization B: Approval History (Data Table)

**Purpose**: Show audit trail of all approval decisions.

1. **Create visualization** > **Data Table**
2. Select index pattern: `job-approvals`

**Metrics**:
- Aggregation: `Count`

**Buckets** (Split Rows):

> **Note**: The `job-approvals` index uses dynamic mapping, so string fields have `.keyword` suffix for aggregations.

1. First bucket:
   - Aggregation: `Terms`
   - Field: `job_run_id.keyword`
   - Size: `50`

2. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `decision.keyword`
   - Size: `5`

3. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `decided_by.keyword`
   - Size: `10`

Click **Update** then **Save** as `Approval History`

---

### Visualization C: Approval Rate (Vega Pie Chart)

**Purpose**: Show ratio of approved vs rejected jobs with color coding.

1. **Create visualization** > **Vega**
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
              "field": "decision.keyword",
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

### Visualization D: Approvals Over Time (Line Chart) - OPTIONAL

**Purpose**: Track approval decisions over time.

> **Note**: This visualization is optional. If quality issues are rare, there won't be enough data points to make this chart useful. Consider skipping this visualization.

1. **Create visualization** > **Line**
2. Select index pattern: `job-approvals`

**Metrics (Y-axis)**:
- Aggregation: `Count`
- Custom label: `Decisions`

**Buckets (X-axis)**:
- Aggregation: `Date Histogram`
- Field: `timestamp`
- Minimum interval: `Day`

**Split Series**:
- Click **Add** > **Split series**
- Sub-aggregation: `Terms`
- Field: `decision.keyword`
- Size: `5`

Click **Update** then **Save** as `Approvals Over Time`

---

## Step 3: Create Quality Visualizations

### Visualization E: Quality Status Distribution (Vega Pie Chart)

**Purpose**: Show distribution of job quality outcomes with semantic colors.

1. **Create visualization** > **Vega**
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

### Visualization F: Quality Status Over Time (Line Chart)

**Purpose**: Track quality trends over time.

1. **Create visualization** > **Line**
2. Select index pattern: `job-events-transform-images`

**Metrics (Y-axis)**:
- Aggregation: `Count`
- Custom label: `Job Count`

**Buckets (X-axis)**:
- Aggregation: `Date Histogram`
- Field: `timestamp`
- Minimum interval: `Auto`

**Split Series**:
- Click **Add** > **Split series**
- Sub-aggregation: `Terms`
- Field: `quality.status`
- Size: `5`

Click **Update** then **Save** as `Quality Status Over Time`

---

### Visualization G: Jobs Requiring Attention (Data Table)

**Purpose**: List jobs with YELLOW or RED quality status for review.

1. **Create visualization** > **Data Table**
2. Select index pattern: `job-events-transform-images`

**Metrics**:
- Aggregation: `Count`

**Buckets** (Split Rows):

1. First bucket:
   - Aggregation: `Terms`
   - Field: `job_run_id`
   - Size: `20`

2. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `quality.status`
   - Size: `5`
   - **Advanced** > **Include**: `YELLOW|RED`

3. Add sub-bucket (Split Rows):
   - Aggregation: `Terms`
   - Field: `timestamp`
   - Size: `1`

Click **Update** then **Save** as `Jobs Requiring Attention`

---

### Visualization H: Quality Checks Summary (Vega Bar Chart)

**Purpose**: Show individual quality check results.

1. **Create visualization** > **Vega**
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
    "color": {"field": "key", "type": "nominal", "legend": null}
  }
}
```

3. Click the **play button** to render
4. **Save** as `Quality Checks Summary`

---

## Step 4: Create Approval Dashboard

> **Recommendation**: Since quality issues are expected to be rare, consider adding **Pending Approvals** directly to your main **Transform Images Operations** dashboard instead of creating a separate approval dashboard. This way you see pending items at a glance during normal operations.

### Option A: Add to Main Operations Dashboard (Recommended)

1. Open your existing **Transform Images Operations** dashboard
2. Click **Edit**
3. Click **Add** and select `Pending Approvals`
4. Place it prominently at the top of the dashboard
5. **Save**

### Option B: Create Separate Approval Dashboard

1. Go to **Dashboard** > **Create dashboard**
2. Click **Add** and select these visualizations:
   - Pending Approvals (required)
   - Approval Rate (optional)
   - Approval History (optional)

3. Arrange layout:

```
+-------------------------------------------------------+
|              Pending Approvals (Table)                |
|         Shows jobs needing review - usually empty     |
+---------------------------+---------------------------+
|     Approval Rate (Pie)   |   Approval History        |
|                           |      (audit trail)        |
+---------------------------+---------------------------+
```

4. Click **Save** as `Approval Dashboard`

---

## Step 5: Create Quality Dashboard

1. Go to **Dashboard** > **Create dashboard**
2. Click **Add** and select these visualizations:
   - Quality Status Distribution
   - Quality Status Over Time
   - Jobs Requiring Attention
   - Quality Checks Summary

3. Arrange layout:

```
+---------------------------+---------------------------+
| Quality Status Dist.      | Jobs Requiring Attention  |
|        (Pie)              |        (Table)            |
+---------------------------+---------------------------+
|           Quality Status Over Time (Line)             |
+-------------------------------------------------------+
|           Quality Checks Summary (Bar)                |
+-------------------------------------------------------+
```

4. Click **Save** as `Quality Dashboard`

---

## Approval Workflow Reference

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

### Approval Fields

| Field | Type | Description |
|-------|------|-------------|
| `approval_status` | keyword | APPROVED or REJECTED |
| `approved_by` | keyword | Email or user ID of approver |
| `approval_reason` | text | Explanation for the decision |
| `approval_timestamp` | date | When the decision was made |

---

## Schema Reference

### `job-approvals` Index Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | keyword | Unique document ID |
| `timestamp` | date | When decision was made |
| `event_type` | keyword | Always `approval_decision` |
| `job_name` | keyword | Job name |
| `job_run_id` | keyword | Job run ID being approved |
| `decision` | keyword | APPROVED or REJECTED |
| `decided_by` | keyword | Approver email/ID |
| `reason` | text | Explanation for decision |

### Quality Fields (in `job-events-transform-images`)

| Field | Type | Description |
|-------|------|-------------|
| `quality.status` | keyword | GREEN, YELLOW, RED |
| `quality.checks` | nested | Array of check results |
| `quality.checks.name` | keyword | Check name (e.g., drop_rate) |
| `quality.checks.status` | keyword | GREEN, YELLOW, RED |
| `quality.checks.value` | float | Actual value |
| `quality.checks.threshold` | float | Threshold value |
| `quality.checks.message` | text | Optional message |

---

## Tips

### Using `.keyword` Fields

OpenSearch creates two versions of string fields:
- `field_name` (text) - for full-text search
- `field_name.keyword` (keyword) - for exact matching and aggregations

**When to use `.keyword`**:
- Terms aggregations in visualizations
- Sorting
- Exact match filters

**Indices with explicit mappings** (like `job-events-transform-images`) define fields as `keyword` type directly, so no `.keyword` suffix needed.

**Indices with dynamic mappings** (like `job-approvals`) require `.keyword` suffix for string field aggregations.

---

### Formatting Numbers

To reduce decimal places in metrics:

1. Go to **Dashboards Management** > **Index patterns**
2. Click on your index pattern
3. Find the numeric field
4. Click the pencil icon to edit
5. Set **Format**: `Number`
6. Set **Numeral.js format pattern**: `0,0.0` (1 decimal)

Common patterns:
- `0,0` - no decimals
- `0,0.0` - 1 decimal
- `0,0.00` - 2 decimals

### Filtering Data Tables

To show only specific values in a Terms bucket:

1. Click on the bucket to expand settings
2. Click **Advanced** to expand
3. Use **Include**: `VALUE1|VALUE2` (regex pattern)
4. Or use **Exclude**: `VALUE_TO_HIDE`

### Refreshing Index Patterns

If new fields don't appear:

1. Go to **Dashboards Management** > **Index patterns**
2. Click your index pattern
3. Click the **Refresh field list** button

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-15 | Simplified approval dashboard - marked Visualization D as optional since quality issues are rare. |
| 2025-12-15 | Added recommendation to add Pending Approvals to main Operations dashboard. |
| 2025-12-15 | Fixed `job-approvals` fields to use `.keyword` suffix for aggregations. |
| 2025-12-15 | Added tip explaining when to use `.keyword` fields. |
| 2025-12-15 | Initial documentation for Quality and Approval dashboards. |
