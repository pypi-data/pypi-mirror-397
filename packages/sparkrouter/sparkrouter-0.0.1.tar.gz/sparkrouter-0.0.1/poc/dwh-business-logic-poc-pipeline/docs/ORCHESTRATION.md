# Job Orchestration

This document describes the downstream job orchestration system for triggering jobs after upstream job completion.

## Architecture

```
Job Completes (SUCCESS)
        ↓
SNS (job_events) ──filter: status=SUCCESS──→ downstream_orchestrator Lambda
        ↓                                              ↓
        ↓                                    Reads workflow_config.json from S3
        ↓                                              ↓
        ↓                                    Triggers downstream jobs
        ↓
Job Requires Approval (PENDING_APPROVAL)
        ↓
Human Approves
        ↓
SNS (job_approvals) ──filter: decision=APPROVED──→ downstream_orchestrator Lambda
                                                           ↓
                                                  Triggers downstream jobs
```

## Configuration

Workflow configuration is stored in S3 as a JSON file. This allows:
- Version control alongside code
- Easy updates without redeploying lambdas
- Environment-specific configurations

### Configuration Location

Set the `workflow_config_s3_uri` terraform variable:

```hcl
workflow_config_s3_uri = "s3://your-bucket/config/workflow_config.json"
```

Or set the `WORKFLOW_CONFIG_S3_URI` environment variable on the lambda directly.

### Configuration Schema

```json
{
  "workflows": {
    "job_name": {
      "description": "Human-readable description",
      "on_success": [
        { /* trigger config */ },
        { /* trigger config */ }
      ],
      "on_approval": [
        { /* trigger config - used when job is approved after quality failure */ }
      ]
    }
  }
}
```

### Trigger Types

#### Glue Job

```json
{
  "type": "glue_job",
  "job_name": "my-downstream-job",
  "description": "Optional description",
  "arguments": {
    "--custom_arg": "value",
    "--source_path": "${artifacts.output_path}"
  }
}
```

**Automatic arguments added:**
- `--triggered_by_job`: Name of upstream job
- `--triggered_by_run_id`: Run ID of upstream job
- `--source_artifacts`: JSON of artifacts from upstream job

#### Step Function

```json
{
  "type": "step_function",
  "arn": "arn:aws:states:us-west-1:123456789:stateMachine:my-workflow",
  "description": "Optional description"
}
```

**Input passed to state machine:**
```json
{
  "triggered_by_job": "upstream_job_name",
  "triggered_by_run_id": "spark-application-xxx",
  "source_event": { /* full job event */ }
}
```

#### EventBridge

```json
{
  "type": "eventbridge",
  "event_bus": "default",
  "detail_type": "JobComplete",
  "source": "dwh.orchestrator",
  "description": "Optional description"
}
```

**Event detail:**
```json
{
  "triggered_by_job": "upstream_job_name",
  "triggered_by_run_id": "spark-application-xxx",
  "source_event": { /* full job event */ }
}
```

#### MWAA DAG (Apache Airflow)

```json
{
  "type": "mwaa_dag",
  "environment_name": "my-mwaa-environment",
  "region": "us-west-2",
  "dag_id": "my_downstream_dag",
  "conf": {
    "custom_param": "value"
  },
  "parameter_mapping": {
    "start_date": "start_date",
    "end_date": "end_date",
    "created_by": "created_by",
    "output_path": "artifacts.output_path"
  },
  "description": "Optional description"
}
```

**Parameter Mapping:** Use `parameter_mapping` to map event fields to DAG parameters. The key is the DAG parameter name, and the value is a dot-notation path into the source event.

Examples:
- `"start_date": "start_date"` - maps top-level `start_date` field
- `"output_path": "artifacts.output_path"` - maps nested field from artifacts
- `"record_count": "metrics.records_written"` - maps field from metrics

**DAG configuration passed:**
```json
{
  "triggered_by_job": "upstream_job_name",
  "triggered_by_run_id": "spark-application-xxx",
  "start_date": "2025-11-24T01:00Z",
  "end_date": "2025-11-24T01:15Z",
  "created_by": "jclark",
  "output_path": "s3://bucket/output/path",
  "source_artifacts": { /* artifacts from upstream job */ },
  "source_metrics": {
    "records_read": 1000000,
    "records_written": 999000,
    "records_dropped": 1000
  },
  "custom_param": "value"
}
```

**In your Airflow DAG**, access this configuration via:
```python
from airflow.models import DagRun

def my_task(**context):
    dag_run: DagRun = context['dag_run']
    conf = dag_run.conf

    triggered_by = conf.get('triggered_by_job')
    artifacts = conf.get('source_artifacts', {})
    metrics = conf.get('source_metrics', {})
```

#### MWAA via SQS (Recommended for Private Networking)

For MWAA environments with private networking, use `sqs_mwaa` instead of `mwaa_dag`.
This publishes a structured message to SQS, which the `event_dispatcher` DAG polls.

```json
{
  "type": "sqs_mwaa",
  "dag_id": "my_downstream_dag",
  "queue_url": "https://sqs.us-west-1.amazonaws.com/123456789/my-queue",
  "conf": {
    "custom_param": "value"
  },
  "parameter_mapping": {
    "start_date": "start_date",
    "end_date": "end_date",
    "created_by": "created_by"
  }
}
```

