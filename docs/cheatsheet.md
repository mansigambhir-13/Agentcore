# AgentCore Workshop - Quick Reference Cheat Sheet

## 🚀 Quick Commands

### Setup & Installation
```bash
# Clone repository
git clone <repo-url>
cd bedrock-agentcore-workshop

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deploy prerequisites (self-paced only)
aws cloudformation create-stack \
  --stack-name agentcore-workshop-prereqs \
  --template-body file://prerequisite/cfn/workshop-prerequisites.yaml \
  --capabilities CAPABILITY_IAM

# Enable CloudWatch Transaction Search
aws cloudwatch put-insight-rule \
  --rule-name BedrockAgentCoreObservability \
  --rule-state ENABLED
```

### Run Demo Script
```bash
# Quick 5-minute demo
python demo_agentcore.py --mode quick

# Full 15-minute demo
python demo_agentcore.py --mode full

# Specific lab demo
python demo_agentcore.py --mode specific --lab 3
```

### Jupyter Notebooks
```bash
# Start Jupyter
jupyter notebook

# Open labs in order:
# 1. lab-01-create-an-agent.ipynb
# 2. lab-02-agentcore-memory.ipynb
# 3. lab-03-agentcore-gateway.ipynb
# 4. lab-04-agentcore-runtime.ipynb
# 5. lab-05-frontend.ipynb
# 6. lab-06-cleanup.ipynb
```

---

## 🔑 Key Concepts

### Lab 1: Agent Prototype

**Core Components:**
```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description for LLM"""
    return "result"

model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
agent = Agent(model=model, tools=[my_tool], system_prompt="...")
response = agent("user query")
```

**Tool Requirements:**
- Decorated with `@tool`
- Type hints for parameters
- Docstring for description
- Return string or serializable object

---

### Lab 2: Memory

**Create Memory:**
```python
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name="us-east-1")

strategies = [
    {"USER_PREFERENCE": {
        "name": "Preferences",
        "namespaces": ["support/customer/{actorId}/preferences"]
    }},
    {"SEMANTIC": {
        "name": "Facts",
        "namespaces": ["support/customer/{actorId}/semantic"]
    }}
]

response = memory_client.create_memory_and_wait(
    name="MyMemory",
    strategies=strategies,
    event_expiry_days=90
)
memory_id = response["id"]
```

**Save Events:**
```python
memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_123",
    messages=[
        ("User question", "USER"),
        ("Agent response", "ASSISTANT")
    ]
)
```

**Retrieve Memories:**
```python
memories = memory_client.retrieve_memories(
    memory_id=memory_id,
    namespace="support/customer/user_001/preferences",
    query="user query",
    top_k=3
)
```

**Memory Hooks:**
```python
from strands.hooks import HookProvider, MessageAddedEvent, AfterInvocationEvent

class MyMemoryHooks(HookProvider):
    def retrieve_context(self, event: MessageAddedEvent):
        # Retrieve and inject memories
        pass
        
    def save_interaction(self, event: AfterInvocationEvent):
        # Save to memory
        memory_client.create_event(...)
        
    def register_hooks(self, registry):
        registry.add_callback(MessageAddedEvent, self.retrieve_context)
        registry.add_callback(AfterInvocationEvent, self.save_interaction)

# Use hooks
agent = Agent(model=model, tools=tools, hooks=[memory_hooks])
```

---

### Lab 3: Gateway

**Create Gateway:**
```python
import boto3

gateway_client = boto3.client("bedrock-agentcore-control")

gateway = gateway_client.create_gateway(
    name="my-gateway",
    roleArn="arn:aws:iam::...",
    protocolType="MCP",
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration={
        "customJWTAuthorizer": {
            "allowedClients": ["client-id"],
            "discoveryUrl": "https://..."
        }
    }
)
gateway_id = gateway["gatewayId"]
gateway_url = gateway["gatewayUrl"]
```

**Add Lambda Target:**
```python
# API Spec (api_spec.json)
[
    {
        "name": "my_tool",
        "description": "Tool description",
        "inputSchema": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    }
]

# Create target
gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="LambdaTarget",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": "arn:aws:lambda:...",
                "toolSchema": {"inlinePayload": api_spec}
            }
        }
    },
    credentialProviderConfigurations=[{
        "credentialProviderType": "GATEWAY_IAM_ROLE"
    }]
)
```

**Use Gateway Tools:**
```python
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

mcp_client = MCPClient(
    lambda: streamablehttp_client(
        gateway_url,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
)

with mcp_client:
    gateway_tools = mcp_client.list_tools_sync()
    agent = Agent(model=model, tools=[local_tools] + gateway_tools)
```

---

### Lab 4: Runtime

**Create Runtime-Ready Code:**
```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
async def invoke(payload, context=None):
    user_input = payload.get("prompt", "")
    auth_header = context.request_headers.get('Authorization', '')
    
    # Your agent logic
    agent = Agent(...)
    response = agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()
```

**Deploy with Starter Toolkit:**
```python
from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()

# Configure
runtime.configure(
    entrypoint="my_agent.py",
    execution_role="arn:aws:iam::...",
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region="us-east-1",
    agent_name="my-agent",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "allowedClients": ["client-id"],
            "discoveryUrl": "https://..."
        }
    }
)

# Launch
result = runtime.launch()
agent_arn = result.agent_arn

# Wait for ready
while runtime.status().endpoint["status"] != "READY":
    time.sleep(10)
```

**Invoke Runtime:**
```python
response = runtime.invoke(
    {"prompt": "user query"},
    bearer_token="jwt_token",
    session_id="session_123"
)
print(response["response"])
```

