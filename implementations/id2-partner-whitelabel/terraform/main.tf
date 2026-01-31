################################################################################
# Partner Whitelabel Infrastructure - Terraform Configuration
#
# This Terraform configuration provisions the necessary infrastructure
# for a partner-whitelabel instance of the WebWaka platform.
################################################################################

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  host                   = aws_eks_cluster.partner.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.partner.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.partner.token
}

################################################################################
# Variables
################################################################################

variable "partner_id" {
  description = "Unique identifier for the partner"
  type        = string
}

variable "partner_name" {
  description = "Human-readable name of the partner"
  type        = string
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "database_size" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.small"
}

variable "storage_size" {
  description = "EBS storage size in GB"
  type        = number
  default     = 100
}

################################################################################
# VPC and Networking
################################################################################

resource "aws_vpc" "partner" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "vpc-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.partner.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name    = "subnet-public-${var.partner_id}-${count.index + 1}"
    Partner = var.partner_id
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.partner.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name    = "subnet-private-${var.partner_id}-${count.index + 1}"
    Partner = var.partner_id
  }
}

resource "aws_internet_gateway" "partner" {
  vpc_id = aws_vpc.partner.id

  tags = {
    Name    = "igw-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.partner.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.partner.id
  }

  tags = {
    Name    = "rt-public-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

################################################################################
# Security Groups
################################################################################

resource "aws_security_group" "eks" {
  name        = "sg-eks-${var.partner_id}"
  description = "Security group for EKS cluster"
  vpc_id      = aws_vpc.partner.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "sg-eks-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_security_group" "rds" {
  name        = "sg-rds-${var.partner_id}"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.partner.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "sg-rds-${var.partner_id}"
    Partner = var.partner_id
  }
}

################################################################################
# EKS Cluster
################################################################################

resource "aws_iam_role" "eks_cluster" {
  name = "role-eks-cluster-${var.partner_id}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_eks_cluster" "partner" {
  name            = "cluster-${var.partner_id}"
  version         = "1.27"
  role_arn        = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids              = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
    security_group_ids      = [aws_security_group.eks.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  tags = {
    Name    = "cluster-${var.partner_id}"
    Partner = var.partner_id
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}

################################################################################
# EKS Node Group
################################################################################

resource "aws_iam_role" "eks_nodes" {
  name = "role-eks-nodes-${var.partner_id}"

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
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_eks_node_group" "partner" {
  cluster_name    = aws_eks_cluster.partner.name
  node_group_name = "ng-${var.partner_id}"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }

  instance_types = [var.instance_type]

  tags = {
    Name    = "ng-${var.partner_id}"
    Partner = var.partner_id
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
  ]
}

################################################################################
# RDS Database
################################################################################

resource "aws_db_subnet_group" "partner" {
  name       = "dbsg-${var.partner_id}"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name    = "dbsg-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_rds_cluster" "partner" {
  cluster_identifier      = "db-${var.partner_id}"
  engine                  = "aurora-postgresql"
  engine_version          = "15.2"
  database_name           = replace(var.partner_id, "-", "_")
  master_username         = "admin"
  master_password         = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.partner.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  skip_final_snapshot     = var.environment != "production"
  backup_retention_period = var.environment == "production" ? 30 : 7

  tags = {
    Name    = "db-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_rds_cluster_instance" "partner" {
  count              = var.environment == "production" ? 2 : 1
  cluster_identifier = aws_rds_cluster.partner.id
  instance_class     = var.database_size
  engine              = aws_rds_cluster.partner.engine
  engine_version      = aws_rds_cluster.partner.engine_version

  tags = {
    Name    = "db-instance-${var.partner_id}-${count.index + 1}"
    Partner = var.partner_id
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

################################################################################
# S3 Storage
################################################################################

resource "aws_s3_bucket" "partner_storage" {
  bucket = "storage-${var.partner_id}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name    = "storage-${var.partner_id}"
    Partner = var.partner_id
  }
}

resource "aws_s3_bucket_versioning" "partner_storage" {
  bucket = aws_s3_bucket.partner_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "partner_storage" {
  bucket = aws_s3_bucket.partner_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

################################################################################
# Data Sources
################################################################################

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_eks_cluster_auth" "partner" {
  name = aws_eks_cluster.partner.name
}

################################################################################
# Outputs
################################################################################

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.partner.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.partner.endpoint
}

output "cluster_ca_certificate" {
  description = "EKS cluster CA certificate"
  value       = aws_eks_cluster.partner.certificate_authority[0].data
  sensitive   = true
}

output "namespace" {
  description = "Kubernetes namespace for partner"
  value       = "partner-${var.partner_id}"
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_rds_cluster.partner.endpoint
}

output "database_reader_endpoint" {
  description = "RDS database reader endpoint"
  value       = aws_rds_cluster.partner.reader_endpoint
}

output "s3_bucket_name" {
  description = "S3 bucket name for partner storage"
  value       = aws_s3_bucket.partner_storage.id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.partner.id
}
