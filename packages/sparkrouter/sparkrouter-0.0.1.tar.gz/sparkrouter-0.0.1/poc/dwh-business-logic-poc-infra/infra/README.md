# Shared DWH Infrastructure

This directory contains shared infrastructure resources used by both MWAA and Pipeline configurations.

## Resources Managed

- **Networking:** VPC, subnets (2 public, 2 private), NAT gateways, internet gateway, S3 VPC endpoint
- **Storage:** S3 buckets (code, data) with versioning
- **Database:** PostgreSQL RDS instance (db.t3.small, 20GB)
- **Integration:** Glue connections and base IAM roles
- **Notifications:** SNS topics (alerts, quality) with email subscriptions
- **Email:** SES email identity

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 5.80.0
- User initials (lowercase)
- Email address
- Available CIDR block (use `../mwaa/cidr_finder.sh <region>` to find one)

## Deployment

### 1. Initialize Terraform

The backend configuration requires a key to be provided at init time. The key should include the environment to support multiple isolated deployments:

```bash
cd infra/
terraform init -backend-config="key=dwh-poc-business-logic-poc/infra/<environment>/<region>.state"
```

Example for dev environment:
```bash
terraform init -backend-config="key=dwh-poc-business-logic-poc/infra/dev/us-west-1.state"
```

### 2. Plan Deployment

```bash
terraform plan \
  -var="email=jclark@shutterfly.com" \
  -var="region=us-west-1" \
  -var="cidr_block=10.1.0.0/16" \
  -var="environment=dev"
```

### 3. Apply

```bash
terraform apply \
  -var="email=jclark@shutterfly.com" \
  -var="region=us-west-1" \
  -var="cidr_block=10.1.0.0/16" \
  -var="environment=dev"
```

### 4. Deploying Multiple Environments

The same configuration can deploy multiple isolated data environments by changing the `environment` variable and state key:

**Dev Environment:**
```bash
terraform init -backend-config="key=dwh-poc-infra/jc/dev/us-west-1.state"
terraform apply -var="environment=dev" -var="cidr_block=10.1.0.0/16" -var="email=jclark@shutterfly.com" -var="region=us-west-1"
```

**QA Environment (in production account):**
```bash
terraform init -backend-config="key=dwh-poc-infra/jc/qa/us-west-1.state" -reconfigure
terraform apply -var="environment=qa" -var="cidr_block=10.2.0.0/16" -var="email=jclark@shutterfly.com" -var="region=us-west-1"
```

**Production Environment (in production account):**
```bash
terraform init -backend-config="key=dwh-poc-infra/jc/prod/us-west-1.state" -reconfigure
terraform apply -var="environment=prod" -var="cidr_block=10.3.0.0/16" -var="email=jclark@shutterfly.com" -var="region=us-west-1"
```

**Important:** Use different CIDR blocks for each environment to avoid IP conflicts in the same AWS account.

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `email` | User email for notifications | - | Yes |
| `region` | AWS region | us-west-1 | No |
| `cidr_block` | VPC CIDR block | - | Yes |
| `environment` | Data environment (dev, qa, prod) | - | Yes |

## Outputs

The following outputs are available for consumption by mwaa/ and pipeline/ via remote state:

### VPC & Networking
- `vpc_id` - VPC ID
- `vpc_cidr` - VPC CIDR block
- `private_subnet_ids` - List of private subnet IDs
- `public_subnet_ids` - List of public subnet IDs
- `private_subnets` - Map of private subnet details
- `public_subnets` - Map of public subnet details

### S3
- `code_bucket_id` - Code bucket name
- `code_bucket_arn` - Code bucket ARN
- `data_bucket_id` - Data bucket name
- `data_bucket_arn` - Data bucket ARN

### RDS PostgreSQL
- `postgres_endpoint` - Database endpoint
- `postgres_address` - Database address
- `postgres_port` - Database port
- `postgres_db_name` - Database name
- `postgres_username` - Database username (sensitive)
- `postgres_password` - Database password (sensitive)
- `postgres_security_group_id` - PostgreSQL security group ID

### Glue
- `glue_connection_name` - Glue PostgreSQL connection name
- `glue_security_group_id` - Glue security group ID
- `glue_role_arn` - Glue IAM role ARN
- `glue_role_name` - Glue IAM role name

### SNS
- `alerts_topic_arn` - Alerts SNS topic ARN
- `quality_topic_arn` - Quality SNS topic ARN

### SES
- `ses_email_identity` - SES email identity

### Metadata
- `resource_prefix` - Resource naming prefix
- `region` - AWS region
- `account_id` - AWS account ID

## Remote State Consumption

Other configurations (mwaa/, pipeline/) can reference this state to access shared infrastructure. They must point to the same environment's state file:

```hcl
data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = "sfly-aws-sandbox-terraform"
    key    = "dwh-poc-business-logic-poc/infra/jc/us-west-1.state"  # Match the environment!
    region = "us-east-1"
  }
}

# Access outputs
vpc_id = data.terraform_remote_state.infra.outputs.vpc_id
```

**Important:** The environment and region in the remote state key must match the environment and region you're deploying. For example, mwaa/ for QA should reference `dwh-poc-business-logic-poc/infra/qa/us-east-1.state`, not the dev state.

## State File Location

S3 bucket: `sfly-aws-sandbox-terraform`

Key pattern: `dwh-poc-business-logic-poc/infra/${environment}/${region}.state`

Region (the region of the state bucket, not deployment region): `us-east-1`

Examples:
- Dev: `dwh-poc-business-logic-poc/infra/dev/us-east-1.state`
- QA: `dwh-poc-business-logic-poc/infra/qa/us-east-1.state`
- Prod: `dwh-poc-business-logic-poc/infra/prod/us-east-1.state`

## Resource Naming

Resources are named with the pattern: `sfly-aws-dwh-sandbox-${environment}`

Examples:
- Dev environment: `sfly-aws-dwh-sandbox-dev-*`
- QA environment: `sfly-aws-dwh-sandbox-qa-*`
- Prod environment: `sfly-aws-dwh-sandbox-prod-*`

This allows multiple isolated data environments to coexist in the same AWS account.

## Destroy

To tear down the infrastructure:

```bash
terraform destroy \
  -var="email=jclark@shutterfly.com" \
  -var="region=us-west-1" \
  -var="cidr_block=10.1.0.0/16" \
  -var="environment=dev"
```

Make sure to destroy dependent configurations (mwaa/, pipeline/) first before destroying infra/.

## Notes

- This infrastructure is deployed **per data environment** (dev, qa, prod) and shared by mwaa/ and pipeline/ configurations for that environment
- The `environment` variable is NOT about "sandbox" vs "production" AWS accounts - it's about data environments within an account (e.g., QA and PROD data running side-by-side in production account)
- Ensure no CIDR block conflicts with existing VPCs in the region (especially important when running multiple environments in same account)
- Database password in `local.tf` should be changed to a secure value or moved to AWS Secrets Manager
- SNS topic subscriptions will send confirmation emails on first deployment
- Each environment gets its own isolated infrastructure: separate VPCs, databases, buckets, etc.
