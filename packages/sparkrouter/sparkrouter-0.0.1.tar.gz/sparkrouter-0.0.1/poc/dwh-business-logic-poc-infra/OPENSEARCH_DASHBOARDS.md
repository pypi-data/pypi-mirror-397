# OpenSearch Dashboards - Visualizing Job Metrics

## Access Dashboard

```bash
cd infra/
terraform output opensearch_dashboard_endpoint
```

Login with username: `admin`, password: from `infra/local.tf`

## Create Index Pattern

First time only - tell OpenSearch Dashboards about your index:

1. Click hamburger menu (☰) → **Management** → **Dashboards Management** → **Index patterns**
2. Click **Create index pattern**
3. Enter: `job-metrics*`
4. Click **Next step**
5. Select time field: `@timestamp` (or `job_start_time`)
6. Click **Create index pattern**

## View Raw Data

1. Click hamburger menu (☰) → **Discover**
2. Select `job-metrics*` from dropdown (top left)
3. Adjust time range (top right) to see your data
4. Expand individual documents to see all fields

## Create Visualizations

### Example: Job Success Rate Over Time

1. Click hamburger menu (☰) → **Visualize** → **Create visualization**
2. Select **Area** or **Line**
3. Select `job-metrics*` index
4. Configure:
   - **Y-axis**: Count
   - **X-axis**: Date Histogram on `@timestamp`
   - **Split series**: Terms on `job_status.keyword` (shows success/failure)
5. Click **▶ Update**
6. Save with meaningful name

### Example: Job Duration by Job Name

1. Create visualization → **Horizontal Bar**
2. Select `job-metrics*` index
3. Configure:
   - **Y-axis**: Average of `duration_seconds`
   - **X-axis**: Terms on `job_name.keyword`
4. Click **▶ Update**
5. Save

### Example: Records Processed Over Time

1. Create visualization → **Line**
2. Select `job-metrics*` index
3. Configure:
   - **Y-axis**: Sum of `extract.records_read` (or other metrics)
   - **X-axis**: Date Histogram on `@timestamp`
   - **Split series**: Terms on `job_name.keyword`
4. Save

## Create Dashboard

1. Click hamburger menu (☰) → **Dashboard** → **Create dashboard**
2. Click **Add** → select saved visualizations
3. Arrange and resize panels
4. Click **Save** → give dashboard a name

## Useful Queries

In **Discover**, use the search bar:

```
# Show only failed jobs
job_status: "FAILED"

# Show specific job
job_name: "transform_images"

# Show jobs that processed > 1000 records
extract.records_read: >1000

# Combine filters
job_name: "transform_images" AND job_status: "SUCCESS"
```

## Tips

- Use **Auto-refresh** (top right) to see live updates
- Create **saved searches** for common queries
- Use **filters** instead of queries for easier visualization setup
- Export dashboards via **Management** → **Saved Objects** for backup
