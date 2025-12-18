resource "aws_s3_bucket" "mwaa" {
  bucket = "${local.resource_prefix}-${local.region}"
  force_destroy = true

  tags = merge(local.tags, {
    Name = "${local.resource_prefix}-${local.region}"
  })
}

resource "aws_s3_bucket_versioning" "mwaa" {
  bucket = aws_s3_bucket.mwaa.id

  versioning_configuration {
    status = "Enabled"
  }
}

output "s3_bucket_name" {
  value = aws_s3_bucket.mwaa.bucket
}

