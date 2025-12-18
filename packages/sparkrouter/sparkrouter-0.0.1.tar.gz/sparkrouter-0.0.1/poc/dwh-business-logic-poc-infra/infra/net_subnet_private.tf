resource "aws_subnet" "private" {
  for_each = { for idx, cidr in local.subnet_cidr_private : idx => {
    cidr  = cidr
    az    = local.subnet_regions[idx]
  } }

  vpc_id                  = aws_vpc.poc_vpc.id
  availability_zone       = each.value.az
  cidr_block              = each.value.cidr
  map_public_ip_on_launch = false

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-private-${each.key}"
  })
}

resource "aws_route_table" "private" {
  for_each = aws_subnet.private

  vpc_id = aws_vpc.poc_vpc.id
  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-private-${each.key}"
  })
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.key].id
}
