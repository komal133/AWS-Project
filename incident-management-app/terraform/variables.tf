variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "instance_name" {
  description = "Name tag for the EC2 resources"
  type        = string
  default     = "incident-management-app"
}

variable "key_name" {
  description = "Existing EC2 key pair name"
  type        = string
}

variable "allowed_cidr" {
  description = "CIDR allowed to access SSH and HTTP"
  type        = string
  default     = "0.0.0.0/0"
}

variable "repo_url" {
  description = "Git repository URL for the Flask app"
  type        = string
}
