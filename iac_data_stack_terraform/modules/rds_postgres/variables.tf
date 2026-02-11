variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "allowed_cidr_blocks" { type = list(string) }
variable "db_name" { type = string }
variable "db_username" { type = string }
variable "instance_class" { type = string default = "db.t4g.micro" }
variable "allocated_storage_gb" { type = number default = 20 }
variable "multi_az" { type = bool default = false }
variable "backup_retention_days" { type = number default = 1 }
variable "tags" { type = map(string) default = {} }
