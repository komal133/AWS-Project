output "instance_public_ip" {
  value = aws_instance.app.public_ip
}

output "load_balancer_dns_name" {
  value = aws_lb.this.dns_name
}

output "app_url" {
  value = "http://${aws_lb.this.dns_name}/"
}
