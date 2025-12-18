data "aws_iam_policy_document" "mwaa_policy_document" {
  # todo: create glue role and remove this
  statement {
    sid    = "GlueIAMPassRole"
    effect = "Allow"
    actions = [
      "iam:GetRole",
      "iam:PassRole"
    ]
    resources = [
      local.glue_role_arn
    ]
  }

  statement {
    sid    = "GlueAccess"
    effect = "Allow"
    actions = [
      "glue:CreateJob",
      "glue:UpdateJob",
      "glue:GetJob",
      "glue:GetJobs",
      "glue:DeleteJob",
      "glue:StartJobRun",
      "glue:BatchStopJobRun",
      "glue:GetJobRun",
      "glue:GetJobRuns",
      "glue:ListJobs",
      "glue:TagResource",
      # "glue:GetConnection",
    ]
    resources = ["*"]
  }

  statement {
    sid = "MWAARequiredServicePermissions"
    effect = "Allow"
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeRouteTables",
      "kms:GenerateDataKey*",
      "secretsmanager:GetSecretValue",
      "airflow:PublishMetrics"
    ]
    resources = ["*"]
  }

  statement {
    sid = "S3FullAccess"
    effect = "Allow"
    actions = [
      "s3:Get*",
      "s3:List*",
      "s3:Put*",
      "s3:*Object",
    ]
    resources = [
      aws_s3_bucket.mwaa.arn,
      "${aws_s3_bucket.mwaa.arn}/*",
    ]
  }

  statement {
    sid = "Logs"
    effect = "Allow"
    actions = [
      "logs:*",
    ]
    resources = ["*"]
  }

  statement {
    sid = "Cloudwatch"
    effect = "Allow"
    actions = [
      "cloudwatch:GetMetricStatistics",
      "cloudwatch:ListMetrics",
      "cloudwatch:PutMetricData"
    ]
    resources = ["*"]
  }

  statement {
    sid = "AirflowReadOnlyAccess"
    effect = "Allow"
    actions = [
      "airflow:ListEnvironments",
      "airflow:GetEnvironment",
      "airflow:ListTagsForResource",
      "airflow:CreateCliToken"
    ]
    resources = ["*"]
  }

  statement {
    sid = "KMSAccess"
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey*",
      "kms:Encrypt",
    ]
    resources = [
      # because we are using the default KMS key for MWAA, we need to allow access to it
      # "arn:aws:kms:${local.region}:${local.account_id}:alias/aws/airflow"
      "*"
    ]
  }
}

resource "aws_iam_policy" "mwaa_policy" {
  name = "${local.resource_prefix}-mwaa"
  policy = data.aws_iam_policy_document.mwaa_policy_document.json


  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-mwaa"
  })
}

data "aws_iam_policy_document" "mwaa_role_document" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = [
        "airflow.amazonaws.com",
        "airflow-env.amazonaws.com",
        "glue.amazonaws.com",
      ]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role" "mwaa_role" {
  name = "${local.resource_prefix}-mwaa"
  assume_role_policy = data.aws_iam_policy_document.mwaa_role_document.json

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-mwaa"
  })
}

resource "aws_iam_role_policy_attachment" "mwaa_execution_policy_attachment" {
  role       = aws_iam_role.mwaa_role.name
  policy_arn = aws_iam_policy.mwaa_policy.arn
}