# Amazon Bedrock AgentCore Workshop - Complete Implementation Guide

## 🎯 Workshop Overview

This workshop demonstrates the complete journey from **prototype to production** for AI agents using Amazon Bedrock AgentCore. You'll build a Customer Support Agent that evolves from a simple local prototype into a production-ready system with memory, shared tools, authentication, and observability.

### What You'll Build

A **Customer Support Agent** that can:
- Answer product information questions
- Handle return policy inquiries
- Provide technical troubleshooting support
- Search the web for updated information
- Remember customer preferences across sessions
- Scale to handle multiple concurrent users

### Workshop Architecture Progression

```
Lab 1: Local Prototype (Strands Agent)
   ↓
Lab 2: + AgentCore Memory (Short & Long-term)
   ↓
Lab 3: + AgentCore Gateway (Shared Tools + Identity)
   ↓
Lab 4: + AgentCore Runtime (Production Deployment + Observability)
   ↓
Lab 5: + Frontend Application (Customer-facing Streamlit UI)
   ↓
Lab 6: Cleanup
```

---

## 📋 Prerequisites

### AWS Account Requirements
- **AWS Account** with appropriate permissions
- **Region**: us-east-1 or us-west-2 (recommended for model availability)
- **IAM Permissions** for:
  - Amazon Bedrock (including model access)
  - Amazon Bedrock AgentCore
  - AWS Lambda
  - Amazon S3
  - Amazon DynamoDB
  - Amazon Cognito
  - AWS Systems Manager (Parameter Store)
  - Amazon CloudWatch
  - Amazon ECR
  - AWS CodeBuild

### Model Access
- **Enable Claude 3.7 Sonnet** in Amazon Bedrock console
  - Navigate to: Bedrock Console → Model Access → Request Access
  - Select: `Anthropic Claude 3.7 Sonnet`
  - Wait for approval (usually instant)

### Local Development Environment
- **Python 3.10+** (3.12 recommended)
- **Docker, Finch, or Podman** (for Lab 4 - Runtime deployment)
- **AWS CLI** configured with credentials
- **Git** (for cloning repositories)

### CloudWatch Configuration
⚠️ **CRITICAL**: Enable CloudWatch Transaction Search for observability
```bash
# Enable via CLI
aws cloudwatch put-insight-rule \
  --rule-name BedrockAgentCoreObservability \
  --rule-state ENABLED \
  --rule-definition '{"Schema": "1.0", "Filter": "{ $.ServiceName = \"bedrock-agentcore\" }"}'
```

Or enable via Console: CloudWatch → Settings → Transaction Search → Enable

---

## 🚀 Quick Start

### Option 1: AWS Workshop Studio (Recommended)
If you're in an AWS-hosted workshop:
1. Access the Workshop Studio environment
2. All prerequisites are pre-configured
3. Jump directly to Lab 1

### Option 2: Self-Paced Setup

#### Step 1: Clone Workshop Repository
```bash
git clone <workshop-repo-url>
cd bedrock-agentcore-workshop
```

#### Step 2: Deploy CloudFormation Stack
```bash
# Deploy prerequisite resources
aws cloudformation create-stack \
  --stack-name agentcore-workshop-prereqs \
  --template-body file://prerequisite/cfn/workshop-prerequisites.yaml \
  --capabilities CAPABILITY_IAM \
  --parameters ParameterKey=Environment,ParameterValue=workshop

# Wait for completion (5-10 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name agentcore-workshop-prereqs
```

This creates:
- Lambda functions for gateway targets
- DynamoDB tables for customer data
- S3 bucket for knowledge base
- Cognito User Pool for authentication
- IAM roles and policies
- SSM parameters for configuration

#### Step 3: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Verify Setup
```bash
# Test AWS credentials
aws sts get-caller-identity

# Verify Bedrock model access
aws bedrock list-foundation-models \
  --by-provider anthropic \
  --query 'modelSummaries[?contains(modelId, `claude-3-7-sonnet`)]'
```

---

## 📚 Lab-by-Lab Implementation Guide

### Lab 1: Create Agent Prototype (30 minutes)

**Objective**: Build a functional customer support agent with local tools

**What You'll Learn**:
- Creating agents with Strands framework
- Implementing custom tool functions
- Tool decoration and schema definition
- Basic agent-model-tool interactions

**Implementation Steps**:

1. **Open Notebook**: `lab-01-create-an-agent.ipynb`

