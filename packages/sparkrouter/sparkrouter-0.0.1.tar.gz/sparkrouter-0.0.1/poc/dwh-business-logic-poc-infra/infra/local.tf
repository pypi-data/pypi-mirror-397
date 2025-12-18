data "aws_availability_zones" "available" {
  state = "available"
  # Optionally, filter out Local Zones
  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
}

locals {

  user_email    = var.email
  region        = var.region

  vpc_cidr = var.cidr_block
  subnet_cidr_public = [
    cidrsubnet(local.vpc_cidr, 8, 20), # 10.1.20.0/24
    cidrsubnet(local.vpc_cidr, 8, 21)  # 10.1.21.0/24
  ]
  subnet_cidr_private = [
    cidrsubnet(local.vpc_cidr, 8, 10), # 10.1.10.0/24
    cidrsubnet(local.vpc_cidr, 8, 11)  # 10.1.11.0/24
  ]

  subnet_regions = slice(data.aws_availability_zones.available.names, 0, 2)

  account_id      = data.aws_caller_identity.current.account_id
  resource_prefix = "sfly-aws-dwh-sandbox-${var.environment}"

  # postgres_usr = "postgres"
  # postgres_pwd = "Postgres1234!" # Change this to a secure password
  # postgres_db_name  = var.environment

  # Service credentials
  opensearch_master_password = "OpenSearch1234!" # Change this to a secure password

  # Common tags to all resources
  tags = {
    Environment        = "sandbox"
    App                = var.environment
    DataClassification = "AllDatasets"
    ManagedBy          = "DataPlatformOperations"
    BusinessUnit       = "Consumer"
    Provisioner        = "Terraform"
    Owner              = "DWH"
  }
}
