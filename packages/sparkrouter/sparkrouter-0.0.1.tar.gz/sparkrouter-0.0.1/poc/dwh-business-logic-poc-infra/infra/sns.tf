resource "aws_sns_topic" "dwh_pipeline_events" {
  name = "dwh-pipeline-events-${var.environment}"

  tags = merge(local.tags, {
    Name = "dwh-pipeline-events-${var.environment}"
  })
}

resource "aws_sns_topic" "dwh_pipeline_approvals" {
  name = "dwh-pipeline-approvals-${var.environment}"

  tags = merge(local.tags, {
    Name = "dwh-pipeline-approvals-${var.environment}"
  })
}