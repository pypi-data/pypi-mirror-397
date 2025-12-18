resource "aws_subnet" "public" {
  for_each = { for idx, cidr in local.subnet_cidr_public : idx => {
    cidr  = cidr
    az    = local.subnet_regions[idx]
  } }

  vpc_id                  = aws_vpc.poc_vpc.id
  availability_zone       = each.value.az
  cidr_block              = each.value.cidr
  map_public_ip_on_launch = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-public-${each.key}"
  })
}

resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_vpc.poc_vpc.default_route_table_id
}

resource "aws_eip" "eip" {
  for_each = aws_subnet.public

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-eip-${each.key}"
  })
}

resource "aws_nat_gateway" "nat" {
  for_each      = aws_subnet.public
  subnet_id     = each.value.id
  allocation_id = aws_eip.eip[each.key].id

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-nat-${each.key}"
  })
}

resource "aws_route" "nat_route" {
  for_each = aws_route_table.private

  route_table_id         = each.value.id
  nat_gateway_id         = aws_nat_gateway.nat[each.key].id
  destination_cidr_block = "0.0.0.0/0"
}