2. **Run Prerequisites** (if self-paced):
   ```python
   !bash scripts/prereq.sh
   ```

3. **Install Dependencies**:
   ```python
   %pip install -U -r requirements.txt -q
   ```

4. **Implement Tools**:
   - `get_product_info()` - Product specifications
   - `get_return_policy()` - Return policies
   - `web_search()` - DuckDuckGo search integration
   - `get_technical_support()` - Knowledge Base retrieval

5. **Create Agent**:
   ```python
   from strands import Agent
   from strands.models import BedrockModel
   
   model = BedrockModel(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
   agent = Agent(
       model=model,
       tools=[get_product_info, get_return_policy, web_search, get_technical_support],
       system_prompt=SYSTEM_PROMPT
   )
   ```

6. **Test Agent**:
   ```python
   response = agent("What's the return policy for my laptop?")
   response = agent("My iPhone is overheating, how do I fix it?")
   ```

**Expected Outcome**: 
- Functional agent answering support queries
- Tool calls visible in execution
- Basic conversation capability

**Limitations Identified**:
- ❌ No conversation memory beyond session
- ❌ Tools not reusable across agents
- ❌ No multi-user support
- ❌ Local execution only

---

### Lab 2: Add Memory (45 minutes)

**Objective**: Add persistent short-term and long-term memory

**What You'll Learn**:
- AgentCore Memory concepts (STM vs LTM)
- Memory strategies (USER_PREFERENCE, SEMANTIC)
- Namespace design for multi-tenancy
- Strands hooks for memory integration

**Implementation Steps**:

1. **Create Memory Resource**:
   ```python
   from bedrock_agentcore.memory import MemoryClient
   
   memory_client = MemoryClient(region_name=REGION)
   
   strategies = [
       {
           "USER_PREFERENCE": {
               "name": "CustomerPreferences",
               "namespaces": ["support/customer/{actorId}/preferences"]
           }
       },
       {
           "SEMANTIC": {
               "name": "CustomerSupportSemantic", 
               "namespaces": ["support/customer/{actorId}/semantic"]
           }
       }
   ]
   
   response = memory_client.create_memory_and_wait(
       name="CustomerSupportMemory",
       strategies=strategies,
       event_expiry_days=90
   )
   memory_id = response["id"]
   ```

2. **Seed Customer History**:
   ```python
   previous_interactions = [
       ("I'm having issues with my MacBook Pro overheating", "USER"),
       ("I can help with that thermal issue...", "ASSISTANT"),
       # More interactions...
   ]
   
   memory_client.create_event(
       memory_id=memory_id,
       actor_id="customer_001",
       session_id="previous_session",
       messages=previous_interactions
   )
   ```

3. **Implement Memory Hooks**:
   ```python
   class CustomerSupportMemoryHooks(HookProvider):
       def retrieve_customer_context(self, event: MessageAddedEvent):
           # Retrieve memories from both namespaces
           memories = self.client.retrieve_memories(
               memory_id=self.memory_id,
               namespace=f"support/customer/{self.actor_id}/preferences",
               query=user_query,
               top_k=3
           )
           # Inject context into prompt
           
       def save_support_interaction(self, event: AfterInvocationEvent):
           # Save interaction to memory
           self.client.create_event(...)
   ```

4. **Create Memory-Enhanced Agent**:
   ```python
   memory_hooks = CustomerSupportMemoryHooks(memory_id, memory_client, CUSTOMER_ID, SESSION_ID)
   
   agent = Agent(
       model=model,
       tools=[...],
       hooks=[memory_hooks],  # Add memory hooks
       system_prompt=SYSTEM_PROMPT
   )
   ```

5. **Test Personalization**:
   ```python
   # Agent remembers preferences from seeded history
   response = agent("Which headphones would you recommend?")
   # Should recommend gaming headphones based on past preferences
   
   response = agent("What is my preferred laptop brand?")
   # Should recall ThinkPad preference
   ```

**Expected Outcome**:
- ✅ Persistent memory across sessions
- ✅ Customer preference extraction
- ✅ Personalized responses
- ✅ Multi-tenant memory isolation

**Key Insights**:
- STM captures immediate context (instant)
- LTM processes patterns (20-30 seconds)
- Namespace design enables multi-tenancy
- Hooks provide seamless integration

---

### Lab 3: Add Gateway & Identity (60 minutes)

