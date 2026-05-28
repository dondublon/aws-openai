# Stateless RAG agent on AWS - Task Definition
## Creating CloudFormation stack from template for following architecture
### Architecture
- HTTP Gateway with proxying POST /chat request  and VPC Link integration (No cognito authorizer required)
- HTTP Gateway with login Lambda function integration
- VPC Link
- Inner Application Load Balancer / Target group 
- ECS/Fargate cluster with autoscaling policy [ 1-4 ] tasks
- Two tables of Dynamo DB with predefined names(one "rag-agent-conversations" with  Partition Key "session_id", other "rag-agent-messages" with Partition Key "session_id"  and Sorted Key "seq")
- Both tables have capacity mode "Provisioned" with auto-scaling for WCU and RCU [1-5]
## Testing
### Functional test 
- Postman
### Loaded test
- Separated Node JS script launched from VSC (script inside the same project-repository)
- using standard fetch (axios not required)
- Playing with interval in setInterval 
- setTime out with closing setInterval and exit from application for example 10 minutes
- the same request for example "Weather in Rehovot" with no session id. It means each request will create new agent session in DynamoDB

# AFTER RUNNING TESTING (EXPERIMENT showing auto scaling with agent running) DON'T FORGET DELETE STACK
