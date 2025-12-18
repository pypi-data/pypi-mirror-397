resource "aws_sns_topic_subscription" "dwh_pipeline_events_email" {
  topic_arn = aws_sns_topic.dwh_pipeline_events.arn
  protocol  = "email"
  endpoint  = local.user_email
}

resource "aws_sns_topic_subscription" "dwh_pipeline_approvals_email" {
  topic_arn = aws_sns_topic.dwh_pipeline_approvals.arn
  protocol  = "email"
  endpoint  = local.user_email
}