# OpenSearch Domain for Job Metrics and Monitoring
# Public access mode - no security group needed
# Domain name must be 3-28 chars, lowercase letters, digits, hyphens only, start with letter
resource "aws_opensearch_domain" "job_metrics" {
  domain_name    = "dwh-${var.environment}-metrics"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type          = "t3.small.search"  # Cost-effective for POC
    instance_count         = 1                   # Single node for public access
    zone_awareness_enabled = false
  }

  # Public access mode - secured by fine-grained access control (username/password for dashboard)
  # VPC mode commented out to allow dashboard access from internet
  # Lambda authenticates via IAM (role explicitly allowed in access_policies)
  # vpc_options {
  #   subnet_ids         = slice(values(aws_subnet.private)[*].id, 0, 2)
  #   security_group_ids = [aws_security_group.opensearch.id]
  # }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20  # GB - adjust based on expected data volume
    iops        = 3000
    throughput  = 125
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "admin"
      master_user_password = local.opensearch_master_password
    }
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"  # Account root allows IAM-authenticated access
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${local.region}:${local.account_id}:domain/dwh-${var.environment}-metrics/*"
      },
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${local.region}:${local.account_id}:domain/dwh-${var.environment}-metrics/*"
        Condition = {
          IpAddress = {
            "aws:SourceIp" = ["0.0.0.0/0"]
          }
        }
      }
    ]
  })

  # Security model:
  # - Lambda: IAM role authentication via AWS4Auth (SigV4 signing)
  # - Dashboard users: Fine-grained access control (username/password) - enforced by advanced_security_options
  # - Credentials: admin / (see local.opensearch_master_password)

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-job-metrics"
  })

  # Note: Service-linked role AWSServiceRoleForAmazonOpenSearchService
  # is assumed to already exist in the AWS account (created automatically
  # on first OpenSearch domain creation or manually via AWS console)

  # Note: Lambda IAM role to OpenSearch role mapping must be configured manually
  # See: infra/OPENSEARCH_IAM_SETUP.md for instructions
}

# CloudWatch Log Group for OpenSearch logs
resource "aws_cloudwatch_log_group" "opensearch" {
  name              = "/aws/opensearch/${local.resource_prefix}-job-metrics"
  retention_in_days = 14

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-opensearch-logs"
  })
}

resource "aws_cloudwatch_log_resource_policy" "opensearch" {
  policy_name = "${local.resource_prefix}-opensearch-log-policy"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "es.amazonaws.com"
        }
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream"
        ]
        Resource = "${aws_cloudwatch_log_group.opensearch.arn}:*"
      }
    ]
  })
}
