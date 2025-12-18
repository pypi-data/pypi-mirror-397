# Remote State Data Source
#
# This references the shared infrastructure state from the infra/ directory.
# This allows us to reference shared infrastructure (VPC, subnets, S3, RDS, Glue, etc.)
# without managing it directly in this configuration.
#
# IMPORTANT: The key must match the environment you're deploying!
# - For dev: key = "dwh-poc-infra/jc/dev/us-west-1.state"
# - For qa:  key = "dwh-poc-infra/jc/qa/us-west-1.state"
# - For prod: key = "dwh-poc-infra/jc/prod/us-west-1.state"
#
# This ensures pipeline/ connects to the correct infra/ environment.

data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = "sfly-aws-sandbox-terraform"
    key    = "dwh-poc-business-logic-poc/infra/jc/us-west-1.state"
    region = "us-east-1"
  }
}