**Objective**: Centralize tools and add secure authentication

**What You'll Learn**:
- AgentCore Gateway for tool sharing
- Model Context Protocol (MCP) integration
- JWT-based authentication with Cognito
- Inbound and outbound authorization

**Implementation Steps**:

1. **Create Lambda Tool** (already deployed):
   ```python
   # Lambda function structure (reference only)
   def lambda_handler(event, context):
       tool_name = context.client_context.custom["bedrockAgentCoreToolName"]
       
       if tool_name == "check_warranty_status":
           serial_number = event["serial_number"]
           return check_warranty_status(serial_number)
       elif tool_name == "web_search":
           keywords = event["keywords"]
           return web_search(keywords)
   ```

2. **Create API Specification**:
   ```json
   [
     {
       "name": "check_warranty_status",
       "description": "Check warranty status using serial number",
       "inputSchema": {
         "type": "object",
         "properties": {
           "serial_number": {"type": "string"},
           "customer_email": {"type": "string"}
         },
         "required": ["serial_number"]
       }
     }
   ]
   ```

3. **Set Up Cognito Authentication**:
   ```python
   from lab_helpers.utils import get_or_create_cognito_pool
   
   cognito_config = get_or_create_cognito_pool(refresh_token=True)
   # Returns: client_id, discovery_url, bearer_token
   ```

4. **Create AgentCore Gateway**:
   ```python
   gateway_client = boto3.client("bedrock-agentcore-control")
   
   auth_config = {
       "customJWTAuthorizer": {
           "allowedClients": [cognito_config["client_id"]],
           "discoveryUrl": cognito_config["discovery_url"]
       }
   }
   
   gateway_response = gateway_client.create_gateway(
       name="customersupport-gw",
       roleArn=gateway_iam_role_arn,
       protocolType="MCP",
       authorizerType="CUSTOM_JWT",
       authorizerConfiguration=auth_config
   )
   
   gateway_id = gateway_response["gatewayId"]
   gateway_url = gateway_response["gatewayUrl"]
   ```

5. **Add Lambda Target to Gateway**:
   ```python
   lambda_target_config = {
       "mcp": {
           "lambda": {
               "lambdaArn": lambda_function_arn,
               "toolSchema": {"inlinePayload": api_spec}
           }
       }
   }
   
   gateway_client.create_gateway_target(
       gatewayIdentifier=gateway_id,
       name="LambdaTarget",
       targetConfiguration=lambda_target_config,
       credentialProviderConfigurations=[{
           "credentialProviderType": "GATEWAY_IAM_ROLE"
       }]
   )
   ```

6. **Create MCP Client**:
   ```python
   from strands.tools.mcp import MCPClient
   from mcp.client.streamable_http import streamablehttp_client
   
   mcp_client = MCPClient(
       lambda: streamablehttp_client(
           gateway_url,
           headers={"Authorization": f"Bearer {cognito_config['bearer_token']}"}
       )
   )
   ```

7. **Create Agent with Gateway Tools**:
   ```python
   with mcp_client:
       tools = [
           get_product_info,  # Local tool
           get_return_policy,  # Local tool
           get_technical_support  # Local tool
       ] + mcp_client.list_tools_sync()  # Gateway tools
       
       agent = Agent(
           model=model,
           tools=tools,
           hooks=[memory_hooks],
           system_prompt=SYSTEM_PROMPT
       )
   ```

8. **Test Gateway Integration**:
   ```python
   response = agent("List all of your tools")
   # Should show both local and gateway tools
   
   response = agent("Check warranty for serial MNO33333333")
   # Uses gateway Lambda tool
   
   response = agent("Search web for iPhone overheating solutions")
   # Uses gateway web search tool
   ```

**Expected Outcome**:
- ✅ Centralized tool infrastructure
- ✅ Secure JWT authentication
- ✅ Reusable tools across agents
- ✅ Local + Gateway tool integration

**Architecture Benefits**:
- Tools can serve multiple agents
- Consistent tool behavior
- Centralized security and access control
- Easy tool updates and versioning

---

### Lab 4: Deploy to Production (90 minutes)

**Objective**: Deploy agent to AgentCore Runtime with observability

**What You'll Learn**:
- AgentCore Runtime deployment
- Container packaging with starter toolkit
- Production authentication flow
- CloudWatch GenAI Observability

**Implementation Steps**:

