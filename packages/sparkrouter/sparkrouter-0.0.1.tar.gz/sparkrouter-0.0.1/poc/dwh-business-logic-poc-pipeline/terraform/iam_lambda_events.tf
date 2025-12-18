# =============================================================================
# IAM Role for Lambda Functions
# =============================================================================

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_job_events" {
  name               = "${local.resource_prefix}-lambda-job-events"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-lambda-job-events"
  })
}

# CloudWatch Logs permissions (inline policy to avoid iam:CreatePolicy restriction)
resource "aws_iam_role_policy" "lambda_logging" {
  name = "cloudwatch-logs"
  role = aws_iam_role.lambda_job_events.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.job_events_indexer.arn}:*",
          "${aws_cloudwatch_log_group.approval_processor.arn}:*",
          "${aws_cloudwatch_log_group.downstream_orchestrator.arn}:*"
        ]
      }
    ]
  })
}

# OpenSearch permissions (inline policy to avoid iam:CreatePolicy restriction)
resource "aws_iam_role_policy" "lambda_opensearch" {
  name = "opensearch-access"
  role = aws_iam_role.lambda_job_events.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowOpenSearchAccess"
        Effect = "Allow"
        Action = [
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpGet"
        ]
        Resource = "${local.opensearch_domain_arn}/*"
      }
    ]
  })
}

# Orchestrator permissions for triggering downstream jobs
resource "aws_iam_role_policy" "lambda_orchestrator" {
  name = "orchestrator-access"
  role = aws_iam_role.lambda_job_events.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3ConfigRead"
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${local.code_bucket_arn}/code/${local.code_version}/orchestration/*"
      },
      {
        Sid    = "AllowGlueTrigger"
        Effect = "Allow"
        Action = [
          "glue:StartJobRun"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowStepFunctionsTrigger"
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowEventBridgeTrigger"
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowMWAATrigger"
        Effect = "Allow"
        Action = [
          "airflow:CreateWebLoginToken"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowSQSSendMessage"
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = local.mwaa_triggers_queue_arn
      }
    ]
  })
}

