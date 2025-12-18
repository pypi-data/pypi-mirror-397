# Remote State Data Source
#
# This references the shared infrastructure state from the infra/ directory.
#
# IMPORTANT: The key must match the environment you're deploying!
# - For dev: key = "dwh-poc-business-logic-poc/infra/dev/us-west-1.state"
# - For qa:  key = "dwh-poc-business-logic-poc/infra/qa/us-west-1.state"
# - For prod: key = "dwh-poc-business-logic-poc/infra/prod/us-west-1.state"
#
# This ensures mwaa/ connects to the correct infra/ environment.

data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = "sfly-aws-sandbox-terraform"
    key    = "dwh-poc-business-logic-poc/infra/jc/us-west-1.state"
    region = "us-east-1"
  }
}
