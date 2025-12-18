resource "aws_s3_bucket" "data" {
  bucket = "${local.resource_prefix}-data-${local.region}"
  force_destroy = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-data-${local.region}"
  })
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}
