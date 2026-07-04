terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "app_sg" {
  name        = "${var.instance_name}-sg"
  description = "Allow SSH and HTTP access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.app_sg.id]

  tags = {
    Name = var.instance_name
  }

  user_data = <<-EOF
    #!/bin/bash
    set -e
    apt-get update
    apt-get install -y python3-pip python3-venv nginx
    mkdir -p /home/ubuntu/incident-management-app
    chown -R ubuntu:ubuntu /home/ubuntu/incident-management-app
  EOF

  provisioner "file" {
    source      = "${path.module}/../app.py"
    destination = "/home/ubuntu/incident-management-app/app.py"

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(var.private_key_path)
    }
  }

  provisioner "file" {
    source      = "${path.module}/../requirements.txt"
    destination = "/home/ubuntu/incident-management-app/requirements.txt"

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(var.private_key_path)
    }
  }

  provisioner "remote-exec" {
    inline = [
      "cd /home/ubuntu/incident-management-app",
      "python3 -m venv venv",
      "source venv/bin/activate",
      "pip install -r requirements.txt",
      "sudo tee /etc/systemd/system/incident-app.service >/dev/null <<'EOF_SERVICE'\n[Unit]\nDescription=Incident Management Flask App\nAfter=network.target\n\n[Service]\nUser=ubuntu\nGroup=www-data\nWorkingDirectory=/home/ubuntu/incident-management-app\nEnvironment=\"PATH=/home/ubuntu/incident-management-app/venv/bin\"\nExecStart=/home/ubuntu/incident-management-app/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 app:app\nRestart=always\n\n[Install]\nWantedBy=multi-user.target\nEOF_SERVICE\nsudo systemctl daemon-reload\nsudo systemctl enable --now incident-app\nsudo tee /etc/nginx/sites-available/incident-app >/dev/null <<'EOF_NGINX'\nserver {\n    listen 80;\n    server_name _;\n\n    location / {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n    }\n}\nEOF_NGINX\nsudo ln -sfn /etc/nginx/sites-available/incident-app /etc/nginx/sites-enabled/default\nsudo nginx -t\nsudo systemctl restart nginx"
    ]

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(var.private_key_path)
    }
  }
}
