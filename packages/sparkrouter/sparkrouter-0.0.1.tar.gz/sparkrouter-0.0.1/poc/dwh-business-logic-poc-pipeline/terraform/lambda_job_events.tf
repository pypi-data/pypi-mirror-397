# Lambda functions for job event processing
#
# Three lambdas handle different aspects of the event-driven architecture:
# 1. job_events_indexer - Index all events to OpenSearch
# 2. approval_processor - Handle human approval decisions
# 3. downstream_orchestrator - Trigger next jobs on SUCCESS/APPROVED

# =============================================================================
# Shared build configuration
# =============================================================================

locals {
  lambda_dir       = "${path.module}/../lambda"
  lambda_layer_dir = "${path.module}/../lambda/layer"
}

# =============================================================================
# Lambda Layer for Shared Dependencies
# =============================================================================

# Build the layer with dependencies (only when requirements.txt changes)
resource "null_resource" "lambda_layer_build" {
  triggers = {
    requirements = filemd5("${local.lambda_dir}/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      rm -rf ${local.lambda_layer_dir}
      mkdir -p ${local.lambda_layer_dir}/python
      pip install -r ${local.lambda_dir}/requirements.txt -t ${local.lambda_layer_dir}/python --quiet
    EOT
    interpreter = ["bash", "-c"]
  }
}

data "archive_file" "lambda_layer" {
  type        = "zip"
  source_dir  = local.lambda_layer_dir
  output_path = "${local.lambda_dir}/lambda_layer.zip"

  depends_on = [null_resource.lambda_layer_build]
}

resource "aws_lambda_layer_version" "opensearch_deps" {
  filename            = data.archive_file.lambda_layer.output_path
  layer_name          = "${local.resource_prefix}-opensearch-deps"
  source_code_hash    = data.archive_file.lambda_layer.output_base64sha256
  compatible_runtimes = ["python3.11"]

  description = "Shared dependencies for job event Lambda functions (opensearch-py, requests-aws4auth)"
}

# =============================================================================
# 1. Job Events Indexer
# =============================================================================

data "archive_file" "job_events_indexer" {
  type        = "zip"
  source_file = "${local.lambda_dir}/job_events_indexer.py"
  output_path = "${local.lambda_dir}/job_events_indexer.zip"
}

resource "aws_lambda_function" "job_events_indexer" {
  filename         = data.archive_file.job_events_indexer.output_path
  function_name    = "${local.resource_prefix}-job-events-indexer"
  role             = aws_iam_role.lambda_job_events.arn
  handler          = "job_events_indexer.handler"
  source_code_hash = data.archive_file.job_events_indexer.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  layers           = [aws_lambda_layer_version.opensearch_deps.arn]

  environment {
    variables = {
      OPENSEARCH_ENDPOINT     = local.opensearch_endpoint
      OPENSEARCH_INDEX_COMMON = "job-events"
      REGION                  = local.region
    }
  }

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-job-events-indexer"
  })

  depends_on = [
    aws_cloudwatch_log_group.job_events_indexer
  ]
}

resource "aws_cloudwatch_log_group" "job_events_indexer" {
  name              = "/aws/lambda/${local.resource_prefix}-job-events-indexer"
  retention_in_days = 14

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-job-events-indexer-logs"
  })
}

# Subscribe to job_events topic (all events)
resource "aws_sns_topic_subscription" "job_events_to_indexer" {
  topic_arn = local.events_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.job_events_indexer.arn
}

resource "aws_lambda_permission" "sns_invoke_indexer" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.job_events_indexer.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = local.events_topic_arn
}

# =============================================================================
# 2. Approval Processor
# =============================================================================

data "archive_file" "approval_processor" {
  type        = "zip"
  source_file = "${local.lambda_dir}/approval_processor.py"
  output_path = "${local.lambda_dir}/approval_processor.zip"
}

resource "aws_lambda_function" "approval_processor" {
  filename         = data.archive_file.approval_processor.output_path
  function_name    = "${local.resource_prefix}-approval-processor"
  role             = aws_iam_role.lambda_job_events.arn
  handler          = "approval_processor.handler"
  source_code_hash = data.archive_file.approval_processor.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  layers           = [aws_lambda_layer_version.opensearch_deps.arn]

  environment {
    variables = {
      OPENSEARCH_ENDPOINT = local.opensearch_endpoint
      REGION              = local.region
    }
  }

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-approval-processor"
  })

  depends_on = [
    aws_cloudwatch_log_group.approval_processor
  ]
}

