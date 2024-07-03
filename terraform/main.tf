# aws provider
provider "aws" {
    region = "ap-southeast-1"
    access_key = var.access_key
    secret_key = var.secret_key
}

# app node setup
resource "aws_instance" "app" {
  ami           = "ami-0b287aaaab87c114d"
  instance_type = "t3.2xlarge"
  vpc_security_group_ids = ["sg-0bf97419aaad88160"] // if no security group needs be specified, delete this line

  user_data = <<-EOF
                #!/bin/bash
                sudo yum update -y
                sudo yum install git -y
                sudo yum install python3 -y
                sudo yum install python3-pip -y
                git clone https://github.com/sillyjason/agentic_customer_service_with_couchbase
                cd agentic_customer_service_with_couchbase
                python3 -m venv venv
                source venv/bin/activate
                pip install -r requirements.txt
                EOF

  tags = {
    Name = "agentic-customer-support-lc-cb"
  }
}


# Couchbase node setup
resource "aws_instance" "cb_server" {
  ami           = "ami-0b287aaaab87c114d"
  instance_type = "t3.2xlarge"
  vpc_security_group_ids = ["sg-0bf97419aaad88160"] // if no security group needs be specified, delete this line

  user_data = <<-EOF
                #!/bin/bash
                sudo wget https://packages.couchbase.com/releases/7.6.1/couchbase-server-enterprise-7.6.1-linux.x86_64.rpm
                yes | sudo yum install ./couchbase-server*.rpm
                sudo systemctl start couchbase-server
                EOF

  tags = {
    Name = "couchbase-server-7.6"
  }
}


# output node hostnames 
output "cb_instance_public_dns" {
  value = aws_instance.cb_server.public_dns
}

output "app_instance_public_dns" {
  value = aws_instance.app.public_dns
}