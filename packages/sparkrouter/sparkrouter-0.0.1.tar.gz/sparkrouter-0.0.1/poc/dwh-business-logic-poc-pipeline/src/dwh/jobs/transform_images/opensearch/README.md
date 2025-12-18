# OpenSearch Dashboard Export

This directory contains exported OpenSearch Dashboards saved objects for the `transform_images` job monitoring dashboard.

## Contents

The `export.ndjson` file contains:

### Index Patterns (2)
- `job-metrics` - Common metrics index for cross-job analysis
- `job-metrics-transform-images` - Job-specific index with full payload details

Both use `data_start_datetime` as the time field.

### Scripted Fields (included in index patterns)
- `throughput_per_second` - Calculated as `records_written / duration_seconds`
- `success_rate_percent` - Calculated as `(records_written / records_read) * 100`

### Visualizations (12)
| Visualization | Type | Description |
|--------------|------|-------------|
| Images Extracted - Volume Trends | Line | Records read over time |
| Images Loaded - Volume Trends | Line | Records written over time |
| Images Dropped - Data Quality Issues | Area | Dropped records over time |
| Processing Throughput - Images per Second | Line | Throughput trend |
| Processing Success Rate | Line | Success rate trend |
| Job Performance - Duration Over Time | Line | Job duration trend |
| Total Images Processed | Metric | Latest run - records written |
| Total Images Dropped | Metric | Latest run - records dropped |
| Latest Duration | Metric | Latest run - duration |
| Average Duration | Metric | Average duration (configurable N runs) |
| Success Rate | Metric | Latest run - success rate % |

### Dashboard (1)
- `Images Dashboard` - Combined dashboard with all visualizations

## Restoring to a Fresh OpenSearch Instance

### Prerequisites

1. OpenSearch domain is running and accessible
2. The `job-metrics-transform-images` index exists with data (run the job at least once)
3. You have the OpenSearch Dashboards endpoint URL
4. You have admin credentials

### Option 1: Import via UI

1. Log into OpenSearch Dashboards
   - URL: Your OpenSearch Dashboards endpoint (e.g., `https://<domain>/_dashboards`)
   - Credentials: admin / your-password

2. Navigate to Saved Objects:
   - Click hamburger menu (☰)
   - **Management** → **Dashboards Management** → **Saved Objects**

3. Import:
   - Click **Import**
   - Select `export.ndjson` file
   - Choose import options:
     - **Check for existing objects**: Recommended to avoid duplicates
     - **Automatically overwrite conflicts**: Optional
   - Click **Import**

4. Verify:
   - Go to **Dashboard** → Open **Images Dashboard**
   - Set time range to cover your data dates
   - Confirm visualizations display data

### Option 2: Import via API (curl)

```bash
# Set your OpenSearch endpoint and credentials
OPENSEARCH_ENDPOINT="https://your-opensearch-domain/_dashboards"
USERNAME="admin"
PASSWORD="your-password"

# Import saved objects
curl -X POST "${OPENSEARCH_ENDPOINT}/api/saved_objects/_import?overwrite=true" \
  -H "osd-xsrf: true" \
  -u "${USERNAME}:${PASSWORD}" \
  --form file=@export.ndjson
```

### Option 3: Import via Terraform

Add to your Terraform configuration:

```hcl
resource "null_resource" "import_opensearch_dashboards" {
  depends_on = [aws_opensearch_domain.main]

  provisioner "local-exec" {
    command = <<-EOT
      curl -X POST "https://${aws_opensearch_domain.main.endpoint}/_dashboards/api/saved_objects/_import?overwrite=true" \
        -H "osd-xsrf: true" \
        -u "admin:${var.opensearch_master_password}" \
        --form file=@${path.module}/../../../src/dwh/jobs/transform_images/opensearch/export.ndjson
    EOT
  }

  triggers = {
    # Re-import when export file changes
    export_hash = filemd5("${path.module}/../../../src/dwh/jobs/transform_images/opensearch/export.ndjson")
  }
}
```

## Troubleshooting

### "Index pattern not found" after import

The index pattern references specific index names. Ensure your indices exist:

```bash
# Check indices exist
curl -X GET "https://<endpoint>/job-metrics-transform-images/_search?size=1"
```

If indices don't exist, run the transform_images job to populate data.

### Visualizations show "No data"

1. Check the time range in the top-right picker - ensure it covers your data dates
2. Verify data exists in the index:
   ```json
   GET job-metrics-transform-images/_search
   {
     "size": 1,
     "sort": [{"data_start_datetime": "desc"}]
   }
   ```

### Scripted fields not working

Scripted fields are included in the index pattern export. If they're missing:

1. Go to **Management** → **Index Patterns** → `job-metrics-transform-images`
2. Click **Scripted fields** tab
3. Verify `throughput_per_second` and `success_rate_percent` exist
4. If missing, re-import or manually add them (see main visualization guide)

## Updating the Export

After making changes to dashboards/visualizations:

1. Go to **Management** → **Dashboards Management** → **Saved Objects**
2. Select all objects to export:
   - Both index patterns
   - All visualizations
   - The dashboard
3. Click **Export**
4. Replace `export.ndjson` with the downloaded file
5. Commit to version control

## Related Documentation

- [OpenSearch Visualization Guide](../../../../dwh-business-logic-poc-infra/infra/OPENSEARCH_VISUALIZATION_GUIDE.md) - Detailed guide for creating visualizations
- [Lambda Metrics Processor](../../../../lambda/job_metrics_processor.py) - Lambda that indexes job metrics