1. **Create Runtime-Ready Agent**:
   ```python
   # Create lab_helpers/lab4_runtime.py
   from bedrock_agentcore.runtime import BedrockAgentCoreApp
   
   app = BedrockAgentCoreApp()  # LINE 1: Import runtime
   
   @app.entrypoint  # LINE 2: Decorate entrypoint
   async def invoke(payload, context=None):
       user_input = payload.get("prompt", "")
       auth_header = context.request_headers.get('Authorization', '')
       
       # Get gateway URL
       gateway_url = get_gateway_url()
       
       # Create MCP client with auth
       mcp_client = MCPClient(lambda: streamablehttp_client(
           url=gateway_url,
           headers={"Authorization": auth_header}
       ))
       
       with mcp_client:
           tools = [local_tools] + mcp_client.list_tools_sync()
           agent = Agent(model=model, tools=tools, hooks=[memory_hooks])
           response = agent(user_input)
           return response.message["content"][0]["text"]
   
   if __name__ == "__main__":
       app.run()  # LINE 3: Run app
   ```

2. **Configure Runtime Deployment**:
   ```python
   from bedrock_agentcore_starter_toolkit import Runtime
   
   execution_role_arn = create_agentcore_runtime_execution_role()
   
   agentcore_runtime = Runtime()
   
   agentcore_runtime.configure(
       entrypoint="lab_helpers/lab4_runtime.py",
       execution_role=execution_role_arn,
       auto_create_ecr=True,
       requirements_file="requirements.txt",
       region=region,
       agent_name="customer_support_agent",
       authorizer_configuration={
           "customJWTAuthorizer": {
               "allowedClients": [cognito_client_id],
               "discoveryUrl": cognito_discovery_url
           }
       }
   )
   ```

3. **Launch Runtime** (builds container, ~5-10 minutes):
   ```python
   launch_result = agentcore_runtime.launch()
   agent_arn = launch_result.agent_arn
   
   # Wait for deployment
   while status not in ["READY", "CREATE_FAILED"]:
       status = agentcore_runtime.status().endpoint["status"]
       time.sleep(10)
   ```

4. **Configure Request Headers**:
   ```python
   client = boto3.client("bedrock-agentcore-control")
   runtime_id = agent_arn.split("/")[-1]
   
   client.update_agent_runtime(
       agentRuntimeId=runtime_id,
       requestHeaderConfiguration={
           "requestHeaderAllowlist": [
               "Authorization",  # For OAuth token propagation
               "X-Custom-Header"
           ]
       }
   )
   ```

5. **Test Runtime Invocation**:
   ```python
   import uuid
   
   session_id = str(uuid.uuid4())
   
   response = agentcore_runtime.invoke(
       {"prompt": "List all of your tools"},
       bearer_token=cognito_config["bearer_token"],
       session_id=session_id
   )
   
   print(response["response"])
   ```

6. **Test Session Continuity**:
   ```python
   # First interaction
   agentcore_runtime.invoke(
       {"prompt": "I have a Gaming Console Pro, check warranty MNO33333333"},
       bearer_token=token,
       session_id=session_id
   )
   
   # Follow-up (same session)
   agentcore_runtime.invoke(
       {"prompt": "What was the warranty status?"},
       bearer_token=token,
       session_id=session_id  # Same session remembers context
   )
   ```

7. **Access CloudWatch Observability**:
   - Navigate to: CloudWatch → GenAI Observability → Bedrock AgentCore
   - View:
     - **Agents**: All deployed runtimes
     - **Sessions**: User conversation sessions
     - **Traces**: Detailed execution traces with timing
     - **Metrics**: Performance and error rates

**Expected Outcome**:
- ✅ Serverless production deployment
- ✅ Auto-scaling capability
- ✅ Session persistence
- ✅ Full request tracing
- ✅ Performance metrics
- ✅ Multi-user support

**Production Features**:
- Automatic scaling based on load
- Built-in health checks
- Request/response logging
- Error tracking and alerting
- JWT token validation

---

### Lab 5: Build Frontend (45 minutes)

**Objective**: Create customer-facing Streamlit application

**What You'll Learn**:
- Streamlit integration with AgentCore Runtime
- Real-time response streaming
- Session management in UI
- Authentication flow in frontend

**Implementation Steps**:

1. **Install Frontend Dependencies**:
   ```python
   %pip install -r lab_helpers/lab5_frontend/requirements.txt -q
   ```

