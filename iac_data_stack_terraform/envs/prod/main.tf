module "network" {
  source = "../../modules/network"
  name_prefix = var.name_prefix
  vpc_cidr    = var.vpc_cidr
  az_count    = 3
  tags        = var.tags
}

module "datalake" {
  source      = "../../modules/s3_datalake"
  name_prefix = var.name_prefix
  tags        = var.tags
}

module "rds" {
  source = "../../modules/rds_postgres"

  name_prefix         = var.name_prefix
  vpc_id              = module.network.vpc_id
  private_subnet_ids   = module.network.private_subnet_ids
  allowed_cidr_blocks  = [module.network.vpc_cidr]

  db_name     = var.db_name
  db_username = var.db_username

  instance_class        = "db.t4g.small"
  allocated_storage_gb  = 100
  backup_retention_days = 7
  multi_az              = true

  tags = var.tags
}

module "ecs" {
  source              = "../../modules/ecs_cluster"
  name_prefix         = var.name_prefix
  vpc_id              = module.network.vpc_id
  private_subnet_ids  = module.network.private_subnet_ids
  tags                = var.tags
}

module "observability" {
  source      = "../../modules/observability"
  name_prefix = var.name_prefix
  tags        = var.tags
}
