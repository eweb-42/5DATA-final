variable "region" {
  default = "eu-west-1"
}

variable "amis" {
  type = map
  default = {
    "eu-west-1" = "ami-01720b5f421cf0179"
  }
}

data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

locals {
  my_public_cidr = "${chomp(data.http.myip.body)}/32"
}

variable "key_path" {
  description = "The path of the key to connect to the instance"
}

variable "key_name" {
  description = "The name of the key pair to connect to the instance"
}

variable "docker_username" {
  description = "Your Docker Hub username, for the main instance"
}

variable "docker_password" {
  description = "Your Docker Hub password, for the main instance"
}

data "template_file" "main_instance_user_data" {
  template = file("./user_data/main_instance.sh")
  vars = {
    "docker_username" = "${var.docker_username}"
    "docker_password" = "${var.docker_password}"
  }
}

data "template_file" "key" {
  template = file(var.key_path)
}

variable "bucket_name" {
  description = "The name of the S3 bucket"
}

variable "emr_service_role" {
  description = "The service role for Elastic Map Reduce"
}

variable "emr_instance_profile" {
  description = "The instance profile for the EC2 instances of the cluster"
}