output "cluster_name" { value = aws_ecs_cluster.this.name }
output "cluster_arn" { value = aws_ecs_cluster.this.arn }
output "task_execution_role_arn" { value = aws_iam_role.task_execution.arn }
output "task_role_arn" { value = aws_iam_role.task.arn }
output "log_group_name" { value = aws_cloudwatch_log_group.tasks.name }
output "tasks_security_group_id" { value = aws_security_group.tasks.id }
output "private_subnet_ids" { value = var.private_subnet_ids }
