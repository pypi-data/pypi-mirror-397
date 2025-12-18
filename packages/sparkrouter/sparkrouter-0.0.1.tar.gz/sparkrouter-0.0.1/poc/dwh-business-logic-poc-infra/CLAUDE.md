# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Terraform infrastructure-as-code for a Data Warehouse Business Logic POC on AWS. It provisions three separate but interconnected environments:

1. **Shared Infrastructure** (`infra/`) - Common networking, storage, and database resources
2. **MWAA Environment** (`mwaa/`) - Apache Airflow managed service infrastructure (depends on infra/)
3. **Pipeline Environment** (`pipeline/`) - Job monitoring and data pipeline infrastructure (depends on infra/)

The shared infrastructure is deployed once and consumed by both MWAA and Pipeline environments via Terraform remote state, eliminating duplication and ensuring consistency.

## Terraform Commands

### Shared Infrastructure (infra/)

The shared infrastructure must be deployed first, as both mwaa/ and pipeline/ depend on it.

The `environment` variable represents the **data environment** (dev, qa, prod, sandbox) and allows multiple isolated deployments in the same AWS account:

```bash
cd infra/

# Initialize with environment-aware backend key
terraform init -backend-config="key=dwh-poc-business-logic-poc/infra/<environment>/<region>.state"
# Example: terraform init -backend-config="key=dwh-poc-business-logic-poc/infra/dev/us-west-1.state"

# Plan with variables
terraform plan \
  -var="email=jclark@shutterfly.com" \
  -var="region=us-west-1" \
  -var="cidr_block=10.1.0.0/16" \
  -var="environment=dev"

# Apply
terraform apply \
  -var="email=jclark@shutterfly.com" \
  -var="region=us-west-1" \
  -var="cidr_block=10.1.0.0/16" \
  -var="environment=dev"
```

**Multiple Environments:** To deploy QA and PROD in the same account, use different CIDR blocks and environment values:
- Dev: `environment=dev`, `cidr_block=10.1.0.0/16`, state key: `dwh-poc-infra/jc/dev/us-west-1.state`
- QA: `environment=qa`, `cidr_block=10.2.0.0/16`, state key: `dwh-poc-infra/jc/qa/us-west-1.state`
- Prod: `environment=prod`, `cidr_block=10.3.0.0/16`, state key: `dwh-poc-infra/jc/prod/us-west-1.state`

See `infra/README.md` for detailed documentation of shared resources and outputs.

### MWAA Environment

The MWAA environment can be deployed using the automation script:

```bash
cd mwaa
./deploy-terraform.sh init        # Initialize with remote state
./deploy-terraform.sh plan        # Create execution plan
./deploy-terraform.sh apply       # Deploy infrastructure
./deploy-terraform.sh destroy     # Tear down environment
```

The script uses hardcoded values (edit the script to customize):
- Region: us-west-1
- CIDR Block: 10.0.0.0/16
- User Initials: jc
- Email: jclark@shutterfly.com

### Pipeline Environment

The pipeline environment uses standard Terraform commands:

```bash
cd pipeline

# Initialize with custom backend key
terraform init -backend-config="key=dwh-poc-business-logic/mwaa/us-west-1.state"

# Plan with variables
terraform plan \
  -var "environment=<environment>" \
  -var "email=<email>" \
  -var "region=<region>" \
  -var "cidr_block=<cidr>"

# Apply
terraform apply \
  -var "environment=<environment>" \
  -var "email=<email>" \
  -var "region=<region>" \
  -var "cidr_block=<cidr>"

# Destroy
terraform destroy \
  -var "environment=<environment>" \
  -var "email=<email>" \
  -var "region=<region>" \
  -var "cidr_block=<cidr>"
```

### Finding Available CIDR Blocks

Both environments include a CIDR finder script:

```bash
./cidr_finder.sh <region>
# Example: ./cidr_finder.sh us-west-1
```

## Architecture Overview

### Shared Infrastructure Components (infra/)

