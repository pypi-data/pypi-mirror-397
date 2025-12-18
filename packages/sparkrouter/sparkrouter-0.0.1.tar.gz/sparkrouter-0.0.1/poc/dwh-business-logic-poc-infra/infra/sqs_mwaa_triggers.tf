# =============================================================================
# SQS Queue for MWAA Event Triggers
# =============================================================================
#
# Architecture:
#   Job SUCCESS -> SNS -> Lambda Orchestrator -> SQS -> MWAA Dispatcher DAG
#                              ↓
#                      workflow_config.json
#                      (dag_id + parameter_mapping)
#
# The orchestrator lambda publishes structured messages directly to this queue.
# Messages contain {dag_id, conf} for the MWAA dispatcher to consume.
# =============================================================================

# SQS Queue for MWAA to poll
resource "aws_sqs_queue" "mwaa_triggers" {
  name = "${local.resource_prefix}-mwaa-triggers"

  # Long polling - MWAA will wait up to 20 seconds for messages
  receive_wait_time_seconds = 20

  # Message retention - keep messages for 4 days if not processed
  message_retention_seconds = 345600

  # Visibility timeout - hide message for 5 minutes while processing
  visibility_timeout_seconds = 300

  # Enable server-side encryption
  sqs_managed_sse_enabled = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-mwaa-triggers"
  })
}

# Dead letter queue for failed messages
resource "aws_sqs_queue" "mwaa_triggers_dlq" {
  name = "${local.resource_prefix}-mwaa-triggers-dlq"

  message_retention_seconds = 1209600  # 14 days

  sqs_managed_sse_enabled = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-mwaa-triggers-dlq"
  })
}

# Redrive policy - send to DLQ after 3 failed attempts
resource "aws_sqs_queue_redrive_policy" "mwaa_triggers" {
  queue_url = aws_sqs_queue.mwaa_triggers.id

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.mwaa_triggers_dlq.arn
    maxReceiveCount     = 3
  })
}
