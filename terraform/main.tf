terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = var.region
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    "Name" = "5data-main-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    "Name" = "5data-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.0.0/26"
  availability_zone       = "eu-west-1a"
  map_public_ip_on_launch = true
  tags = {
    "Name" = "5data-main-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags = {
    "Name" = "5data-public-route-table"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_security_group" "main_instance_sg" {
  vpc_id = aws_vpc.main.id
  tags = {
    "Name" = "5data-main-instance-sg"
  }
}

resource "aws_security_group_rule" "main_instance_ssh" {
  security_group_id = aws_security_group.main_instance_sg.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_blocks       = [local.my_public_cidr]
}

resource "aws_security_group_rule" "main_instance_scheduler" {
  security_group_id = aws_security_group.main_instance_sg.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 8080
  to_port           = 8080
  cidr_blocks       = [local.my_public_cidr]
}

resource "aws_security_group_rule" "main_instance_egress" {
  security_group_id = aws_security_group.main_instance_sg.id
  type              = "egress"
  protocol          = "tcp"
  from_port         = 0
  to_port           = 65535
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_iam_role" "ec2_s3_access_role" {
  name               = "ec2_s3_access_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "s3_emr_access_policy" {
  name = "s3_emr_access_policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*",
        "elasticmapreduce:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ec2_s3_access_policy_attach" {
  role       = aws_iam_role.ec2_s3_access_role.name
  policy_arn = aws_iam_policy.s3_emr_access_policy.arn
}

resource "aws_iam_instance_profile" "main_instance_profile" {
  name = "main_instance_profile"
  role = aws_iam_role.ec2_s3_access_role.name
}

resource "aws_instance" "main_instance" {
  ami                  = var.amis[var.region]
  instance_type        = "t2.small"
  subnet_id            = aws_subnet.public.id
  key_name             = var.key_name
  security_groups      = [aws_security_group.main_instance_sg.id]
  iam_instance_profile = aws_iam_instance_profile.main_instance_profile.name
  user_data            = data.template_file.main_instance_user_data.rendered
  tags = {
    "Name" = "5data-main-instance"
  }
}

resource "null_resource" "main_instance_provisioning" {
  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = aws_instance.main_instance.public_ip
    private_key = data.template_file.key.rendered
  }
  provisioner "file" {
    source      = "../scripts"
    destination = "/home/ec2-user"
  }
  provisioner "file" {
    source      = "../data"
    destination = "/home/ec2-user"
  }
  provisioner "file" {
    source      = "../sources"
    destination = "/home/ec2-user"
  }
  provisioner "file" {
    source      = "../dags"
    destination = "/home/ec2-user"
  }
  # Following command is a containment, had a race condition with ec2 user data, and a deadlock with user groups not refreshing
  provisioner "remote-exec" {
    inline = [
      "until [ $(systemctl is-active docker) = 'active' ]; do echo 'waiting for docker to start' && sleep 1; done",
      "sleep 1.5"
    ]
  }
  provisioner "remote-exec" {
    inline = [
      "cd ~/",
      "chmod +x scripts/*",
      "./scripts/start_erp.sh",
      "./scripts/start_scheduler.sh -b ${var.bucket_name}"
    ]
  }
}

resource "aws_s3_bucket" "main_bucket" {
  bucket = var.bucket_name
  acl    = "private"
  tags = {
    "Name" = "5DATA bucket"
  }
}

# === EMR ===

resource "aws_s3_bucket_object" "spark_jobs" {
  for_each = fileset("../spark/", "*")

  bucket = aws_s3_bucket.main_bucket.id
  key    = "spark/${each.value}"
  source = "../spark/${each.value}"
  etag   = filemd5("../spark/${each.value}")
}

resource "aws_s3_bucket_object" "emr_bootstrap" {
  for_each = fileset("../scripts/EMR/", "*")

  bucket = aws_s3_bucket.main_bucket.id
  key    = "EMR/${each.value}"
  source = "../scripts/EMR/${each.value}"
  etag   = filemd5("../scripts/EMR/${each.value}")
}

resource "aws_security_group" "emr_cluster_sg" {
  vpc_id = aws_vpc.main.id
  tags = {
    "Name" = "5data-emr-sg"
  }
}

resource "aws_security_group_rule" "emr_master_ssh" {
  security_group_id = aws_security_group.emr_cluster_sg.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_blocks       = [local.my_public_cidr]
}

resource "aws_security_group_rule" "emr_hue" {
  security_group_id = aws_security_group.emr_cluster_sg.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 8888
  to_port           = 8888
  cidr_blocks       = [local.my_public_cidr]
}

resource "aws_security_group_rule" "emr_egress" {
  security_group_id = aws_security_group.emr_cluster_sg.id
  type              = "egress"
  protocol          = "tcp"
  from_port         = 0
  to_port           = 65535
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_emr_cluster" "emr_cluster" {
  name          = "5data-emr-cluster"
  release_label = "emr-5.32.0"
  applications  = ["Hadoop", "Spark", "Hive", "Hue"]

  termination_protection            = false
  keep_job_flow_alive_when_no_steps = true

  log_uri = "s3://${var.bucket_name}"

  ec2_attributes {
    subnet_id                         = aws_subnet.public.id
    key_name                          = var.key_name
    emr_managed_master_security_group = aws_security_group.emr_cluster_sg.id
    emr_managed_slave_security_group  = aws_security_group.emr_cluster_sg.id
    instance_profile                  = var.emr_instance_profile
  }

  master_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 1
  }

  service_role = var.emr_service_role

  tags = {
    "Name" = "5data-emr-cluster"
  }
}