**Note:** `queue_url` is optional if the `MWAA_TRIGGER_QUEUE_URL` environment variable is set on the orchestrator lambda.

**Architecture:**
```
Job SUCCESS -> SNS -> Lambda Orchestrator -> SQS -> event_dispatcher DAG -> Target DAG
                           ↓
                   workflow_config.json
                   (dag_id + parameter_mapping)
```

**SQS Message Format:**
```json
{
  "dag_id": "filter_image_glue_pyspark",
  "conf": {
    "triggered_by_job": "transform_images",
    "triggered_by_run_id": "spark-xxx",
    "start_date": "2025-01-01",
    "end_date": "2025-01-02",
    "created_by": "jclark"
  }
}
```

**Setup Requirements:**
1. Create SQS queue in infra (see `terraform/sqs_mwaa_triggers.tf.infra`)
2. Add SQS permissions to MWAA execution role (see `terraform/iam_mwaa_sqs.tf.infra`)
3. Deploy `event_dispatcher.py` DAG to MWAA
4. Set Airflow Variable `mwaa_trigger_queue_url` to the queue URL
5. Set terraform variable `mwaa_trigger_queue_url` (or lambda env var)

**In your Airflow DAG**, the configuration is passed via `dag_run.conf`:
```python
def my_task(**context):
    conf = context['dag_run'].conf
    start_date = conf.get('start_date')
    triggered_by = conf.get('triggered_by_job')
```

## Example Configuration

```json
{
  "workflows": {
    "transform_images": {
      "description": "Image transformation pipeline",
      "on_success": [
        {
          "type": "glue_job",
          "job_name": "load_images_to_redshift",
          "description": "Load transformed images to Redshift"
        }
      ],
      "on_approval": [
        {
          "type": "glue_job",
          "job_name": "load_images_to_redshift",
          "description": "Load approved images to Redshift",
          "arguments": {
            "--approval_required": "true"
          }
        }
      ]
    },

    "load_promos": {
      "description": "Promotions load pipeline",
      "on_success": [
        {
          "type": "eventbridge",
          "event_bus": "default",
          "detail_type": "PromoLoadComplete",
          "source": "dwh.load_promos"
        }
      ]
    }
  }
}
```

## Deployment

The `deploy.sh` script automatically uploads orchestration configs to S3. Terraform automatically constructs the S3 URI based on the same pattern.

### Deployment Steps

1. **Edit** `orchestration/workflow_config.json`

2. **Run deploy:**
   ```bash
   ./deploy.sh --account=sandbox --env=jc
   ```

   This uploads configs to: `s3://{CODE_BUCKET}/code/{VERSION}/orchestration/workflow_config.json`

3. **Apply terraform** with matching version:
   ```bash
   cd terraform
   terraform apply -var="code_version=0.3.0"
   ```

   Terraform automatically constructs the S3 URI:
   ```
   s3://sfly-aws-dwh-sandbox-{env}-code-{region}/code/{version}/orchestration/workflow_config.json
   ```

### Manual Upload

If you need to update config without a full deploy:

```bash
aws s3 cp orchestration/workflow_config.json s3://sfly-aws-dwh-sandbox-jc-code-us-west-1/code/0.3.0/orchestration/workflow_config.json
```

## Updating Configuration

To update workflow configuration without redeploying lambdas:

1. Edit `orchestration/workflow_config.json`
2. Upload to S3:
   ```bash
   aws s3 sync orchestration s3://your-bucket/code/VERSION/orchestration/
   ```

The lambda reads the config on each invocation, so changes take effect immediately.

## Monitoring

### CloudWatch Logs

Each lambda has a log group:
- `/aws/lambda/{prefix}-downstream-orchestrator`

### What Gets Logged

- Received event
- Config source (S3, SSM, or default)
- Each triggered downstream job
- Any errors during triggering

### Example Log Output

```
Received event: {"Records": [...]}
SNS Message: {"event_type": "job_completed", "job_name": "transform_images", ...}
Loaded workflow config from S3: s3://bucket/config/workflow_config.json
Triggered: {"type": "glue_job", "job_name": "load_images_to_redshift", "run_id": "jr_xxx"}
```

## Error Handling

- If config fails to load from S3, falls back to SSM Parameter Store
- If SSM fails, falls back to hardcoded default (empty)
- Individual trigger failures don't stop other triggers
- All errors are logged and included in response

## IAM Permissions

The lambda role needs permissions for:
- `s3:GetObject` on config bucket
- `glue:StartJobRun` for Glue triggers
- `states:StartExecution` for Step Function triggers
- `events:PutEvents` for EventBridge triggers
- `airflow:CreateWebLoginToken` for MWAA triggers

See `terraform/iam_lambda_events.tf` for the full IAM policy.

## Testing

### Direct Lambda Invocation

```bash
aws lambda invoke \
  --function-name {prefix}-downstream-orchestrator \
  --payload '{
    "event_type": "job_completed",
    "job_name": "transform_images",
    "job_run_id": "test-run-001",
    "status": "SUCCESS"
  }' \
  response.json
```

### Check Logs

```bash
aws logs tail /aws/lambda/{prefix}-downstream-orchestrator --follow
```
