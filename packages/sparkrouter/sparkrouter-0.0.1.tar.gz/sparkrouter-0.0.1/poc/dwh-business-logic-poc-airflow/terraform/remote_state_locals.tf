# Local values from remote state
#
# These locals reference infrastructure managed by the shared infra/ Terraform config.
# infra/ MUST be deployed first before deploying mwaa/.

locals {
  # VPC and Networking
  vpc_id             = data.terraform_remote_state.infra.outputs.vpc_id
  private_subnet_ids = data.terraform_remote_state.infra.outputs.private_subnet_ids

  # Glue
  # glue_connection_name   = data.terraform_remote_state.infra.outputs.glue_connection_name
  glue_role_arn          = data.terraform_remote_state.infra.outputs.glue_role_arn
  # glue_security_group_id = data.terraform_remote_state.infra.outputs.glue_security_group_id
}