2. **Frontend Architecture**:
   ```
   lab_helpers/lab5_frontend/
   ├── main.py              # Streamlit app + auth
   ├── chat.py              # Chat management
   ├── chat_utils.py        # Message formatting
   └── sagemaker_helper.py  # URL generation
   ```

3. **Key Components**:

   **main.py** - Authentication & UI:
   ```python
   import streamlit as st
   from chat import CustomerSupportChat
   
   # Authentication
   if not st.session_state.get("authenticated"):
       username = st.text_input("Username")
       password = st.text_input("Password", type="password")
       if st.button("Login"):
           token = authenticate_user(username, password)
           st.session_state.authenticated = True
           st.session_state.token = token
   
   # Chat interface
   chat = CustomerSupportChat(
       runtime_endpoint=runtime_url,
       auth_token=st.session_state.token
   )
   
   if prompt := st.chat_input("Ask a question..."):
       chat.send_message(prompt)
   ```

   **chat.py** - Runtime Integration:
   ```python
   class CustomerSupportChat:
       def send_message(self, prompt: str):
           response = requests.post(
               f"{self.runtime_endpoint}/invocations",
               headers={"Authorization": f"Bearer {self.auth_token}"},
               json={"prompt": prompt, "session_id": self.session_id}
           )
           return response.json()
   ```

4. **Launch Streamlit Application**:
   ```python
   from lab_helpers.lab5_frontend.sagemaker_helper import get_streamlit_url
   
   streamlit_url = get_streamlit_url()
   print(f"Access application at: {streamlit_url}")
   
   !cd lab_helpers/lab5_frontend/ && streamlit run main.py
   ```

5. **Test End-to-End Flow**:
   - Access Streamlit URL
   - Login with Cognito credentials
   - Ask: "What are the specifications for your laptops?"
   - Ask: "What's the return policy for electronics?"
   - Ask: "My iPhone is overheating, what should I do?"
   - Refresh page - conversation history persists

**Expected Outcome**:
- ✅ Professional web interface
- ✅ Secure user authentication
- ✅ Real-time responses
- ✅ Session persistence
- ✅ Response timing metrics
- ✅ Complete customer experience

---

### Lab 6: Cleanup (15 minutes)

**Objective**: Remove all workshop resources

**What You'll Clean Up**:
- AgentCore Memory resources
- AgentCore Runtime deployments
- AgentCore Gateway and targets
- ECR repositories
- IAM roles
- CloudWatch logs
- Cognito resources
- SSM parameters
- Local files

**Implementation Steps**:

1. **Run Cleanup Notebook**: `lab-06-cleanup.ipynb`

2. **Automated Cleanup Functions**:
   ```python
   # Clean Memory
   agentcore_memory_cleanup()
   
   # Clean Runtime
   runtime_resource_cleanup()
   
   # Clean Gateway
   gateway_target_cleanup()
   
   # Clean Security
   delete_agentcore_runtime_execution_role()
   cleanup_cognito_resources()
   delete_customer_support_secret()
   
   # Clean Observability
   delete_observability_resources()
   
   # Clean Local Files
   local_file_cleanup()
   ```

3. **Verify Cleanup**:
   ```bash
   # Check for remaining resources
   aws bedrock-agentcore-control list-agent-runtimes
   aws bedrock-agentcore-control list-gateways
   aws bedrock-agentcore list-memories
   ```

---

## 🎓 Key Concepts & Best Practices

### Memory Design Patterns

**Multi-Tenant Namespace Strategy**:
```
support/customer/{actorId}/preferences  # User preferences
support/customer/{actorId}/semantic     # Factual information
sales/{actorId}/interactions           # Sales history
inventory/{productId}/queries          # Product inquiries
```

**Memory Strategies**:
- `USER_PREFERENCE`: Behavioral patterns, preferences (structured)
- `SEMANTIC`: Factual information, searchable (vector embeddings)

**Best Practices**:
- Use separate namespaces per customer/context
- Set appropriate expiry (30-365 days)
- Query with relevant context for better retrieval
- Monitor memory costs and optimize retention

### Gateway Patterns

**Tool Organization**:
```
Gateway A: Customer Data Tools
  - check_warranty
  - get_customer_profile
  - update_preferences

Gateway B: Product Tools  
  - search_catalog
  - check_inventory
  - get_specifications

Gateway C: External Integrations
  - web_search
  - knowledge_base_query
  - third_party_api
```

