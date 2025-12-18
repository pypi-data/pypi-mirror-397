# VPC Outputs
output "vpc_id" {
  value       = aws_vpc.poc_vpc.id
  description = "VPC ID"
}

output "vpc_cidr" {
  value       = aws_vpc.poc_vpc.cidr_block
  description = "VPC CIDR block"
}

# Subnet Outputs
output "private_subnet_ids" {
  value       = values(aws_subnet.private)[*].id
  description = "Private subnet IDs"
}

output "public_subnet_ids" {
  value       = values(aws_subnet.public)[*].id
  description = "Public subnet IDs"
}

output "private_subnets" {
  value = {
    for k, s in aws_subnet.private :
    k => {
      id   = s.id
      az   = s.availability_zone
      cidr = s.cidr_block
    }
  }
  description = "Private subnet details"
}

output "public_subnets" {
  value = {
    for k, s in aws_subnet.public :
    k => {
      id   = s.id
      az   = s.availability_zone
      cidr = s.cidr_block
    }
  }
  description = "Public subnet details"
}

# S3 Outputs
output "code_bucket_id" {
  value       = aws_s3_bucket.code.id
  description = "Code bucket name"
}

output "code_bucket_arn" {
  value       = aws_s3_bucket.code.arn
  description = "Code bucket ARN"
}

output "data_bucket_id" {
  value       = aws_s3_bucket.data.id
  description = "Data bucket name"
}

output "data_bucket_arn" {
  value       = aws_s3_bucket.data.arn
  description = "Data bucket ARN"
}

# RDS Outputs
# output "postgres_endpoint" {
#   value       = aws_db_instance.postgres.endpoint
#   description = "PostgreSQL endpoint"
# }

# output "postgres_address" {
#   value       = aws_db_instance.postgres.address
#   description = "PostgreSQL address"
# }

# output "postgres_port" {
#   value       = aws_db_instance.postgres.port
#   description = "PostgreSQL port"
# }

# output "postgres_db_name" {
#   value       = aws_db_instance.postgres.db_name
#   description = "PostgreSQL database name"
# }

# output "postgres_username" {
#   value       = local.postgres_usr
#   description = "PostgreSQL username"
#   sensitive   = true
# }

# output "postgres_password" {
#   value       = local.postgres_pwd
#   description = "PostgreSQL password"
#   sensitive   = true
# }

# output "postgres_security_group_id" {
#   value       = aws_security_group.sg_postgres.id
#   description = "PostgreSQL security group ID"
# }

# Glue Outputs
# output "glue_connection_name" {
#   value       = aws_glue_connection.postgres_connection.name
#   description = "Glue PostgreSQL connection name"
# }

# output "glue_security_group_id" {
#   value       = aws_security_group.sg_glue.id
#   description = "Glue security group ID"
# }

output "glue_role_arn" {
  value       = aws_iam_role.glue_role.arn
  description = "Glue IAM role ARN"
}

output "glue_role_name" {
  value       = aws_iam_role.glue_role.name
  description = "Glue IAM role name"
}

# SNS Outputs
output "events_topic_arn" {
  value       = aws_sns_topic.dwh_pipeline_events.arn
  description = "Events SNS topic ARN"
}

output "approvals_topic_arn" {
  value       = aws_sns_topic.dwh_pipeline_approvals.arn
  description = "Approvals SNS topic ARN"
}

# SES Outputs
output "ses_email_identity" {
  value       = aws_ses_email_identity.jclark.email
  description = "SES email identity"
}

# Metadata Outputs
output "resource_prefix" {
  value       = local.resource_prefix
  description = "Resource naming prefix"
}

output "region" {
  value       = local.region
  description = "AWS region"
}

output "account_id" {
  value       = local.account_id
  description = "AWS account ID"
}

# OpenSearch Outputs
output "opensearch_endpoint" {
  value       = aws_opensearch_domain.job_metrics.endpoint
  description = "OpenSearch domain endpoint"
}

output "opensearch_dashboard_endpoint" {
  value       = aws_opensearch_domain.job_metrics.dashboard_endpoint
  description = "OpenSearch Dashboards endpoint"
}

output "opensearch_domain_arn" {
  value       = aws_opensearch_domain.job_metrics.arn
  description = "OpenSearch domain ARN"
}

# Lambda IAM Role Outputs
# output "lambda_job_metrics_role_arn" {
#   value       = aws_iam_role.lambda_job_metrics.arn
#   description = "IAM role ARN for Lambda job metrics processor"
# }
#
# output "lambda_job_metrics_role_name" {
#   value       = aws_iam_role.lambda_job_metrics.name
#   description = "IAM role name for Lambda job metrics processor"
# }

# SQS Outputs
output "mwaa_triggers_queue_url" {
  value       = aws_sqs_queue.mwaa_triggers.url
  description = "SQS queue URL for MWAA to poll for DAG triggers"
}

output "mwaa_triggers_queue_arn" {
  value       = aws_sqs_queue.mwaa_triggers.arn
  description = "SQS queue ARN for MWAA triggers"
}

output "mwaa_triggers_dlq_url" {
  value       = aws_sqs_queue.mwaa_triggers_dlq.url
  description = "Dead letter queue URL for failed MWAA triggers"
}

output "mwaa_triggers_dlq_arn" {
  value       = aws_sqs_queue.mwaa_triggers_dlq.arn
  description = "Dead letter queue ARN for failed MWAA triggers"
}
