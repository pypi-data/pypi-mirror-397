locals {
  region          = var.region
  account_id      = data.aws_caller_identity.current.account_id
  resource_prefix = "sfly-aws-dwh-sandbox-${var.environment}-mwaa"

  # Common tags
  tags = {
    Environment        = var.environment
    App                = "mwaa"
    DataClassification = "AllDatasets"
    ManagedBy          = "DataPlatformOperations"
    BusinessUnit       = "Consumer"
    Provisioner        = "Terraform"
    Owner              = "DWH"
    InfraState         = "dwh-poc-business-logic-poc/infra/${var.environment}/us-west-1.state"
    MwaaState          = "dwh-poc-business-logic-poc/mwaa/${var.environment}/us-west-1.state"
  }
}
