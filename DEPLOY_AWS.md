AWS Deployment guide (ECR + ECS Fargate + RDS)

This document outlines steps to deploy the Django app container to AWS using ECR for images, ECS (Fargate) for running the container, and RDS (MySQL) as the managed database. It assumes you have the AWS CLI configured with appropriate IAM permissions.

High-level steps
1. Build and test locally with Docker Compose.
2. Create an ECR repository and push the Docker image.
3. Create an RDS MySQL instance (or use an existing DB), ensure security groups allow the ECS tasks to connect.
4. Create an ECS cluster and an ECS Task Definition (Fargate) that references the image in ECR.
5. Create a Service with an Application Load Balancer (ALB) and set up target group and health checks.
6. Configure environment variables (SECRET_KEY, DB credentials, ALLOWED_HOSTS, etc.) in the Task Definition or via AWS Secrets Manager.

Commands (examples)

# 1) Build & tag image locally
docker build -t meetingapp-web:latest .

# 2) Create ECR repo and push
aws ecr create-repository --repository-name meetingapp-web --region us-east-1
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag meetingapp-web:latest <account>.dkr.ecr.us-east-1.amazonaws.com/meetingapp-web:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/meetingapp-web:latest

# 3) Create RDS MySQL (example)
aws rds create-db-instance --db-instance-identifier meetingapp-db --db-instance-class db.t3.micro --engine mysql --master-username admin --master-user-password <password> --allocated-storage 20

# 4) Create ECS Task Definition - use the provided `ecs-task-def.json` as a template and register it
aws ecs register-task-definition --cli-input-json file://ecs-task-def.json

# 5) Create an ECS Service from the Task Definition, attach ALB, and deploy.

Security notes
- Store sensitive values (DB password, SECRET_KEY) in AWS Secrets Manager and reference in the Task Definition environment variables.
- Use security groups to restrict access to RDS and ALB.

If you want, I can:
- produce a fully parameterized `ecs-task-def.json` containing the container definition using the ECR image URL and environment variable placeholders, and
- optionally add a small `deploy.sh` script that automates ECR login, tagging, and pushing the image to ECR.