The shared infrastructure is deployed once and consumed by both mwaa/ and pipeline/ via remote state:

- **VPC & Networking**: VPC, Internet Gateway, S3 VPC Endpoint, 2 private + 2 public subnets across 2 AZs, NAT Gateways, Route Tables
- **RDS Postgres**: Publicly accessible database (db.t3.small, 20GB) with security group and subnet group
- **AWS Glue**: Security group, PostgreSQL connection, base IAM role (without Redshift permissions)
- **S3 Buckets**:
  - Code bucket with versioning
  - Data bucket with versioning
- **SNS**: Alert and quality notification topics with email subscriptions
- **SES**: Email identity for notifications

Resource prefix: `sfly-aws-dwh-sandbox-{environment}` (e.g., `sfly-aws-dwh-sandbox-dev`)

### MWAA Environment Components (mwaa/)

MWAA-specific resources that depend on shared infrastructure:

- **MWAA**: Managed Apache Airflow environment (mw1.small, Airflow 2.8.1)
- **S3 MWAA Bucket**: DAG, plugin, and requirements storage
- **IAM MWAA Role**: MWAA-specific permissions including Glue job management

Resource prefix: `sfly-aws-dwh-sandbox-{environment}-mwaa`

### Pipeline Environment Components (pipeline/)

Pipeline-specific resources that depend on shared infrastructure:

- **OpenSearch**: 2-node cluster (t3.small.search) for job metrics with Dashboards
- **EventBridge**: Rules capturing Glue job state changes and custom metrics
- **Lambda**: Python 3.11 function processing job events and indexing to OpenSearch
- **Redshift**: Data warehouse cluster (commented out)
- **Databricks**: Integration (provider configured but commented out)
- **IAM Glue Redshift Policy**: Supplemental Redshift permissions attached to shared Glue role

Resource prefix: `sfly-aws-dwh-sandbox-{environment}-poc`

### Remote State Architecture

Both mwaa/ and pipeline/ reference shared infrastructure via `remote_state.tf` and `remote_state_locals.tf`:
- **Data Source**: Points to `infra/` state file in S3 (must match the environment!)
- **Toggle Mechanism**: `use_remote_state` flag allows switching between remote (infra/) and local resources
- **Local Variable Mappings**: All shared resources accessed via `local.*` variables for consistency
- **Environment Awareness**: The remote state key must match the environment being deployed (dev mwaa/ → dev infra/, qa mwaa/ → qa infra/, etc.)

Key remote state outputs consumed:
- VPC ID, CIDR, subnet IDs
- S3 bucket IDs and ARNs
- RDS PostgreSQL endpoint, credentials, security group
- Glue connection name, role ARN, security group
- SNS topic ARNs
- SES email identity

**Critical:** When deploying mwaa/ or pipeline/ for a specific environment (e.g., QA), update `remote_state.tf` to point to the matching infra/ state file:
```hcl
# For QA environment
key = "dwh-poc-infra/jc/qa/us-west-1.state"
```

When `use_remote_state = false`, configurations fall back to local resource definitions (useful for testing or migration).

## File Organization Patterns

All three environments follow a consistent Terraform file structure:

**infra/ (Shared Infrastructure):**
- `config.tf` - Provider configuration and S3 backend (key provided via -backend-config)
- `variables.tf` - Input variables (email, region, cidr_block, environment)
- `local.tf` - Local variables, CIDR calculations, resource naming, tags, credentials
- `net_*.tf` - Networking resources (VPC, subnets, route tables)
- `s3_*.tf` - S3 buckets (code, data)
- `rds_postgres.tf` - PostgreSQL database
- `glue.tf` - Glue connection and security group
- `iam_glue.tf` - Base Glue IAM role
- `sns.tf` - SNS topics
- `ses.tf` - SES email identity
- `outputs.tf` - Comprehensive outputs for remote state consumption

