resource "random_password" "db" {
  length  = 20
  special = true
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-dbsubnets"
  subnet_ids = var.private_subnet_ids
  tags       = merge(var.tags, { Name = "${var.name_prefix}-dbsubnets" })
}

resource "aws_security_group" "db" {
  name        = "${var.name_prefix}-rds-sg"
  description = "RDS Postgres access (restricted)"
  vpc_id      = var.vpc_id
  tags        = merge(var.tags, { Name = "${var.name_prefix}-rds-sg" })
}

resource "aws_security_group_rule" "ingress" {
  type              = "ingress"
  security_group_id = aws_security_group.db.id
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = var.allowed_cidr_blocks
}

resource "aws_security_group_rule" "egress" {
  type              = "egress"
  security_group_id = aws_security_group.db.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_db_instance" "this" {
  identifier              = "${var.name_prefix}-postgres"
  engine                  = "postgres"
  engine_version          = "16.3"
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage_gb

  db_name                 = var.db_name
  username                = var.db_username
  password                = random_password.db.result

  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [aws_security_group.db.id]

  publicly_accessible     = false
  multi_az                = var.multi_az
  backup_retention_period = var.backup_retention_days

  storage_encrypted       = true
  skip_final_snapshot     = true

  tags = merge(var.tags, { Name = "${var.name_prefix}-postgres" })
}
