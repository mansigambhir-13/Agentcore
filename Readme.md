# AgentCore - Amazon Bedrock AgentCore Workshop & Samples

A comprehensive collection of Amazon Bedrock AgentCore implementations, tutorials, and examples demonstrating how to build production-ready AI agents from prototype to customer-facing applications.

## 🎯 Overview

This repository contains:

- **Workshop Labs**: Complete end-to-end workshop with 6 labs covering agent development, memory, gateway, runtime deployment, and frontend applications
- **Sample Projects**: Production-ready use cases and integrations
- **Starter Toolkit**: Tools and utilities for AgentCore development
- **Tutorials**: Step-by-step guides for AgentCore features

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/mansigambhir-13/Agentcore.git
cd Agentcore

# Install dependencies
pip install -r requirements.txt
```

### Run the Workshop

```bash
# Run all labs sequentially
python workshop/run_workshop.py --all

# Or run individual labs
python workshop/run_workshop.py --lab 1  # Agent Prototype
python workshop/run_workshop.py --lab 2  # Memory & Personalization
python workshop/run_workshop.py --lab 4  # Production Runtime
python workshop/run_workshop.py --lab 5  # Frontend Application

# Or use the makefile
make run-all          # Run all labs
make lab1            # Run specific lab
```

## 📁 Project Structure

```
Agentcore/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── makefile                           # Convenient commands
├── workshop/                          # Workshop implementation files
│   ├── run_workshop.py               # Main workshop runner
│   ├── lab1.py - lab6.py            # Individual lab implementations
│   └── Implement_labs.py             # Lab implementation helper
├── docs/                              # Documentation
│   ├── start_here.md                 # Quick start guide
│   ├── Readme.md                     # Detailed workshop documentation
│   ├── Index.md                      # Navigation guide
│   ├── overview.md                   # Architecture overview
│   └── ...                           # Additional documentation
├── scripts/                           # Utility scripts
│   └── demo_agentcore.py             # Demo script
├── amazon-bedrock-agentcore-samples/  # AWS official samples
│   ├── 01-tutorials/                  # Step-by-step tutorials
│   ├── 02-use-cases/                  # Production use cases
│   └── 03-integrations/               # Integration examples
└── bedrock-agentcore-starter-toolkit/ # Development toolkit
```

## 🏗️ What You'll Build

### Lab 1: Agent Prototype
- Create custom tools for customer support
- Initialize Bedrock Claude model
- Build agent with Strands framework
- **Duration**: ~5 minutes

### Lab 2: Memory & Personalization
- Create AgentCore Memory resource
- Implement memory strategies
- Enable personalized responses
- **Duration**: ~10 minutes

### Lab 3: Gateway & Identity
- Create AgentCore Gateway for tool sharing
- Configure Authorization Provider with Cognito
- Enable multi-agent architectures
- **Duration**: ~10 minutes

### Lab 4: Production Runtime
- Deploy agent to serverless runtime
- Build and deploy Docker container
- Configure auto-scaling infrastructure
- **Duration**: ~15 minutes

### Lab 5: Customer-Facing Frontend
- Create Streamlit web application
- Integrate Cognito authentication
- Build real-time chat interface
- **Duration**: ~5 minutes

### Lab 6: Complete Cleanup
- Remove all AWS resources
- Clean up local files
- Reset environment
- **Duration**: ~5 minutes

## 📚 Documentation

- **[docs/start_here.md](docs/start_here.md)** - Quick start guide and package overview
- **[docs/Readme.md](docs/Readme.md)** - Complete workshop documentation with detailed lab instructions
- **[docs/Index.md](docs/Index.md)** - Navigation guide for all documentation
- **[docs/overview.md](docs/overview.md)** - Architecture and design overview
- **[amazon-bedrock-agentcore-samples/README.md](amazon-bedrock-agentcore-samples/README.md)** - AWS official samples documentation

## 🛠️ Technologies Used

- **Amazon Bedrock AgentCore** - Runtime, Memory, Gateway
- **Claude 3.7 Sonnet** - AI model
- **Strands Framework** - Agent orchestration
- **Streamlit** - Web frontend
- **Docker** - Containerization
- **AWS Services**: Cognito, IAM, ECR, CloudWatch, Systems Manager

## 📋 AWS Services Required

- Amazon Bedrock (AgentCore, Runtime, Memory, Gateway)
- Amazon Cognito
- AWS IAM
- AWS Systems Manager (Parameter Store)
- AWS Secrets Manager
- Amazon ECR
- Amazon CloudWatch

## 🔧 Configuration

The workshop uses multiple configuration sources:

1. **Lab Configuration** (`lab_config.json`) - Generated during labs
2. **SSM Parameters** - Stored in AWS Systems Manager
3. **Environment Variables** - Optional override

See [Readme.md](Readme.md) for detailed configuration instructions.

## 🧪 Testing

```bash
# Test individual labs
python workshop/lab1.py
python workshop/lab2.py

# Or use makefile
make lab1
make lab2

# Validate environment
python scripts/validate_env.py  # If available

# Test frontend (after Lab 5)
cd streamlit_app
streamlit run main.py
```

## 📊 Observability

All agent interactions are logged to CloudWatch:
- Navigate to AWS Console → CloudWatch
- Select "GenAI Observability"
- Choose "Bedrock AgentCore"
- View traces, metrics, and logs

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -r requirements.txt --upgrade
```

**AWS Credentials**
```bash
aws configure
```

**Memory Creation Timeout**
- Memory creation takes 2-3 minutes
- Check CloudWatch logs
- Verify IAM permissions

See [Readme.md](Readme.md) for comprehensive troubleshooting guide.

## 📖 Sample Use Cases

This repository includes various production use cases:

- **Customer Support Assistant** - AI-powered customer service
- **Text-to-Python IDE** - Code generation and execution
- **Video Games Sales Assistant** - Data analysis and insights
- **Healthcare Appointment Agent** - Appointment scheduling
- **Finance Personal Assistant** - Financial planning
- **Device Management Agent** - IoT device management

Explore `amazon-bedrock-agentcore-samples/02-use-cases/` for complete implementations.

## 🤝 Contributing

This repository contains educational content. If you find issues or have suggestions:
1. Document the issue clearly
2. Provide reproduction steps
3. Suggest improvements

## 📄 License

See [LICENSE](amazon-bedrock-agentcore-samples/LICENSE) files in subdirectories for licensing information.

## 🔗 Resources

### Official Documentation
- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Strands Framework](https://github.com/aws/strands)
- [Streamlit Documentation](https://docs.streamlit.io)

### Related Repositories
- [Amazon Bedrock AgentCore Samples](https://github.com/aws-samples/amazon-bedrock-agentcore-samples)
- [Bedrock AgentCore Starter Toolkit](https://github.com/aws-samples/bedrock-agentcore-starter-toolkit)

## 🎓 Learning Outcomes

After completing this workshop, you will understand:

- ✅ How to build custom AI agents with tools
- ✅ Memory strategies for personalization
- ✅ Multi-agent architectures with shared tools
- ✅ Production deployment patterns
- ✅ Authentication and authorization
- ✅ Observability and monitoring
- ✅ Building customer-facing AI applications

## 🎉 Get Started Now!

1. **Read the Quick Start**: [start_here.md](start_here.md)
2. **Run the Workshop**: `python run_workshop.py --all`
3. **Explore Samples**: Check out `amazon-bedrock-agentcore-samples/`

---

**Happy Building! 🚀**

*Amazon Bedrock AgentCore Workshop - From Prototype to Production*
