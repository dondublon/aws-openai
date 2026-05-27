# Deploy RAG agent on AWS - Task Definition
## Creating CloudFormation stack from template for following architecture
### Architecture
- HTTP Gateway with proxying POST /chat request and cognito authorizer and VPC Link integration
- HTTP Gateway with login Lambda function integration
- VPC Link
- Inner Application Load Balancer / Target group 
- Target is EC2 instance running docker container 
- Login Lambda function created from docker container
## Testing
- Postman