**mwaa/ (MWAA-Specific):**
- `config.tf` - Provider configuration and S3 backend
- `local.tf` - Local variables and resource naming
- `remote_state.tf` - Data source pointing to infra/ state
- `remote_state_locals.tf` - Toggle mechanism and local variable mappings
- `mwaa.tf` - MWAA environment resources
- `iam_mwaa.tf` - MWAA-specific IAM role
- `s3_mwaa.tf` - MWAA DAG/logs bucket

**pipeline/ (Pipeline-Specific):**
- `config.tf` - Provider configuration and S3 backend
- `local.tf` - Local variables and resource naming
- `remote_state.tf` - Data source pointing to infra/ state
- `remote_state_locals.tf` - Toggle mechanism and local variable mappings
- `opensearch.tf` - OpenSearch domain
- `eventbridge.tf` - EventBridge rules
- `lambda_job_metrics.tf` - Lambda function for metrics processing
- `iam_lambda_metrics.tf` - Lambda IAM role
- `iam_glue_redshift.tf` - Supplemental Redshift permissions for shared Glue role
- `redshift.tf` - Redshift cluster (commented out)
- `databricks.tf` - Databricks integration (commented out)

## Important Configuration Details

### User-Specific Variables

All resources are tagged and named with user initials for multi-user isolation:
- `environment`: Data environment (e.g., "dev", "prod", etc.)
- `email`: Shutterfly email address
- `region`: AWS region (default: us-west-1)
- `cidr_block`: VPC CIDR (must not overlap with existing VPCs)

### Subnet Allocation

Both environments use the same subnet calculation:
- Public subnets: `{vpc_cidr}/20` and `/21` (e.g., 10.1.20.0/24, 10.1.21.0/24)
- Private subnets: `{vpc_cidr}/10` and `/11` (e.g., 10.1.10.0/24, 10.1.11.0/24)

### Credentials in local.tf

Both environments store database/service passwords in `local.tf`:
- **MWAA**: `postgres_usr`, `postgres_pwd`, `postgres_db_name`
- **Pipeline**: Adds `redshift_usr`, `redshift_pwd`, `redshift_db_name`, `opensearch_master_password`

These should be changed before deployment and ideally moved to AWS Secrets Manager.

### Remote State Backend

Both environments use the same S3 backend:
- Bucket: `sfly-aws-sandbox-terraform`
- Region: `us-east-1`
- Key structure varies per environment (see `config.tf`)

## OpenSearch Job Monitoring

The pipeline environment includes a complete job monitoring system. Key files:

- `opensearch.tf` - 2-node OpenSearch domain with encryption and fine-grained access
- `eventbridge.tf` - Captures Glue job state changes and custom metrics
- `lambda_job_metrics.tf` - Python Lambda with automatic packaging
- `iam_lambda_metrics.tf` - Permissions for Lambda to access OpenSearch, Glue API, S3

Lambda automatically:
- Processes Glue job state changes
- Enriches events with Glue API details
- Indexes structured data to OpenSearch
- Handles custom metrics JSON from jobs

See `pipeline/README_OPENSEARCH.md` for monitoring setup, dashboard creation, and publishing custom metrics from jobs.

## Common Tasks

### Deploying MWAA Environment

1. Find available CIDR: `cd mwaa && ./cidr_finder.sh us-west-1`
2. Edit `deploy-terraform.sh` with your CIDR, initials, and email
3. Run: `./deploy-terraform.sh init && ./deploy-terraform.sh plan && ./deploy-terraform.sh apply`

### Deploying Pipeline Environment

1. Find available CIDR: `cd pipeline && ./cidr_finder.sh us-west-1`
2. Update passwords in `local.tf`
3. Initialize: `terraform init -backend-config="key=dwh-poc-business-logic/{initials}/{region}.state"`
4. Deploy: `terraform plan` then `terraform apply` with all variables

### Enabling Remote State (Pipeline)

1. Verify the Airflow config state key in S3
2. Update `remote_state.tf` line 19 with correct key
3. Verify available outputs: See `REMOTE_STATE_SETUP.md` Step 2
4. Update `remote_state_locals.tf` output mappings
5. Set `use_remote_state = true` in `remote_state_locals.tf`
6. Run `terraform plan` to verify no unwanted changes

