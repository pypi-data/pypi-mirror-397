# OpenSearch Integration Guide

## Overview

This guide shows how to integrate OpenSearch metrics publishing into your existing jobs. The integration publishes job metrics to EventBridge, which triggers a Lambda function that indexes the data into OpenSearch for real-time monitoring.

## Quick Start

### 1. Update Job to Publish Metrics

Add metrics publishing to your `AbstractJob.run()` method or individual job implementations:

```python
from dwh.services.metrics_publisher import create_metrics_publisher

class TransformImagesJob(AbstractJob):

    def __init__(self, ...):
        # ... existing init code ...

        # Add metrics publisher
        self.metrics_publisher = create_metrics_publisher(
            region='us-west-1',
            enabled=True  # Set False to disable publishing
        )

    def execute_job(self, **kwargs) -> Any:
        metrics = JobMetrics()

        try:
            # ... existing job logic ...

            metrics.complete()

            # Publish metrics to EventBridge/OpenSearch
            self.metrics_publisher.publish_metrics(
                job_name='transform_images',
                job_run_id=self._get_job_run_id(),
                metrics=metrics.get_json()
            )

            return metrics.get_json()

        except Exception as e:
            # Publish failure event
            self.metrics_publisher.publish_job_completion(
                job_name='transform_images',
                job_run_id=self._get_job_run_id(),
                status='FAILED',
                error_message=str(e)
            )
            raise

    def _get_job_run_id(self) -> str:
        """Get unique job run ID from Glue context or generate one."""
        try:
            # In Glue environment
            from awsglue.utils import getResolvedOptions
            args = getResolvedOptions(sys.argv, ['JOB_RUN_ID'])
            return args['JOB_RUN_ID']
        except:
            # Fallback for local/testing
            import uuid
            return str(uuid.uuid4())
```

### 2. Test Locally with No-Op Publisher

For local development and testing:

```python
from dwh.services.metrics_publisher import create_metrics_publisher

# Use no-op publisher (just logs, doesn't publish)
publisher = create_metrics_publisher(use_noop=True)

# Metrics will be logged but not sent to EventBridge
publisher.publish_metrics(
    job_name='test_job',
    job_run_id='local-test-123',
    metrics={'duration': 10.5, 'records': 1000}
)
```

### 3. Enable in Production

Set environment variable or configuration:

```python
# In job factory or configuration
METRICS_ENABLED = os.environ.get('PUBLISH_METRICS', 'true').lower() == 'true'

publisher = create_metrics_publisher(
    region='us-west-1',
    enabled=METRICS_ENABLED
)
```

## Integration Patterns

### Pattern 1: Centralized in AbstractJob

Add metrics publishing to the base `AbstractJob` class so all jobs inherit it:

```python
# src/dwh/jobs/abstract_job.py

from dwh.services.metrics_publisher import create_metrics_publisher

class AbstractJob(ABC):

    def __init__(self):
        self.metrics_publisher = create_metrics_publisher(
            region=os.environ.get('AWS_REGION', 'us-west-1'),
            enabled=os.environ.get('PUBLISH_METRICS', 'true').lower() == 'true'
        )

    def run(self, **kwargs) -> Any:
        job_run_id = self._get_job_run_id()

        try:
            results = self.execute_job(**kwargs)

            # Publish metrics if results is a metrics dict
            if isinstance(results, dict) and 'job_name' in results:
                self.metrics_publisher.publish_metrics(
                    job_name=results.get('job_name', self.__class__.__name__),
                    job_run_id=job_run_id,
                    metrics=results
                )

            self.on_success(results)
            return results

        except Exception as e:
            error_message = str(e)

            # Publish failure event
            self.metrics_publisher.publish_job_completion(
                job_name=self.__class__.__name__,
                job_run_id=job_run_id,
                status='FAILED',
                error_message=error_message
            )

            self.on_failure(error_message)
            raise RuntimeError(f"Job execution failed: {error_message}") from e
```

