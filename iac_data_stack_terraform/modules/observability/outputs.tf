output "platform_log_group" { value = aws_cloudwatch_log_group.platform.name }
output "alarm_rds_cpu_high" { value = aws_cloudwatch_metric_alarm.rds_cpu_high.alarm_name }
