variable "email" {
  description = "User email for notifications"
  type        = string
  default     = "jclark@shutterfly.com"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-1"
}

variable "cidr_block" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.1.0.0/16"
}

variable "environment" {
  description = "Data environment (e.g. dev, qa, prod) - a unique name used to isolate multiple deployments in the same account"
  type        = string
  default     = "jc"
}
