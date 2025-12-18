resource "aws_security_group" "sg_mwaa" {
  name        = "${local.resource_prefix}-sg-mwaa"
  description = "No Ingress Security Group"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
    description = "Allow all traffic within this security group"
  }

  # Egress rule to allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-sg-mwaa"
  })
}

resource "aws_s3_object" "requirements" {
  depends_on = [
    aws_s3_bucket.mwaa
  ]
  bucket = aws_s3_bucket.mwaa.id
  key    = "mwaa/requirements.txt"
  source = "${path.module}/../requirements.txt"
  etag   = filemd5("${path.module}/../requirements.txt")
}

resource "aws_mwaa_environment" "mwaa" {
  depends_on = [
    aws_s3_object.requirements
  ]
  name               = local.resource_prefix
  execution_role_arn = aws_iam_role.mwaa_role.arn
  airflow_version = "2.8.1"

  source_bucket_arn = aws_s3_bucket.mwaa.arn
  dag_s3_path        = "mwaa/dags/"
  requirements_s3_path = "mwaa/requirements.txt"
  # kms_key = aws_kms_alias.mwaa.target_key_arn

  environment_class = "mw1.small"
  webserver_access_mode = "PUBLIC_ONLY"

  network_configuration {
    subnet_ids         = local.private_subnet_ids
    security_group_ids = [aws_security_group.sg_mwaa.id]
  }

  # max_webservers = 2
  # min_webservers = 2
  # schedulers = 2
  # max_workers = 10
  # min_workers = 2
  # plugins_s3_object_version = "1.10.12"
  # plugins_s3_path = "plugins/plugins.zip"
  # plugins_s3_path = "plugins.zip"
  # startup_script_s3_object_version = aws_s3_object.startup_script.etag
  # startup_script_s3_path = "s3://${data.aws_s3_bucket.dags.bucket}/${local.namespace}/startup.sh"
  # weekly_maintenance_window_start = "SUN:05:00"

  airflow_configuration_options = {
    "core.load_examples" = "False"
    "core.store_serialized_dags" = "True"
    "webserver.expose_config" = "True"
    "scheduler.dag_dir_list_interval" = "60"
    # "webserver.default_ui_timezone" = "America/Los_Angeles"
  }

  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }

    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }

    task_logs {
      enabled   = true
      log_level = "INFO"
    }

    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }

    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  tags = merge(local.tags, {
    Name = local.resource_prefix
  })
}

output "mwaa_sg" {
  description = "Security Group for MWAA"
  value = aws_security_group.sg_mwaa.id
}