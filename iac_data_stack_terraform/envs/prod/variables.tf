variable "name_prefix" { type = string default = "data-stack-prod" }
variable "vpc_cidr" { type = string default = "10.30.0.0/16" }
variable "db_name" { type = string default = "platform" }
variable "db_username" { type = string default = "platform_admin" }
variable "tags" {
  type = map(string)
  default = { project = "iac-data-stack", env = "prod" }
}
