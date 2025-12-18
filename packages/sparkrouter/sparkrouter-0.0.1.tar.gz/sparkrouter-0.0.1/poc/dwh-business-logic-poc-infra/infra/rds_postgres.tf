# resource "aws_security_group" "sg_postgres" {
#   name        = "${local.resource_prefix}-sg-postgres"
#   description = "Security group for PostgreSQL database"
#   vpc_id      = aws_vpc.poc_vpc.id
#
#   ingress {
#     from_port       = 5432
#     to_port         = 5432
#     protocol        = "tcp"
#     # todo: limit this to glue
#     cidr_blocks     = ["0.0.0.0/0"]
#   }
#
#   ingress {
#     from_port                = 5432
#     to_port                  = 5432
#     protocol                 = "tcp"
#     security_groups          = [aws_security_group.sg_glue.id]
#   }
#
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#
#   tags = merge(local.tags, {
#     Name = "${local.resource_prefix}-sg-postgres"
#   })
# }

# resource "aws_db_subnet_group" "postgres_subnet_group" {
#   name       = "${local.resource_prefix}-subnet-postgres"
#   subnet_ids = [for s in values(aws_subnet.public) : s.id]
#
#   tags = merge(local.tags, {
#     Name = "${local.resource_prefix}-subnet-postgres"
#   })
# }

# resource "aws_db_instance" "postgres" {
#   identifier             = "${local.resource_prefix}-postgres"
#   engine                 = "postgres"
#   engine_version         = "14.18"
#   instance_class         = "db.t3.small"
#   allocated_storage      = 20
#   max_allocated_storage  = 100
#   storage_type           = "gp3"
#
#   db_name                = local.postgres_db_name
#   username               = local.postgres_usr
#   password               = local.postgres_pwd
#
#   vpc_security_group_ids = [aws_security_group.sg_postgres.id]
#   db_subnet_group_name   = aws_db_subnet_group.postgres_subnet_group.name
#
#   backup_retention_period = 0
#
#   multi_az               = false
#   publicly_accessible    = true
#   skip_final_snapshot    = true
#
#   tags = merge(local.tags, {
#     Name = "${local.resource_prefix}-postgres"
#   })
# }
