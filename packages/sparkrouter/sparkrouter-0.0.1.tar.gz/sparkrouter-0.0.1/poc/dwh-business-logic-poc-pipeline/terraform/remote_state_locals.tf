# Local values from remote state
#
# These locals reference infrastructure managed by the shared infra/ Terraform config.
# infra/ MUST be deployed first before deploying pipeline/.

locals {
  # S3 Buckets
  code_bucket_id  = data.terraform_remote_state.infra.outputs.code_bucket_id
  code_bucket_arn = data.terraform_remote_state.infra.outputs.code_bucket_arn
  # data_bucket_id  = data.terraform_remote_state.infra.outputs.data_bucket_id
  # data_bucket_arn = data.terraform_remote_state.infra.outputs.data_bucket_arn

  # RDS PostgreSQL
  # postgres_endpoint       = data.terraform_remote_state.infra.outputs.postgres_endpoint
  # postgres_db_name        = data.terraform_remote_state.infra.outputs.postgres_db_name
  # postgres_security_group = data.terraform_remote_state.infra.outputs.postgres_security_group_id

  # Glue
  # glue_connection_name   = data.terraform_remote_state.infra.outputs.glue_connection_name
  # glue_role_arn          = data.terraform_remote_state.infra.outputs.glue_role_arn
  # glue_role_name         = data.terraform_remote_state.infra.outputs.glue_role_name
  # glue_security_group_id = data.terraform_remote_state.infra.outputs.glue_security_group_id

  # SNS
  events_topic_arn    = data.terraform_remote_state.infra.outputs.events_topic_arn
  approvals_topic_arn = data.terraform_remote_state.infra.outputs.approvals_topic_arn

  # SES
  # ses_email_identity = data.terraform_remote_state.infra.outputs.ses_email_identity

  # OpenSearch
  opensearch_endpoint   = data.terraform_remote_state.infra.outputs.opensearch_endpoint
  opensearch_domain_arn = data.terraform_remote_state.infra.outputs.opensearch_domain_arn

  # SQS
  mwaa_triggers_queue_url = data.terraform_remote_state.infra.outputs.mwaa_triggers_queue_url
  mwaa_triggers_queue_arn = data.terraform_remote_state.infra.outputs.mwaa_triggers_queue_arn
}
