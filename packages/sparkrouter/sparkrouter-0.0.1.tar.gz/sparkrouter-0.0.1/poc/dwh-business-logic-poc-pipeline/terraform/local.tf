locals {
  region          = var.region
  account_id      = data.aws_caller_identity.current.account_id
  resource_prefix = "sfly-aws-dwh-sandbox-${var.environment}-poc"

  # Code version: use variable if provided, otherwise read from VERSION file
  code_version = var.code_version != "" ? var.code_version : trimspace(file("${path.module}/../VERSION"))

  # Orchestration config S3 URI
  # Uses code bucket from remote state and code version
  orchestration_config_s3_uri = "s3://${local.code_bucket_id}/code/${local.code_version}/orchestration/workflow_config.json"

  # Common tags
  tags = {
    Environment        = var.environment
    App                = "pipeline"
    DataClassification = "AllDatasets"
    ManagedBy          = "DataPlatformOperations"
    BusinessUnit       = "Consumer"
    Provisioner        = "Terraform"
    Owner              = "DWH"
    InfraState         = "dwh-poc-business-logic-poc/infra/us-west-1.state"
    PipelineState      = "dwh-poc-business-logic-poc/pipeline/us-west-1.state"
  }
}
