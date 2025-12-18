resource "aws_s3_bucket" "code" {
  bucket = "${local.resource_prefix}-code-${local.region}"
  force_destroy = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-code-${local.region}"
  })
}

resource "aws_s3_bucket_versioning" "code" {
  bucket = aws_s3_bucket.code.id

  versioning_configuration {
    status = "Enabled"
  }
}
