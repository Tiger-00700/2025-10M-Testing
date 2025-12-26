# Cloud Migration Infrastructure as Code
# Terraform模块示例 - 云迁移基础设施自动化
#
# 功能特性:
# - 多云环境支持
# - 模块化架构
# - 状态管理
# - 依赖处理
# - 成本优化

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }

  # 状态管理配置
  backend "s3" {
    bucket         = "migration-terraform-state"
    key            = "migration/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "migration-terraform-locks"
  }
}

# 输入变量
variable "environment" {
  description = "部署环境"
  type        = string
  default     = "migration"

  validation {
    condition     = contains(["dev", "staging", "migration", "prod"], var.environment)
    error_message = "环境必须是: dev, staging, migration, prod"
  }
}

variable "region" {
  description = "部署区域"
  type        = string
  default     = "us-east-1"
}

variable "migration_wave" {
  description = "迁移波次标识"
  type        = string
  default     = "wave-001"
}

variable "resource_tags" {
  description = "资源标签"
  type        = map(string)
  default = {
    Project     = "Cloud Migration"
    Environment = "Migration"
    ManagedBy   = "Terraform"
  }
}

variable "vpc_config" {
  description = "VPC网络配置"
  type = object({
    cidr_block           = string
    enable_dns_hostnames = bool
    enable_dns_support   = bool
  })
  default = {
    cidr_block           = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
  }
}

variable "instance_config" {
  description = "EC2实例配置"
  type = object({
    instance_type = string
    ami_id        = string
    key_name      = string
    volume_size   = number
  })
  default = {
    instance_type = "t3.medium"
    ami_id        = "ami-0abcdef1234567890"
    key_name      = "migration-key"
    volume_size   = 50
  }
}

variable "database_config" {
  description = "数据库配置"
  type = object({
    engine         = string
    engine_version = string
    instance_class = string
    allocated_storage = number
    db_name        = string
    username       = string
  })
  default = {
    engine            = "mysql"
    engine_version    = "8.0"
    instance_class    = "db.t3.medium"
    allocated_storage = 100
    db_name           = "migrated_db"
    username          = "admin"
  }
  sensitive = true
}

# 数据源
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# 本地值
locals {
  common_tags = merge(var.resource_tags, {
    Environment   = var.environment
    MigrationWave = var.migration_wave
    CreatedBy     = "Terraform"
    CreatedAt     = timestamp()
  })

  # 资源命名约定
  name_prefix = "migration-${var.migration_wave}"

  # 子网配置
  public_subnets = [
    for i, az in data.aws_availability_zones.available.names :
    cidrsubnet(var.vpc_config.cidr_block, 8, i)
  ]

  private_subnets = [
    for i, az in data.aws_availability_zones.available.names :
    cidrsubnet(var.vpc_config.cidr_block, 8, i + 10)
  ]
}

# VPC和网络资源
module "vpc" {
  source = "./modules/vpc"

  name               = "${local.name_prefix}-vpc"
  cidr_block         = var.vpc_config.cidr_block
  enable_dns_hostnames = var.vpc_config.enable_dns_hostnames
  enable_dns_support   = var.vpc_config.enable_dns_support

  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets

  tags = local.common_tags
}

# 安全组
resource "aws_security_group" "migration_sg" {
  name_prefix = "${local.name_prefix}-sg"
  vpc_id      = module.vpc.vpc_id

  # SSH访问
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # 限制为内部网络
  }

  # HTTP/HTTPS访问
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 数据库访问
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.db_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-security-group"
  })
}

resource "aws_security_group" "db_sg" {
  name_prefix = "${local.name_prefix}-db-sg"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.migration_sg.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-security-group"
  })
}

# EC2实例
resource "aws_instance" "migration_servers" {
  count = 3  # 为高可用性创建多个实例

  ami           = var.instance_config.ami_id
  instance_type = var.instance_config.instance_type
  key_name      = var.instance_config.key_name

  vpc_security_group_ids = [aws_security_group.migration_sg.id]
  subnet_id              = module.vpc.public_subnets[count.index % length(module.vpc.public_subnets)]

  root_block_device {
    volume_size = var.instance_config.volume_size
    volume_type = "gp3"
    encrypted   = true

    tags = merge(local.common_tags, {
      Name = "${local.name_prefix}-server-${count.index + 1}-root"
    })
  }

  user_data = templatefile("${path.module}/templates/user_data.sh.tpl", {
    migration_wave = var.migration_wave
    environment    = var.environment
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-server-${count.index + 1}"
    Role = "MigrationServer"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# RDS数据库实例
resource "aws_db_instance" "migration_db" {
  identifier = "${local.name_prefix}-db"

  engine         = var.database_config.engine
  engine_version = var.database_config.engine_version
  instance_class = var.database_config.instance_class

  allocated_storage = var.database_config.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.database_config.db_name
  username = var.database_config.username
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.migration_db_subnet.name

  multi_az               = true
  backup_retention_period = 7
  skip_final_snapshot    = false
  final_snapshot_identifier = "${local.name_prefix}-db-final-snapshot"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database"
  })
}

resource "aws_db_subnet_group" "migration_db_subnet" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

# S3存储桶用于迁移数据
resource "aws_s3_bucket" "migration_data" {
  bucket = "${local.name_prefix}-data-${data.aws_caller_identity.current.account_id}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-data-bucket"
  })
}

resource "aws_s3_bucket_versioning" "migration_data_versioning" {
  bucket = aws_s3_bucket.migration_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "migration_data_encryption" {
  bucket = aws_s3_bucket.migration_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "migration_data_lifecycle" {
  bucket = aws_s3_bucket.migration_data.id

  rule {
    id     = "migration_data_lifecycle"
    status = "Enabled"

    # 迁移完成后30天删除临时数据
    expiration {
      days = 30
    }

    # 过渡到IA存储类
    transition {
      days          = 7
      storage_class = "STANDARD_IA"
    }

    # 过渡到Glacier
    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}

# CloudWatch监控和告警
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${local.name_prefix}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "迁移服务器CPU使用率过高"

  dimensions = {
    InstanceId = aws_instance.migration_servers[0].id
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "db_high_cpu" {
  alarm_name          = "${local.name_prefix}-db-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "迁移数据库CPU使用率过高"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.migration_db.id
  }

  tags = local.common_tags
}

# IAM角色和策略
resource "aws_iam_role" "migration_role" {
  name = "${local.name_prefix}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "migration_ssm" {
  role       = aws_iam_role.migration_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "migration_s3" {
  role       = aws_iam_role.migration_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "migration_profile" {
  name = "${local.name_prefix}-instance-profile"
  role = aws_iam_role.migration_role.name
}

# 输出
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "migration_servers" {
  description = "迁移服务器信息"
  value = {
    for idx, server in aws_instance.migration_servers :
    "server-${idx + 1}" => {
      instance_id = server.id
      public_ip   = server.public_ip
      private_ip  = server.private_ip
    }
  }
}

output "database_endpoint" {
  description = "数据库端点"
  value       = aws_db_instance.migration_db.endpoint
  sensitive   = true
}

output "data_bucket" {
  description = "数据存储桶名称"
  value       = aws_s3_bucket.migration_data.bucket
}

output "migration_wave" {
  description = "迁移波次"
  value       = var.migration_wave
}

# 成本估算
resource "aws_budgets_budget" "migration_budget" {
  name         = "${local.name_prefix}-budget"
  budget_type  = "COST"
  limit_amount = "1000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = ["MigrationWave$${var.migration_wave}"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_email_addresses = ["migration-alerts@example.com"]
  }
}