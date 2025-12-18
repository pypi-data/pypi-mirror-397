terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.80.0"
    }
  }

  backend "s3" {
    bucket = "sfly-aws-sandbox-terraform"
    key    = "dwh-poc-business-logic-poc/mwaa/us-west-1.state"
    region = "us-east-1"
  }
}

provider "aws" {
  region = local.region
}

data "aws_caller_identity" "current" {}