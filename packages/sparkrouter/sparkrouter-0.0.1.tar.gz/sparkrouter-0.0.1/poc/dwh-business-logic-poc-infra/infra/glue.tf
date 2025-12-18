# resource "aws_security_group" "sg_glue" {
#   name        = "${local.resource_prefix}-glue-sg"
#   description = "Security group for Glue to access PostgreSQL"
#   vpc_id      = aws_vpc.poc_vpc.id
#
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#
#   tags = merge(local.tags, {
#     Name = "${local.resource_prefix}-glue-sg"
#   })
# }
#
# resource "aws_glue_connection" "postgres_connection" {
#   name = "${local.resource_prefix}-postgres-connection"
#
#   connection_properties = {
#     JDBC_CONNECTION_URL = "jdbc:postgresql://${aws_db_instance.postgres.endpoint}/${aws_db_instance.postgres.db_name}"
#     USERNAME            = local.postgres_usr
#     PASSWORD            = local.postgres_pwd
#   }
#
#   physical_connection_requirements {
#     availability_zone      = values(aws_subnet.private)[0].availability_zone
#     security_group_id_list = [aws_security_group.sg_glue.id]
#     subnet_id              = values(aws_subnet.private)[0].id
#   }
# }