**Configure Headers:**
```python
client = boto3.client("bedrock-agentcore-control")
runtime_id = agent_arn.split("/")[-1]

client.update_agent_runtime(
    agentRuntimeId=runtime_id,
    requestHeaderConfiguration={
        "requestHeaderAllowlist": [
            "Authorization",
            "X-Custom-Header"
        ]
    }
)
```

---

## 📊 AWS Console Navigation

### CloudWatch GenAI Observability
```
AWS Console → CloudWatch → GenAI Observability → Bedrock AgentCore

Views:
  • Agents    - All deployed runtimes
  • Sessions  - User conversations
  • Traces    - Detailed execution flow
  • Metrics   - Performance data
```

### AgentCore Resources
```
AWS Console → Amazon Bedrock → AgentCore

Sections:
  • Memories   - Memory resources
  • Gateways   - Gateway endpoints
  • Runtimes   - Deployed agents
```

### Lambda Functions
```
AWS Console → Lambda → Functions

Filter: "customersupport"
  • Gateway target functions
  • Tool implementations
```

### Cognito
```
AWS Console → Cognito → User Pools

Find: workshop user pool
  • Users - Test accounts
  • App clients - Client IDs
  • Settings - Discovery URL
```

---

## 🔧 Troubleshooting

### Memory Not Processing
```python
# Wait for LTM processing (20-30 seconds)
import time
retries = 0
while retries < 6:
    memories = memory_client.retrieve_memories(...)
    if memories:
        break
    time.sleep(10)
    retries += 1
```

### Gateway Authentication Error
```python
# Refresh expired token (valid 2 hours)
from lab_helpers.utils import get_or_create_cognito_pool

cognito_config = get_or_create_cognito_pool(refresh_token=True)
jwt_token = cognito_config['bearer_token']
```

### Runtime Deployment Failed
```bash
# Check CodeBuild logs
aws codebuild list-builds-for-project \
  --project-name agentcore-runtime-build

# Verify execution role
aws iam get-role --role-name AgentCoreRuntimeRole

# Check Docker
docker ps
docker system prune -a  # Clean if needed
```

### Knowledge Base Sync Issues
```python
# Check sync status
bedrock = boto3.client("bedrock-agent")
job = bedrock.get_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id,
    ingestionJobId=job_id
)
print(job["ingestionJob"]["status"])

# Restart if stuck
bedrock.start_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id
)
```

### Port Already in Use
```bash
# Find process on port 8501
lsof -ti:8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run main.py --server.port 8502
```

---

## 📝 Common Patterns

### Multi-Tool Agent
```python
agent = Agent(
    model=model,
    tools=[
        local_tool_1,
        local_tool_2
    ] + gateway_tools,
    hooks=[memory_hooks],
    system_prompt=system_prompt
)
```

### Namespace Design
```python
# Per-customer isolation
"app/{appId}/customer/{customerId}/preferences"
"app/{appId}/customer/{customerId}/semantic"

# Per-product organization  
"app/{appId}/product/{productId}/inquiries"
"app/{appId}/product/{productId}/reviews"

# Per-session tracking
"app/{appId}/session/{sessionId}/context"
```

### Error Handling
```python
try:
    response = agent(user_query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    return "I apologize, but I encountered an error. Please try again."
```

---

## 🎯 Best Practices

### Memory
- Set appropriate expiry (30-365 days)
- Use specific queries for better retrieval
- Monitor memory costs
- Design namespaces for multi-tenancy

### Gateway
- Group related tools in targets
- Use separate gateways for different domains
- Implement proper token refresh
- Monitor gateway metrics

### Runtime
- Pre-load models in startup handler
- Configure timeout based on complexity
- Use environment variables for config
- Implement graceful error handling

### Security
- Use least-privilege IAM roles
- Rotate credentials regularly
- Store secrets in Secrets Manager
- Enable CloudWatch logging

---

## 📚 Key Resources

### Documentation
- [AgentCore Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Memory Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [Gateway Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Runtime Docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)
- [Strands Agents](https://strandsagents.com/)

### GitHub
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [Starter Toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [Strands SDK](https://github.com/strands-agents/sdk-python)

### Support
- [AWS Support](https://console.aws.amazon.com/support)
- [re:Post Community](https://repost.aws/)
- [GitHub Issues](https://github.com/aws/bedrock-agentcore-starter-toolkit/issues)

---

## 🔐 Required IAM Permissions

### For Workshop User
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "bedrock-agentcore:*",
        "bedrock-agentcore-control:*",
        "lambda:*",
        "s3:*",
        "dynamodb:*",
        "cognito-idp:*",
        "ssm:*",
        "cloudwatch:*",
        "logs:*",
        "ecr:*",
        "codebuild:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

### Runtime Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock-agentcore:GetMemory",
        "bedrock-agentcore:RetrieveMemories",
        "bedrock-agentcore:CreateEvent",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🎓 Workshop Completion Checklist

- [ ] Lab 1: Created agent with local tools
- [ ] Lab 2: Added memory and personalization
- [ ] Lab 3: Integrated gateway and shared tools
- [ ] Lab 4: Deployed to production runtime
- [ ] Lab 5: Built customer-facing frontend
- [ ] Viewed CloudWatch observability traces
- [ ] Tested end-to-end customer journey
- [ ] Understood memory namespace design
- [ ] Explored gateway authentication flow
- [ ] Analyzed runtime session persistence
- [ ] Lab 6: Cleaned up all resources

---

**Version**: 1.0  
**Last Updated**: January 2025