**Authentication Strategies**:
- **Inbound**: JWT from IdP (Cognito, Okta, Entra)
- **Outbound**: IAM, API Key, OAuth for downstream services
- **Token Propagation**: Pass user context to tools

### Runtime Deployment

**Container Requirements**:
- Entrypoint function with `@app.entrypoint`
- Port 8080 exposure
- `/invocations` endpoint
- `/ping` health check

**Scaling Considerations**:
- Runtime auto-scales based on load
- Cold start: ~2-3 seconds
- Warm requests: <100ms overhead
- Configure timeouts based on agent complexity

**Header Configuration**:
```python
requestHeaderAllowlist = [
    "Authorization",      # Required for OAuth
    "X-User-Id",         # Custom user tracking
    "X-Session-Id",      # Session management
    "X-Request-Id"       # Request tracing
]
```

### Observability

**Trace Analysis**:
- View full conversation flow
- Identify tool usage patterns
- Debug errors with stack traces
- Analyze response times

**Key Metrics**:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Tool invocation frequency
- Token consumption

**Monitoring Setup**:
```python
# Custom metrics in agent code
import time

start_time = time.time()
response = agent(prompt)
duration = time.time() - start_time

# Log to CloudWatch
cloudwatch.put_metric_data(
    Namespace='AgentCore/CustomerSupport',
    MetricData=[{
        'MetricName': 'ResponseTime',
        'Value': duration,
        'Unit': 'Seconds'
    }]
)
```

---

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Memory Processing Delays
**Symptom**: Long-term memories not appearing after `create_event`

**Solution**:
```python
import time
retries = 0
while retries < 6:
    memories = memory_client.retrieve_memories(...)
    if memories:
        break
    time.sleep(10)
    retries += 1
```
**Explanation**: LTM processing takes 20-30 seconds asynchronously

#### 2. Gateway Authentication Errors
**Symptom**: `401 Unauthorized` when calling gateway

**Solution**:
```python
# Verify token is not expired
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
exp_time = decoded['exp']
if time.time() > exp_time:
    token = get_or_create_cognito_pool(refresh_token=True)['bearer_token']
```
**Explanation**: Cognito tokens expire after 2 hours

#### 3. Runtime Deployment Failures
**Symptom**: `CREATE_FAILED` status

**Check**:
```bash
# View CodeBuild logs
aws codebuild list-builds-for-project \
  --project-name agentcore-runtime-build

# Check execution role permissions
aws iam simulate-principal-policy \
  --policy-source-arn <execution-role-arn> \
  --action-names bedrock:InvokeModel
```

#### 4. Docker Build Issues
**Symptom**: Container build fails

**Solution**:
```bash
# Verify Docker is running
docker ps

# Clean Docker cache
docker system prune -a

# Use Finch as alternative
brew install finch
finch vm start
```

#### 5. Knowledge Base Sync Stuck
**Symptom**: Ingestion job stuck in progress

**Solution**:
```python
# Cancel stuck job
bedrock.stop_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id,
    ingestionJobId=job_id
)

# Restart sync
bedrock.start_ingestion_job(...)
```

#### 6. Streamlit Won't Start
**Symptom**: Port already in use

**Solution**:
```bash
# Find process on port 8501
lsof -ti:8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run main.py --server.port 8502
```

---

## 📊 Demo Script for Showcasing

### 5-Minute Executive Demo

```python
# ====================
# 1. PROTOTYPE (Lab 1)
# ====================
print("🎯 Demo 1: Simple Agent Prototype")
agent = Agent(model=model, tools=[get_product_info, get_return_policy])
response = agent("What's the return policy for laptops?")
# Show: Basic tool usage, single session

# ====================
# 2. MEMORY (Lab 2)
# ====================
print("\n💭 Demo 2: Persistent Memory")
agent_with_memory = Agent(model=model, tools=tools, hooks=[memory_hooks])
response = agent_with_memory("Which headphones would you recommend?")
# Show: Personalized response based on past preferences

# ====================
# 3. GATEWAY (Lab 3)
# ====================
print("\n🌐 Demo 3: Shared Tools via Gateway")
with mcp_client:
    gateway_tools = mcp_client.list_tools_sync()
    print(f"Available gateway tools: {[t.name for t in gateway_tools]}")
    response = agent("Check warranty for serial MNO33333333")
# Show: Centralized tool infrastructure

# ====================
# 4. RUNTIME (Lab 4)
# ====================
print("\n🚀 Demo 4: Production Deployment")
session_id = str(uuid.uuid4())
response = agentcore_runtime.invoke(
    {"prompt": "My laptop won't turn on, help!"},
    bearer_token=token,
    session_id=session_id
)
# Show: CloudWatch traces, session persistence

# ====================
# 5. FRONTEND (Lab 5)
# ====================
print("\n🖥️  Demo 5: Customer-Facing Application")
print(f"Access UI: {streamlit_url}")
# Show: Live Streamlit interface, real-time responses
```