### Pattern 2: Job-Specific Publishing

Publish metrics only from specific jobs:

```python
class TransformImagesJob(AbstractJob):

    def execute_job(self, **kwargs) -> Any:
        metrics = JobMetrics()

        # ... job execution ...

        metrics.complete()
        metrics_dict = metrics.get_json()

        # Enrich with job-specific metadata
        metrics_dict['job_name'] = 'transform_images'
        metrics_dict['environment'] = os.environ.get('ENVIRONMENT', 'dev')
        metrics_dict['version'] = os.environ.get('JOB_VERSION', '0.3.0')

        # Publish to OpenSearch
        publisher = create_metrics_publisher()
        publisher.publish_metrics(
            job_name='transform_images',
            job_run_id=self._get_job_run_id(),
            metrics=metrics_dict
        )

        return metrics_dict
```

### Pattern 3: Conditional Publishing

Publish only when certain conditions are met:

```python
def execute_job(self, **kwargs) -> Any:
    metrics = JobMetrics()

    # ... job execution ...

    metrics.complete()

    # Only publish if job took > 60 seconds OR had drops > 100
    should_publish = (
        metrics.get_duration_seconds() > 60 or
        sum(metrics.drop_reasons.values()) > 100
    )

    if should_publish:
        publisher = create_metrics_publisher()
        publisher.publish_metrics(
            job_name='transform_images',
            job_run_id=self._get_job_run_id(),
            metrics=metrics.get_json()
        )

    return metrics.get_json()
```

## Testing

### Unit Tests

```python
from dwh.services.metrics_publisher import NoOpMetricsPublisher

class TestTransformImagesJob(unittest.TestCase):

    def setUp(self):
        # Use NoOp publisher in tests
        self.job = TransformImagesJob(...)
        self.job.metrics_publisher = NoOpMetricsPublisher()

    def test_job_execution(self):
        result = self.job.execute_job(...)

        # Metrics are logged but not published
        self.assertIsNotNone(result)
```

### Functional Tests

```python
# Use real publisher but disable it
publisher = create_metrics_publisher(enabled=False)

# Or use NoOp
publisher = create_metrics_publisher(use_noop=True)
```

## Monitoring Published Metrics

### Check EventBridge Events

```bash
# List recent events
aws events list-rules --name-prefix sfly-aws-dwh-sandbox-jc-poc

# Test event publishing
aws events put-events --entries '[{
  "Source": "dwh.pipeline",
  "DetailType": "Job Metrics",
  "Detail": "{\"job_name\":\"test\",\"job_run_id\":\"123\"}"
}]'
```

### Check Lambda Logs

```bash
# Tail Lambda logs
aws logs tail /aws/lambda/sfly-aws-dwh-sandbox-jc-poc-job-metrics-processor --follow

# Search for specific job
aws logs filter-log-events \
  --log-group-name /aws/lambda/sfly-aws-dwh-sandbox-jc-poc-job-metrics-processor \
  --filter-pattern "transform_images"
```

### Query OpenSearch

```bash
# Check if index exists
curl -XGET "https://<opensearch-endpoint>/_cat/indices/job-metrics*" \
  -u admin:password

# Query recent metrics
curl -XGET "https://<opensearch-endpoint>/job-metrics/_search?pretty" \
  -u admin:password \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "filter": [
          {"range": {"timestamp": {"gte": "now-1h"}}},
          {"term": {"event_type": "custom_metrics"}}
        ]
      }
    },
    "size": 10,
    "sort": [{"timestamp": "desc"}]
  }'
```

## Troubleshooting

### Metrics Not Appearing in OpenSearch

1. **Check EventBridge rule is enabled**:
   ```bash
   aws events describe-rule --name sfly-aws-dwh-sandbox-jc-poc-custom-job-metrics
   ```

