resource "aws_vpc" "poc_vpc" {
  cidr_block        = local.vpc_cidr
  instance_tenancy  = "default"

  #  enables external access to dbs
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-vpc"
  })
}

resource aws_internet_gateway "vpc_igw" {
  vpc_id = aws_vpc.poc_vpc.id
  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-vpc-gateway"
  })
}

resource "aws_route" "igw_route" {
  route_table_id = aws_vpc.poc_vpc.default_route_table_id
  gateway_id = aws_internet_gateway.vpc_igw.id
  destination_cidr_block = "0.0.0.0/0"
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.poc_vpc.id
  service_name      = "com.amazonaws.${local.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for rt in values(aws_route_table.private) : rt.id]
  tags = local.tags
}
