# Terraform Environment

This Terraform setup creates an isolated AWS environment for MWAA testing Data Warehouse Business Logic. 
It provisions an S3 bucket and MWAA instance.

## Pre-requisites

The INFRA must be setup first - see [infra/README.md](https://github.com/jclark_sflyinc/dwh-business-logic-poc-infra/blob/899d09e7e7b928b3871b24e1155bf81ed6e0e15f/infra/README.md)

* You will need to be authenticated with AWS CLI and have the necessary permissions to create resources in the specified region.
* Environment name (lowercase, unique; must match infra)
* AWS region (default: us-west-1; must match infra)


## Quick Start

You may find it easier to write a quick script to automate the steps below, but here are the manual steps to set up the environment:

1. Prepare your Terraform state file path:
```shell
dwh-business-logic-poc/mwaa/<environment>/<region>.state
# Example:
#dwh-poc-business-logic-poc/mwaa/dev/us-west-1.state
```

2. Initialize Terraform:
```shell
terraform init -backend-config="key=dwh-business-logic-poc/mwaa/<environment>/<region>.state"
# Example:
#terraform init -backend-config="key=dwh-poc-business-logic-poc/mwaa/dev/us-west-1.state"
```

3. Run Terraform plan:
```shell
terraform plan \
  -var "environment=<environment>" \
  -var "region=<your region>"   
# Example:
#terraform plan \
#  -var "environment=dev" \
#  -var "region=us-west-1"
```

4. Apply to create the environment:
```shell
terraform apply \
  -var "environment=<environment>" \
  -var "region=<your region>"
# Example:
#terraform apply \
#  -var "environment=dev" \
#  -var "region=us-west-1"
```

5. Output variables will provide details about the created resources, including the Postgres database endpoint and Glue connection name.

## What Gets Created
* S3 Bucket for MWAA DAGs
* MWAA Instance

## Deploy Code to S3

To deploy your code to S3, you can use the following command:
```shell
./deploy.sh <environment> <region>

## Destroy the Environment

To tear down the environment, run:
```shell
terraform destroy \
  -var "environment=<environment>" \
  -var "region=<your region>"
# Example:
#terraform destroy \
#  -var "environment=dev" \
#  -var "region=us-west-1"
```