2. **Verify Lambda was invoked**:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Lambda \
     --metric-name Invocations \
     --dimensions Name=FunctionName,Value=sfly-aws-dwh-sandbox-jc-poc-job-metrics-processor \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Sum
   ```

3. **Check Lambda errors**:
   ```bash
   aws logs filter-log-events \
     --log-group-name /aws/lambda/sfly-aws-dwh-sandbox-jc-poc-job-metrics-processor \
     --filter-pattern "ERROR"
   ```

### IAM Permission Issues

If Lambda can't write to OpenSearch, check:

```bash
# Verify Lambda role has OpenSearch policy
aws iam list-attached-role-policies \
  --role-name sfly-aws-dwh-sandbox-jc-poc-lambda-job-metrics-role

# Check inline policies
aws iam list-role-policies \
  --role-name sfly-aws-dwh-sandbox-jc-poc-lambda-job-metrics-role
```

### Network/VPC Issues

If Lambda can't reach OpenSearch:

```bash
# Check security groups
aws ec2 describe-security-groups \
  --group-ids <lambda-sg-id> <opensearch-sg-id>

# Verify subnet connectivity
aws ec2 describe-subnets --subnet-ids <subnet-id>
```

## Best Practices

1. **Enrich Metrics**: Add contextual data like environment, version, user
2. **Handle Failures Gracefully**: Don't fail jobs if metrics publishing fails
3. **Use Async**: Consider using SQS queue for metrics if high volume
4. **Minimize Size**: Keep metrics under 256KB (EventBridge limit)
5. **Use Sampling**: For high-frequency jobs, consider sampling (e.g., 1 in 10)
6. **Add Tagging**: Include tags for cost attribution and filtering

## Example: Complete Integration

```python
# src/dwh/jobs/transform_images/transform_images_job.py

import os
import sys
from typing import Any
from dwh.jobs.abstract_job import AbstractJob
from dwh.services.metrics_publisher import create_metrics_publisher
from dwh.jobs.transform_images.metrics.job_metrics import JobMetrics


class TransformImagesJob(AbstractJob):

    def __init__(self, ...):
        super().__init__(...)

        # Initialize metrics publisher
        self.metrics_publisher = create_metrics_publisher(
            region=os.environ.get('AWS_REGION', 'us-west-1'),
            enabled=os.environ.get('PUBLISH_METRICS', 'true').lower() == 'true'
        )

    def execute_job(self, **kwargs) -> Any:
        metrics = JobMetrics()
        job_run_id = self._get_job_run_id()

        try:
            # Execute job phases
            raw_df, extract_dropped_df = self.extract.extract(...)
            transformed_df, transform_dropped_df = self.image_transformer.transform(...)
            self.image_loader.load(...)

            # Capture metrics
            metrics.complete()

            # Publish to OpenSearch
            try:
                self.metrics_publisher.publish_metrics(
                    job_name='transform_images',
                    job_run_id=job_run_id,
                    metrics=metrics.get_json()
                )
            except Exception as e:
                # Log but don't fail job
                print(f"Warning: Failed to publish metrics: {e}")

            return metrics.get_json()

        except Exception as e:
            # Publish failure event
            try:
                self.metrics_publisher.publish_job_completion(
                    job_name='transform_images',
                    job_run_id=job_run_id,
                    status='FAILED',
                    error_message=str(e)
                )
            except:
                pass  # Don't fail on metrics publishing failure

            raise

    def _get_job_run_id(self) -> str:
        """Get job run ID from Glue or generate UUID."""
        try:
            from awsglue.utils import getResolvedOptions
            args = getResolvedOptions(sys.argv, ['JOB_RUN_ID'])
            return args['JOB_RUN_ID']
        except:
            import uuid
            return str(uuid.uuid4())
```

## Next Steps

1. Deploy Terraform infrastructure - `terraform apply` will automatically build and deploy the Lambda function (see `terraform/README_OPENSEARCH.md`)
2. Update jobs to publish metrics (use patterns above)
3. Create OpenSearch dashboards for visualization
4. Set up alerts for critical metrics (drop rate, duration, errors)
