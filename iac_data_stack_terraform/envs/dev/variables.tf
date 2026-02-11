variable "name_prefix" {
  type        = string
  description = "Prefix for resource naming."
  default     = "data-stack-dev"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR."
  default     = "10.20.0.0/16"
}

variable "db_name" {
  type        = string
  default     = "platform"
}

variable "db_username" {
  type        = string
  default     = "platform_admin"
}

variable "tags" {
  type        = map(string)
  default = {
    project = "iac-data-stack"
    env     = "dev"
  }
}
