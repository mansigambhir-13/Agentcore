# Amazon Bedrock AgentCore End-to-End Workshop

A comprehensive workshop demonstrating how to build a production-ready AI agent from prototype to customer-facing application using Amazon Bedrock AgentCore.

## 🎯 Workshop Overview

This workshop guides you through building a complete customer support agent system, showcasing all AgentCore capabilities:

- **Lab 1**: Create Agent Prototype with custom tools
- **Lab 2**: Add Memory & Personalization
- **Lab 3**: Scale with Gateway & Identity (separate module)
- **Lab 4**: Deploy to Production Runtime
- **Lab 5**: Build Customer-Facing Frontend
- **Lab 6**: Complete Cleanup

## 🏗️ What You'll Build

By the end of this workshop, you'll have:

- ✅ AI-powered customer support agent with custom tools
- ✅ Persistent memory with short-term and long-term strategies
- ✅ Shared tool gateway for multi-agent scenarios
- ✅ Production-ready serverless runtime deployment
- ✅ Secure authentication with Amazon Cognito
- ✅ Customer-facing Streamlit web application
- ✅ CloudWatch observability and tracing

## 📋 Prerequisites

### Required
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.10 or higher
- pip package manager

### AWS Services Used
- Amazon Bedrock (AgentCore, Runtime, Memory, Gateway)
- Amazon Cognito
- AWS IAM
- AWS Systems Manager (Parameter Store)
- AWS Secrets Manager
- Amazon ECR
- Amazon CloudWatch
- Amazon SageMaker (optional, for notebook environment)

## 🚀 Quick Start

### Option 1: Run All Labs Sequentially

```bash
# Clone or download the workshop files
cd agentcore-workshop

# Install dependencies
pip install -r requirements.txt

# Run the complete workshop
python run_workshop.py --all
```

### Option 2: Run Individual Labs

```bash
# Run a specific lab
python run_workshop.py --lab 1  # Agent Prototype
python run_workshop.py --lab 2  # Memory & Personalization
python run_workshop.py --lab 4  # Production Runtime
python run_workshop.py --lab 5  # Frontend Application
python run_workshop.py --lab 6  # Cleanup

# Or run lab files directly
python lab1_implementation.py
python lab2_implementation.py
# etc.
```

### Option 3: Non-Interactive Mode

```bash
# Run without prompts (useful for automation)
python run_workshop.py --all --non-interactive
```

## 📚 Lab Details

### Lab 1: Create Agent Prototype

**Duration**: ~5 minutes

**What You'll Do**:
- Create custom tools for customer support
- Initialize Bedrock Claude model
- Build agent with Strands framework
- Test agent functionality

**Tools Created**:
- `get_product_info()` - Product specifications
- `get_return_policy()` - Return policy information
- `web_search()` - Web search capability
- `get_technical_support()` - Troubleshooting guidance

**Files Created**:
- `lab_config.json` - Configuration storage

```bash
python lab1_implementation.py
```

### Lab 2: Add Memory & Personalization

**Duration**: ~10 minutes

**What You'll Do**:
- Create AgentCore Memory resource
- Seed customer interaction history
- Implement memory hooks
- Test personalized responses

**Memory Strategies**:
- **User Preference**: Customer preferences and behavior patterns
- **Semantic**: Factual information from conversations

**Files Created**:
- Updated `lab_config.json` with memory ID

```bash
python lab2_implementation.py
```

### Lab 3: Scale with Gateway & Identity

**Duration**: ~10 minutes

**Note**: This lab is implemented separately. Run `lab3_implementation.py` for Gateway setup.

**What You'll Do**:
- Create AgentCore Gateway for tool sharing
- Configure Authorization Provider with Cognito
- Register tools as gateway targets
- Test secure tool access

### Lab 4: Deploy to Production Runtime

**Duration**: ~15 minutes

**What You'll Do**:
- Create runtime-ready agent code
- Configure execution role
- Build and deploy Docker container
- Deploy to AgentCore Runtime
- Test production invocation