resource "aws_cloudwatch_log_group" "approval_processor" {
  name              = "/aws/lambda/${local.resource_prefix}-approval-processor"
  retention_in_days = 14

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-approval-processor-logs"
  })
}

# Subscribe to job_approvals topic
resource "aws_sns_topic_subscription" "approvals_to_processor" {
  count     = local.approvals_topic_arn != "" ? 1 : 0
  topic_arn = local.approvals_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.approval_processor.arn
}

resource "aws_lambda_permission" "sns_invoke_approval" {
  count         = local.approvals_topic_arn != "" ? 1 : 0
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.approval_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = local.approvals_topic_arn
}

# =============================================================================
# 3. Downstream Orchestrator
# =============================================================================

data "archive_file" "downstream_orchestrator" {
  type        = "zip"
  source_file = "${local.lambda_dir}/downstream_orchestrator.py"
  output_path = "${local.lambda_dir}/downstream_orchestrator.zip"
}

resource "aws_lambda_function" "downstream_orchestrator" {
  filename         = data.archive_file.downstream_orchestrator.output_path
  function_name    = "${local.resource_prefix}-downstream-orchestrator"
  role             = aws_iam_role.lambda_job_events.arn
  handler          = "downstream_orchestrator.handler"
  source_code_hash = data.archive_file.downstream_orchestrator.output_base64sha256
  runtime          = "python3.11"
  timeout          = 120
  memory_size      = 256

  environment {
    variables = {
      REGION                  = local.region
      WORKFLOW_CONFIG_S3_URI  = local.orchestration_config_s3_uri
      WORKFLOW_CONFIG_PARAM   = ""  # Fallback: SSM parameter path
      MWAA_TRIGGER_QUEUE_URL  = local.mwaa_triggers_queue_url
    }
  }

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-downstream-orchestrator"
  })

  depends_on = [
    aws_cloudwatch_log_group.downstream_orchestrator
  ]
}

resource "aws_cloudwatch_log_group" "downstream_orchestrator" {
  name              = "/aws/lambda/${local.resource_prefix}-downstream-orchestrator"
  retention_in_days = 14

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-downstream-orchestrator-logs"
  })
}

# Subscribe to job_events topic (filtered: SUCCESS only)
resource "aws_sns_topic_subscription" "job_events_to_orchestrator" {
  topic_arn = local.events_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.downstream_orchestrator.arn

  filter_policy = jsonencode({
    status = ["SUCCESS"]
  })
}

resource "aws_lambda_permission" "sns_invoke_orchestrator_events" {
  statement_id  = "AllowSNSInvokeFromEvents"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.downstream_orchestrator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = local.events_topic_arn
}

# Subscribe to job_approvals topic (filtered: APPROVED only)
resource "aws_sns_topic_subscription" "approvals_to_orchestrator" {
  count     = local.approvals_topic_arn != "" ? 1 : 0
  topic_arn = local.approvals_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.downstream_orchestrator.arn

  filter_policy = jsonencode({
    decision = ["APPROVED"]
  })
}

resource "aws_lambda_permission" "sns_invoke_orchestrator_approvals" {
  count         = local.approvals_topic_arn != "" ? 1 : 0
  statement_id  = "AllowSNSInvokeFromApprovals"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.downstream_orchestrator.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = local.approvals_topic_arn
}

# =============================================================================
# Outputs
# =============================================================================

output "job_events_indexer_arn" {
  value       = aws_lambda_function.job_events_indexer.arn
  description = "Job events indexer Lambda ARN"
}

output "approval_processor_arn" {
  value       = aws_lambda_function.approval_processor.arn
  description = "Approval processor Lambda ARN"
}

output "downstream_orchestrator_arn" {
  value       = aws_lambda_function.downstream_orchestrator.arn
  description = "Downstream orchestrator Lambda ARN"
}

output "lambda_job_events_role_arn" {
  value       = aws_iam_role.lambda_job_events.arn
  description = "IAM role ARN for job event Lambda functions"
}

output "opensearch_endpoint" {
  value       = local.opensearch_endpoint
  description = "OpenSearch endpoint (from infra remote state)"
}
