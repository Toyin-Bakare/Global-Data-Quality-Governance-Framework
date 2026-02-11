output "vpc_id" { value = module.network.vpc_id }
output "private_subnet_ids" { value = module.network.private_subnet_ids }
output "datalake_raw_bucket" { value = module.datalake.raw_bucket_name }
output "rds_endpoint" { value = module.rds.db_endpoint }
output "ecs_cluster_name" { value = module.ecs.cluster_name }
