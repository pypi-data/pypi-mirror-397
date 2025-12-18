# # IAM Role for Lambda function to process job metrics
# # This role is created in infra/ so OpenSearch can reference it in access policies
# resource "aws_iam_role" "lambda_job_metrics" {
#   name = "${local.resource_prefix}-lambda-job-metrics-role"
#
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#         Action = "sts:AssumeRole"
#       }
#     ]
#   })
#
#   tags = merge(local.tags, {
#     Name = "${local.resource_prefix}-lambda-job-metrics-role"
#   })
# }
#
# # Policy for Lambda to write logs
# resource "aws_iam_role_policy" "lambda_logs" {
#   name = "${local.resource_prefix}-lambda-logs-policy"
#   role = aws_iam_role.lambda_job_metrics.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "logs:CreateLogGroup",
#           "logs:CreateLogStream",
#           "logs:PutLogEvents"
#         ]
#         Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/${local.resource_prefix}-poc-job-metrics-processor:*"
#       }
#     ]
#   })
# }
#
# # Policy for Lambda to access OpenSearch
# resource "aws_iam_role_policy" "lambda_opensearch" {
#   name = "${local.resource_prefix}-lambda-opensearch-policy"
#   role = aws_iam_role.lambda_job_metrics.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "es:ESHttpPost",
#           "es:ESHttpPut",
#           "es:ESHttpGet",
#           "es:ESHttpHead"
#         ]
#         Resource = [
#           "${aws_opensearch_domain.job_metrics.arn}",
#           "${aws_opensearch_domain.job_metrics.arn}/*"
#         ]
#       }
#     ]
#   })
# }
#
# # Policy for Lambda to read Glue job details (for enriching metrics)
# resource "aws_iam_role_policy" "lambda_glue_read" {
#   name = "${local.resource_prefix}-lambda-glue-read-policy"
#   role = aws_iam_role.lambda_job_metrics.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "glue:GetJob",
#           "glue:GetJobRun",
#           "glue:GetJobRuns"
#         ]
#         Resource = "*"
#       }
#     ]
#   })
# }
#
# # Policy for Lambda to read S3 metrics files (optional - if jobs write metrics to S3)
# resource "aws_iam_role_policy" "lambda_s3_metrics" {
#   name = "${local.resource_prefix}-lambda-s3-metrics-policy"
#   role = aws_iam_role.lambda_job_metrics.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "s3:GetObject",
#           "s3:ListBucket"
#         ]
#         Resource = [
#           "${aws_s3_bucket.data.arn}",
#           "${aws_s3_bucket.data.arn}/*/metrics/*"
#         ]
#       }
#     ]
#   })
# }
