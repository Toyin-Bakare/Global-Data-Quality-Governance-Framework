resource "random_id" "suffix" { byte_length = 3 }

locals {
  suffix = random_id.suffix.hex
  raw_bucket_name     = "${var.name_prefix}-datalake-raw-${local.suffix}"
  curated_bucket_name = "${var.name_prefix}-datalake-curated-${local.suffix}"
  logs_bucket_name    = "${var.name_prefix}-datalake-logs-${local.suffix}"
  buckets = {
    raw     = local.raw_bucket_name
    curated = local.curated_bucket_name
    logs    = local.logs_bucket_name
  }
}

resource "aws_s3_bucket" "b" {
  for_each = local.buckets
  bucket   = each.value
  tags     = merge(var.tags, { Name = each.value, purpose = "datalake-${each.key}" })
}

resource "aws_s3_bucket_public_access_block" "block" {
  for_each = aws_s3_bucket.b
  bucket   = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  for_each = aws_s3_bucket.b
  bucket   = each.value.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_versioning" "versioning" {
  for_each = aws_s3_bucket.b
  bucket   = each.value.id
  versioning_configuration {
    status = each.key == "curated" ? "Suspended" : "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  for_each = aws_s3_bucket.b
  bucket   = each.value.id

  rule {
    id     = "expire-noncurrent"
    status = "Enabled"
    noncurrent_version_expiration { noncurrent_days = 30 }
  }

  rule {
    id     = "intelligent-tiering"
    status = "Enabled"
    transition { days = 30 storage_class = "INTELLIGENT_TIERING" }
  }
}
