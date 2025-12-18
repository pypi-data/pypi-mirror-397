#!/bin/bash

REGION = "us-west-1"

# Check required variables
#if [[ -z "$REGION" ]]; then
#  echo "Error: REGION must be set before running this script. Do NOT check in your changes."
#  exit 1
#fi

USED_CIDRS=(
  $(aws ec2 describe-vpcs --query "Vpcs[*].CidrBlock" --output text --region $REGION)
  $(aws ec2 describe-subnets --query "Subnets[*].CidrBlock" --output text --region $REGION)
)

echo "Used CIDR blocks in AWS:"
for cidr in "${USED_CIDRS[@]}"; do
  echo "  $cidr"
done
echo

cidr_overlaps() {
    python3 -c "import ipaddress, sys; sys.exit(0) if ipaddress.ip_network('$1').overlaps(ipaddress.ip_network('$2')) else sys.exit(1)"
}

for i in $(seq 0 255); do
    candidate="10.$i.0.0/16"
    conflict=0
    for used in "${USED_CIDRS[@]}"; do
        if cidr_overlaps "$candidate" "$used"; then
            conflict=1
            break
        fi
    done
    if [ $conflict -eq 0 ]; then
        echo "Available CIDR: $candidate"
        exit 0
    fi
done

echo "No available /16 CIDR found."
exit 1