### Lambda Development (Pipeline)

The Lambda function for job metrics is in `lambda/job_metrics_processor/`:
- Terraform detects changes to `.py` and `requirements.txt` files
- Automatically builds deployment package on `terraform apply`
- No manual packaging required

### Checking CIDR Overlaps

Use the Python script to verify no conflicts:

```bash
cd mwaa  # or pipeline
python check_cidr_overlaps.py
```

## Deployment Order

When deploying from scratch, follow this order:

1. **Deploy infra/ first** (shared infrastructure)
   ```bash
   cd infra/
   terraform init -backend-config="key=dwh-poc-infra/jc/dev/us-west-1.state"
   terraform apply -var="email=jclark@shutterfly.com" -var="region=us-west-1" -var="cidr_block=10.1.0.0/16" -var="environment=dev"
   ```

2. **Update remote_state.tf in mwaa/ and pipeline/** to point to the correct environment state
   ```hcl
   # In both mwaa/remote_state.tf and pipeline/remote_state.tf
   key = "dwh-poc-infra/jc/dev/us-west-1.state"  # Match the environment!
   ```

3. **Deploy mwaa/** (depends on infra/)
   ```bash
   cd ../mwaa/
   ./deploy-terraform.sh init
   ./deploy-terraform.sh apply
   ```

4. **Deploy pipeline/** (depends on infra/)
   ```bash
   cd ../pipeline/
   terraform init -backend-config="key=dwh-poc-business-logic/mwaa/us-west-1.state"
   terraform apply -var="email=jclark@shutterfly.com" -var="region=us-west-1" -var="cidr_block=10.1.0.0/16"
   ```

### Deploying Multiple Environments

To deploy QA alongside DEV in production account:

1. Deploy QA infra with different CIDR:
   ```bash
   cd infra/
   terraform init -backend-config="key=dwh-poc-infra/jc/qa/us-west-1.state" -reconfigure
   terraform apply -var="environment=qa" -var="cidr_block=10.2.0.0/16" -var="email=jclark@shutterfly.com"
   ```

2. Update mwaa/remote_state.tf and pipeline/remote_state.tf to use `key = "dwh-poc-infra/jc/qa/us-west-1.state"`

3. Deploy QA mwaa/ and pipeline/ as normal

When updating shared infrastructure:
1. Update infra/ configuration for the specific environment
2. Run `terraform apply` in infra/ for that environment
3. Verify mwaa/ and pipeline/ for that environment still work (they consume outputs via remote state)
4. Update mwaa/ or pipeline/ as needed

## Migration from Local to Remote State

Both mwaa/ and pipeline/ include a toggle mechanism for migrating from local resources to remote state:

1. **Initial state**: `use_remote_state = false` in `remote_state_locals.tf` (uses local resources)
2. **After infra/ is deployed**: Set `use_remote_state = true`
3. **Remove duplicate resources**: Back up and remove net_*.tf, s3_*.tf, rds_postgres.tf, glue.tf, iam_glue.tf, sns.tf, ses.tf files
4. **Apply changes**: `terraform apply` will remove duplicates from state

The toggle allows safe testing and rollback if needed.

## Databricks Integration (Pipeline Only)

The pipeline environment includes Databricks provider configuration but it's commented out in `config.tf`. To enable:

1. Uncomment the provider block in `config.tf`
2. Set credentials in `local.tf` or use AWS Secrets Manager
3. Configure workspace resources in `databricks.tf`

## Tags Applied to All Resources

All three environments apply consistent tags:
- Environment: sandbox
- App: `{environment}` for infra/ (dev, qa, prod), "mwaa" for mwaa/, "poc" for pipeline/
- DataClassification: AllDatasets
- ManagedBy: DataPlatformOperations
- BusinessUnit: Consumer
- Provisioner: Terraform
- Owner: DWH

The infra/ App tag matches the data environment (dev, qa, prod, sandbox), making it easy to identify which environment resources belong to.
