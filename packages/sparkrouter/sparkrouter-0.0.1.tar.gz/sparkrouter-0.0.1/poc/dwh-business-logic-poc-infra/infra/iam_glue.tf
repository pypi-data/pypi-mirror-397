data "aws_iam_policy_document" "glue_policy_document" {

  statement {
    sid    = "GlueSendEmail"
    effect = "Allow"
    actions = [
      "ses:SendRawEmail"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "GlueSendSNS"
    effect = "Allow"
    actions = [
      "sns:Publish"
    ]
    resources = ["*"]
  }

  statement {
    sid = "S3CodeReadAccess"
    effect = "Allow"
    actions = [
      "s3:Get*",
      "s3:List*",
    ]
    resources = [
      aws_s3_bucket.code.arn,
      "${aws_s3_bucket.code.arn}/*",
    ]
  }

  statement {
    sid = "S3DataFullAccess"
    effect = "Allow"
    actions = [
      "s3:Get*",
      "s3:List*",
      "s3:Put*",
      "s3:*Object",
      "s3:Delete*",
    ]
    resources = [
      aws_s3_bucket.data.arn,
      "${aws_s3_bucket.data.arn}/*",
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

  # statement {
  #   sid    = "GlueGetConnection"
  #   effect = "Allow"
  #   actions = [
  #     "glue:GetConnection"
  #   ]
  #   resources = [
  #     "arn:aws:glue:${local.region}:${local.account_id}:catalog",
  #     aws_glue_connection.postgres_connection.arn
  #   ]
  # }
}

resource "aws_iam_policy" "glue_policy" {
  name = "${local.resource_prefix}-glue"
  policy = data.aws_iam_policy_document.glue_policy_document.json

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-${local.region}-glue"
  })
}

data "aws_iam_policy_document" "glue_role_document" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = [
        "glue.amazonaws.com",
      ]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role" "glue_role" {
  name = "${local.resource_prefix}-glue"
  assume_role_policy = data.aws_iam_policy_document.glue_role_document.json

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-glue"
  })
}

resource "aws_iam_role_policy_attachment" "glue_execution_policy_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_policy.arn
}