**Files Created**:
- `runtime_agent/` directory
- `runtime_agent/agent.py` - Runtime entrypoint
- `runtime_agent/requirements.txt` - Dependencies
- `.bedrock_agentcore.yaml` - Runtime configuration
- `Dockerfile` - Container definition

```bash
python lab4_implementation.py
```

### Lab 5: Build Customer-Facing Frontend

**Duration**: ~5 minutes

**What You'll Do**:
- Create Streamlit web application
- Integrate Cognito authentication
- Connect to AgentCore Runtime
- Implement real-time chat interface
- Test complete customer journey

**Files Created**:
- `streamlit_app/` directory
- `streamlit_app/main.py` - Main application
- `streamlit_app/chat.py` - Chat management
- `streamlit_app/chat_utils.py` - Utilities
- `streamlit_app/requirements.txt` - Dependencies
- `streamlit_app/config.json` - Configuration

**Launch the Frontend**:
```bash
python lab5_implementation.py

# Then in a separate terminal:
cd streamlit_app
streamlit run main.py
```

**Test Credentials**:
- Username: `testuser`
- Password: `TestPass123!`

### Lab 6: Complete Cleanup

**Duration**: ~5 minutes

**What You'll Do**:
- Clean up Memory resources
- Clean up Runtime and ECR
- Clean up Gateway resources
- Clean up Security resources (IAM, Cognito, Secrets)
- Clean up CloudWatch logs
- Clean up local files

**⚠️ Warning**: This action is irreversible!

```bash
python lab6_implementation.py

# Or non-interactive:
python lab6_implementation.py --no-confirm
```

## 📁 Project Structure

```
agentcore-workshop/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── run_workshop.py              # Main workshop runner
├── lab1_implementation.py       # Lab 1: Agent Prototype
├── lab2_implementation.py       # Lab 2: Memory & Personalization
├── lab4_implementation.py       # Lab 4: Production Runtime
├── lab5_implementation.py       # Lab 5: Frontend Application
├── lab6_implementation.py       # Lab 6: Cleanup
├── lab_config.json              # Generated: Configuration storage
├── runtime_agent/               # Generated: Runtime code
│   ├── agent.py
│   └── requirements.txt
└── streamlit_app/               # Generated: Frontend application
    ├── main.py
    ├── chat.py
    ├── chat_utils.py
    ├── requirements.txt
    └── config.json
```

## 🔧 Configuration

The workshop uses multiple configuration sources:

### 1. Lab Configuration (`lab_config.json`)
```json
{
  "memory_id": "mem-xxxxx",
  "gateway_id": "gw-xxxxx",
  "runtime_arn": "arn:aws:bedrock-agentcore:..."
}
```

### 2. SSM Parameters
- `/app/customersupport/agentcore/runtime_arn`
- `/app/customersupport/agentcore/gateway_url`
- `/app/customersupport/agentcore/client_id`
- `/app/customersupport/agentcore/pool_id`
- `/app/customersupport/agentcore/cognito_discovery_url`

### 3. Environment Variables (Optional)
```bash
export AWS_REGION=us-east-1
export RUNTIME_ARN=arn:aws:...
export CLIENT_ID=your-client-id
export POOL_ID=your-pool-id
```

## 🛠️ Dependencies

### Core Dependencies
```
boto3>=1.34.0
strands>=0.1.0
bedrock-agentcore-sdk>=0.1.0
bedrock-agentcore-starter-toolkit>=0.1.0
rich>=13.0.0
```

### Frontend Dependencies
```
streamlit>=1.28.0
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 🧪 Testing

### Test Agent Functionality
```python
from lab1_implementation import Lab1Implementation

lab1 = Lab1Implementation()
lab1.create_tools()
lab1.create_model()
lab1.create_agent()