### 15-Minute Technical Deep Dive

**Part 1: Architecture Evolution** (3 min)
- Show progression from local → memory → gateway → runtime → frontend
- Explain each component's role
- Highlight AWS services used

**Part 2: Memory Intelligence** (4 min)
- Demonstrate preference extraction
- Show semantic search results
- Explain STM vs LTM processing
- Show namespace isolation

**Part 3: Gateway & Identity** (4 min)
- Show Lambda tool implementation
- Demonstrate JWT authentication flow
- Explain tool sharing benefits
- Show inbound/outbound auth

**Part 4: Production Operations** (4 min)
- CloudWatch observability dashboard
- Trace analysis walkthrough
- Session management
- Performance metrics

---

## 🔐 Security Best Practices

### IAM Policies

**Least Privilege Runtime Role**:
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
        "bedrock-agentcore:CreateEvent"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock-agentcore:*:*:memory/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/bedrock-agentcore/*"
    }
  ]
}
```

### Token Management

```python
class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = 0
    
    def get_token(self):
        if time.time() >= self.expires_at - 300:  # Refresh 5 min early
            self.token = refresh_cognito_token()
            self.expires_at = decode_jwt(self.token)['exp']
        return self.token
```

### Secrets Management

```python
# Store secrets in AWS Secrets Manager, not code
import boto3

secrets_client = boto3.client('secretsmanager')

def get_api_key(secret_name):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])['api_key']
```

---

## 📈 Performance Optimization

### Memory Optimization

```python
# Optimize retrieval with targeted queries
memories = memory_client.retrieve_memories(
    memory_id=memory_id,
    namespace=f"support/customer/{actor_id}/preferences",
    query=user_query,  # Specific query
    top_k=3,  # Limit results
    score_threshold=0.7  # Quality filter
)
```

### Runtime Optimization

```python
# Pre-load models and resources
@app.startup
def preload():
    global model, memory_client, mcp_client
    model = BedrockModel(...)
    memory_client = MemoryClient(...)
    # Reduces cold start time

@app.entrypoint
async def invoke(payload, context):
    # Use pre-loaded resources
    return agent(payload["prompt"])
```

### Tool Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_product_info(product_type: str):
    # Cache frequently accessed product data
    return fetch_from_database(product_type)
```

---

## 📚 Additional Resources

### Documentation
- [AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)
- [Strands Agents](https://strandsagents.com/)

### Sample Code
- [AgentCore Samples Repository](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [Starter Toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit)

### Blog Posts
- [AgentCore Memory Deep Dive](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/)
- [Production Agent Deployment](https://aws.amazon.com/blogs/machine-learning/deploy-ai-agents-to-production/)

---

## 🎉 Congratulations!

You've completed the full Amazon Bedrock AgentCore workshop! You now know how to:

✅ Build agents with custom tools  
✅ Add persistent memory for personalization  
✅ Share tools securely via Gateway  
✅ Deploy to production with Runtime  
✅ Create customer-facing applications  
✅ Monitor and debug with observability  

### Next Steps

1. **Extend the Agent**: Add more tools for your use case
2. **Multi-Agent Systems**: Coordinate multiple specialized agents
3. **Advanced Memory**: Implement custom extraction strategies
4. **Production Hardening**: Add rate limiting, monitoring, alerting
5. **Enterprise Integration**: Connect to your existing systems

### Questions?

- AWS Support: [Create Support Case](https://console.aws.amazon.com/support)
- Community: [AWS re:Post](https://repost.aws/)
- GitHub: [Report Issues](https://github.com/aws/bedrock-agentcore-starter-toolkit/issues)

---

**Workshop Version**: 1.0  
**Last Updated**: January 2025  
**Region Support**: us-east-1, us-west-2, eu-west-1, ap-southeast-1