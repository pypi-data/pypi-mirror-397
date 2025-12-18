variable "region" {
    description = "AWS region for the resources"
    type        = string
    default     = "us-west-1"
}

variable "environment" {
  description = "Data environment (e.g. dev, qa, prod) - a unique name used to isolate multiple deployments in the same account"
  type        = string
  default     = "jc"
}

variable "code_version" {
  description = "Code version (defaults to VERSION file, must match deploy.sh)"
  type        = string
  default     = ""  # Empty means use VERSION file
}