# Test query
response = lab1.agent("What's the return policy for laptops?")
print(response.message["content"][0]["text"])
```

### Test Memory Integration
```python
from lab2_implementation import Lab2Implementation

lab2 = Lab2Implementation()
# Follow lab2 setup...

# Test personalized query
response = lab2.agent("Which headphones would you recommend?")
# Should reference past gaming headphone preferences
```

### Test Frontend
```bash
cd streamlit_app
streamlit run main.py

# Open browser to http://localhost:8501
# Login with test credentials
# Try example queries
```

## 📊 Observability

### CloudWatch Logs
All agent interactions are logged to CloudWatch:
- Navigate to AWS Console → CloudWatch
- Select "GenAI Observability"
- Choose "Bedrock AgentCore"
- View traces, metrics, and logs

### Monitoring Metrics
- Invocation count
- Response time
- Error rates
- Tool usage patterns
- Token consumption

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt --upgrade
```

#### 2. AWS Credentials
```bash
# Configure AWS CLI
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

#### 3. Memory Creation Timeout
Memory creation takes 2-3 minutes. If it times out:
- Check CloudWatch logs
- Verify IAM permissions
- Ensure region supports AgentCore Memory

#### 4. Runtime Deployment Issues
- Ensure Docker is installed and running
- Verify ECR permissions
- Check execution role has required policies

#### 5. Frontend Not Loading
- Verify runtime is deployed and ready
- Check Cognito configuration
- Ensure port 8501 is available

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python run_workshop.py --lab 1
```

## 💡 Best Practices

### 1. Resource Management
- Always run Lab 6 cleanup when done
- Monitor CloudWatch for unexpected usage
- Use SSM Parameter Store for configuration

### 2. Security
- Rotate Cognito credentials regularly
- Use least-privilege IAM policies
- Enable MFA for production deployments

### 3. Cost Optimization
- Clean up unused resources promptly
- Monitor Bedrock usage
- Use appropriate memory expiry settings

### 4. Development Workflow
- Test agents locally before runtime deployment
- Use memory namespaces to isolate environments
- Version control your agent code

## 🔗 Resources

### Documentation
- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Strands Framework](https://github.com/aws/strands)
- [Streamlit Documentation](https://docs.streamlit.io)

### Sample Queries
Try these with your customer support agent:

**Product Information**:
- "What are the specifications for your laptops?"
- "Tell me about your smartphone features"
- "What headphones do you have available?"

**Return Policy**:
- "What's your return policy for electronics?"
- "How do I return a laptop?"
- "Can I return opened products?"

**Technical Support**:
- "My phone is overheating, what should I do?"
- "My laptop won't turn on"
- "I'm having WiFi connectivity issues"

**Personalization** (after Lab 2):
- "Which headphones would you recommend?" (references past gaming preference)
- "What's my preferred laptop brand?" (references ThinkPad preference)

## 🤝 Contributing

This workshop is designed to be educational. If you find issues or have suggestions:
1. Document the issue clearly
2. Provide reproduction steps
3. Suggest improvements

## 📄 License

This workshop code is provided as-is for educational purposes.

## 🎓 Learning Outcomes

After completing this workshop, you will understand:

- ✅ How to build custom AI agents with tools
- ✅ Memory strategies for personalization
- ✅ Multi-agent architectures with shared tools
- ✅ Production deployment patterns
- ✅ Authentication and authorization
- ✅ Observability and monitoring
- ✅ Building customer-facing AI applications

## 🎉 Next Steps

After completing the workshop:

1. **Customize the Agent**: Add your own tools and logic
2. **Enhance the Frontend**: Improve UI/UX, add features
3. **Scale the Solution**: Deploy multiple agents
4. **Add More Tools**: Integrate with your systems
5. **Implement Analytics**: Track usage and insights

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review CloudWatch logs
- Consult AWS Bedrock documentation
- Open an issue in the repository

---

**Happy Building! 🚀**

*Amazon Bedrock AgentCore Workshop - From Prototype to Production*