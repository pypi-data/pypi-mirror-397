# dwh-business-logic-poc-airflow
Business Logic POC: Airflow Component - centralizing business logic

[airflow-versions](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html#airflow-versions-official)


## Setup

### Dev Environment
Verify Python 3.11.7 (To match MWAA in DEV)
```shell
python --version
# Should show Python 3.11.7
```



Set up and activate local pyton environment:

```shell
python -m venv venv
source venv/bin/activate

pip install -r requirements-dev.txt
```

Install terraform
```shell
cd
sudo apt-get update
sudo apt-get install -y wget unzip
wget https://releases.hashicorp.com/terraform/1.8.1/terraform_1.8.1_linux_amd64.zip
unzip terraform_1.8.1_linux_amd64.zip
sudo mv terraform /usr/local/bin/
terraform --version

rm terraform_1.8.1_linux_amd64.zip
```


### MWAA

```shell
cd terraform/mwaa
terraform init
terraform apply
```

Create connections
```shell
cd terraform/mwaa

# Get the endpoint
POSTGRES_ENDPOINT=$(terraform output -raw postgres_endpoint)
# sfly-aws-dwh-sandbox-poc-postgres.cpxxromm0k5d.us-east-1.rds.amazonaws.com:5432
POSTGRES_DB_NAME=$(terraform output -raw postgres_db_name)
# airflowdb
POSTGRES_CONN_STRING=$(terraform output -raw postgres_connection_string)
MWAA_WEBSERVER_URL=$(terraform output -raw mwaa_webserver_url)

# Create a CLI token
CLI_TOKEN=$(aws mwaa create-cli-token --name sfly-aws-dwh-sandbox-poc-business-logic --region us-east-1 --output text --query CliToken)

# Use the token to create a connection
curl --request POST "https://${MWAA_WEBSERVER_URL}/aws_mwaa/cli" \
  --header "Authorization: Bearer $CLI_TOKEN" \
  --header "Content-Type: text/plain" \
  --data-raw "connections add --conn-id postgres_db --conn-type postgres --conn-host $POSTGRES_ENDPOINT --conn-schema $POSTGRES_DB_NAME --conn-login airflow --conn-password CHANGE_ME"
````

### Debugging

```shell
# Check MWAA environment status
aws mwaa get-environment --name sfly-aws-dwh-sandbox-poc-business-logic --region us-east-1
```

```shell
# Check CloudWatch logs for MWAA
aws logs describe-log-groups --log-group-name-prefix "/aws/vendedlogs/mwaa" --region us-east-1
```


```shell
# First, find your VPC ID
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=sfly-aws-dwh-sandbox-poc-vpc" --region us-east-1
```

```shell
# Then use it in the endpoints command
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=vpc-057a571e11079fad2" --region us-east-1
```

```shell
# 2. Check SecurityGroup's inbound/outbound rules
aws ec2 describe-security-group-rules --security-group-id sg-0714127313fe06193 --region us-east-1
```

```shell
# 3. View CloudWatch logs for MWAA environment creation
aws logs describe-log-groups --log-group-name-prefix "/aws/mwaa" --region us-east-1
```

```shell
# View specific log streams
aws logs describe-log-streams --log-group-name "/aws/vendedlogs/mwaa/sfly-aws-dwh-sandbox-poc-business-logic" --region us-east-1
```

#### Network Connectivity Testing

Test connectivity from one of your private subnets:
```shell
# Create a test EC2 instance in private subnet
aws ec2 run-instances --image-id ami-0005e0cfe09cc9050 --instance-type t3.micro --subnet-id subnet-03d7bc939902343d3 --security-group-ids sg-0714127313fe06193 --region us-east-1

# Then SSH to it via Session Manager and test connectivity to required services
```

1. Check Your Current CIDR Allocations
```shell
# List your VPC CIDR
aws ec2 describe-vpcs --vpc-ids vpc-057a571e11079fad2 --query "Vpcs[0].CidrBlock" --region us-east-1

# List all subnet CIDRs
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-057a571e11079fad2" --query "Subnets[*].[SubnetId,CidrBlock,Tags[?Key=='Name'].Value]" --output table --region us-east-1
```

### Restart MWAA

```shell
# 1. Upload updated requirements.txt
aws s3 cp requirements.txt s3://sfly-aws-dwh-sandbox-poc-mwaa/requirements.txt

# 2. Get the version ID of the newly uploaded file
aws s3api list-object-versions --bucket sfly-aws-dwh-sandbox-poc-mwaa --prefix requirements.txt --query 'Versions[?IsLatest].VersionId' --output text

# 3. Update MWAA environment with the specific version ID (replace VERSION_ID with the value from above)
aws mwaa update-environment \
  --name sfly-aws-dwh-sandbox-poc-business-logic \
  --region us-east-1 \
  --requirements-s3-object-version 7IVZt4Bde78j00yVf67ISginLGrGjlr7
```