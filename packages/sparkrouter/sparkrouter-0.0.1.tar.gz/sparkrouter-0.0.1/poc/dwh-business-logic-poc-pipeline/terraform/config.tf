terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.80.0"
    }
    # databricks = {
    #   source  = "databricks/databricks"
    #   version = "~> 1.30.0"
    # }
  }

  backend "s3" {
    bucket = "sfly-aws-sandbox-terraform"
    key    = "dwh-poc-business-logic-poc/pipeline/us-west-1.state"
    region = "us-east-1"
  }
}

provider "aws" {
  region = local.region
}

# provider "databricks" {
#   # host  = "https://sfly-aws-dwh-dev-consumer.cloud.databricks.com"
#   # token = "d09d5fd7-a9f3-42b4-8720-47f569e1a844"
#   # Or use service_principal_id and service_principal_password for service principal auth
#   client_id     = local.databricks_client_id
#   client_secret = data.aws_secretsmanager_secret_version.current.secret_string
#   account_id    = local.databricks_account_id
# }

data "aws_caller_identity" "current" {}