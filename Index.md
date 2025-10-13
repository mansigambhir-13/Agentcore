# AgentCore Workshop - Complete Package Index

## 📦 Package Contents

This package contains a complete, ready-to-run demonstration of Amazon Bedrock AgentCore capabilities from prototype to production.

---

## 🚀 Getting Started Files

### 1. **QUICKSTART.md** ⭐ START HERE
   - Quick 5-minute setup guide
   - Essential commands
   - Fast path to running the workshop

### 2. **validate_env.py**
   - Environment validation script
   - Checks prerequisites
   - Run before workshop: `python validate_env.py`

### 3. **Makefile**
   - Convenient command shortcuts
   - Type `make help` for all commands
   - Quick commands: `make install`, `make run-all`

---

## 📚 Documentation Files

### Core Documentation
- **README.md** - Complete workshop documentation (comprehensive)
- **SUMMARY.md** - Implementation summary and architecture
- **QUICKSTART.md** - Fast start guide (5 minutes)

### Reference
- **requirements.txt** - All Python dependencies
- **INDEX.md** - This file (navigation guide)

---

## 🔬 Lab Implementation Files

### Main Runner
- **run_workshop.py** - Runs all labs sequentially
  - Usage: `python run_workshop.py --all`
  - Options: `--lab N`, `--non-interactive`

### Individual Labs

#### **lab1_implementation.py** - Lab 1: Agent Prototype
   - Creates customer support agent
   - 4 custom tools (product info, returns, search, support)
   - Duration: ~5 minutes
   - Run: `python lab1_implementation.py`

#### **lab2_implementation.py** - Lab 2: Memory & Personalization
   - AgentCore Memory integration
   - 2 memory strategies (preferences, semantic)
   - Seeds customer history
   - Duration: ~10 minutes
   - Run: `python lab2_implementation.py`

#### **lab4_implementation.py** - Lab 4: Production Runtime
   - Runtime-ready agent code
   - Docker container deployment
   - Serverless infrastructure
   - Duration: ~15 minutes
   - Run: `python lab4_implementation.py`

#### **lab5_implementation.py** - Lab 5: Customer Frontend
   - Streamlit web application
   - Cognito authentication
   - Real-time chat interface
   - Duration: ~5 minutes
   - Run: `python lab5_implementation.py`

#### **lab6_implementation.py** - Lab 6: Complete Cleanup
   - Removes all AWS resources
   - Cleans local files
   - Irreversible operation
   - Duration: ~5 minutes
   - Run: `python lab6_implementation.py`

---

## 📂 Generated Files (During Workshop)

These files are created automatically when you run the labs:

### Configuration
- **lab_config.json** - Stores IDs and ARNs from labs
  - Memory ID, Runtime ARN, Gateway URL
  - Used by subsequent labs

### Lab 4 Outputs
- **runtime_agent/** - Runtime agent code directory
  - `agent.py` - Runtime entrypoint
  - `requirements.txt` - Runtime dependencies
- **.bedrock_agentcore.yaml** - Runtime configuration
- **Dockerfile** - Container definition

### Lab 5 Outputs
- **streamlit_app/** - Frontend application directory
  - `main.py` - Main Streamlit app
  - `chat.py` - Chat management
  - `chat_utils.py` - Utility functions
  - `config.json` - Frontend configuration
  - `requirements.txt` - Frontend dependencies

---

## 🎯 Quick Reference

### Complete Workshop
```bash
# Fastest path
make quick-start

# Or step by step
make install      # Install dependencies
make validate     # Check environment
make run-all      # Run all labs
```

### Individual Labs
```bash
make lab1    # Agent Prototype
make lab2    # Memory & Personalization  
make lab4    # Production Runtime
make lab5    # Customer Frontend
make lab6    # Cleanup
```

### Frontend
```bash
make frontend    # Launch Streamlit app
# Opens http://localhost:8501
```

### Cleanup
```bash
make cleanup     # Remove all AWS resources
make clean       # Remove local files only
```

---

## 📖 Documentation Map

### First Time Users
1. Read: **QUICKSTART.md**
2. Run: `python validate_env.py`
3. Execute: `python run_workshop.py --all`
4. Review: **SUMMARY.md**

### Developers
1. Read: **README.md** (full details)
2. Study: Lab implementation files
3. Customize: Modify tools and prompts
4. Deploy: Use Lab 4 patterns

### Presenters/Demos
1. Review: **SUMMARY.md**
2. Prepare: Run `make validate`
3. Demo: Use `make run-all`
4. Show: Launch frontend with `make frontend`

---

## 🏗️ Architecture Overview

```
Lab 1: Agent Prototype
  └─> Claude Model + Custom Tools

Lab 2: + Memory
  └─> Agent + AgentCore Memory (2 strategies)

Lab 3: + Gateway (separate)
  └─> Multi-agent + Shared Tools

Lab 4: + Production Runtime  
  └─> Serverless Deployment + Observability

Lab 5: + Customer Frontend
  └─> Web App + Authentication + Chat

Lab 6: Cleanup
  └─> Remove All Resources
```

---

## 🎓 Learning Path

### Beginner Path (30 min)
1. Install: `make install`
2. Validate: `make validate`
3. Run All: `make run-all`
4. Test: Launch frontend
5. Cleanup: `make cleanup`

### Intermediate Path (45 min)
1. Run labs individually: `make lab1`, `make lab2`, etc.
2. Examine generated code
3. Modify tools in lab1_implementation.py
4. Test changes
5. Review CloudWatch logs

### Advanced Path (1-2 hours)
1. Fork and customize all implementations
2. Add new tools and memory strategies
3. Integrate with your systems
4. Deploy to your AWS account
5. Implement CI/CD pipeline

---

## 🔧 Utilities

### Environment
- `validate_env.py` - Pre-flight checks
- `make aws-check` - Verify AWS credentials
- `make aws-region` - Show current region

### Development
- `make lint` - Code linting
- `make format` - Code formatting
- `make test` - Run validation

### Monitoring
- `make aws-logs` - Tail CloudWatch logs
- `make status` - Show workshop status
- `make info` - Display workshop info

---

## 📊 What Gets Created

### AWS Resources
- ✅ AgentCore Memory (Lab 2)
- ✅ AgentCore Gateway (Lab 3)
- ✅ AgentCore Runtime (Lab 4)
- ✅ ECR Repository (Lab 4)
- ✅ Cognito User Pool (Lab 3/4)
- ✅ IAM Roles (Lab 4)
- ✅ SSM Parameters (Labs 3-5)
- ✅ CloudWatch Logs (All labs)

### Local Files
- ✅ lab_config.json
- ✅ runtime_agent/
- ✅ streamlit_app/
- ✅ Docker artifacts

---

## 🎯 Key Features Demonstrated

| Lab | Feature | Capability |
|-----|---------|------------|
| 1 | Tools | Custom tool creation |
| 1 | Agent | Claude integration |
| 2 | Memory | Short/long-term storage |
| 2 | Hooks | Auto context retrieval |
| 3 | Gateway | Tool sharing |
| 3 | Auth | Authorization provider |
| 4 | Runtime | Serverless deployment |
| 4 | Observability | CloudWatch tracing |
| 5 | Frontend | Web application |
| 5 | Auth | Cognito integration |

---

## 💡 Tips & Tricks

### Speed Up Development
```bash
# Non-interactive mode
python run_workshop.py --all --non-interactive

# Skip validation
python run_workshop.py --lab 5 --no-validate
```

### Debug Mode
```bash
# Verbose output
export LOG_LEVEL=DEBUG
python lab1_implementation.py
```

### Custom Port
```bash
# Use different Streamlit port
cd streamlit_app
streamlit run main.py --server.port 8502
```

---

## 🆘 Troubleshooting

### Issue: Import Errors
```bash
make install
# Or: pip install -r requirements.txt --upgrade
```

### Issue: AWS Credentials
```bash
make aws-check
aws configure
```

### Issue: Port In Use
```bash
# Kill Streamlit
pkill -f streamlit
# Or use different port
make streamlit-port
```

### Issue: Docker Not Running
```bash
make docker-check
# Start Docker Desktop or daemon
```

---

## 🔗 Quick Links

### Essential Commands
- `make help` - Show all commands
- `make quick-start` - Complete setup
- `make run-all` - Run workshop
- `make frontend` - Launch app
- `make cleanup` - Remove resources

### Documentation
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start
- [SUMMARY.md](SUMMARY.md) - Implementation summary

### AWS Resources
- [Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [AgentCore Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Strands Framework](https://github.com/aws/strands)

---

## 🎉 Getting Started NOW

**Fastest path to running workshop:**

```bash
# 1. Install
make install

# 2. Validate
make validate

# 3. Run
make run-all

# 4. Test frontend (after Lab 5)
make frontend
```

**Or single command:**
```bash
make quick-start
```

---

## 📞 Support

- **Environment Issues**: Run `python validate_env.py`
- **AWS Issues**: Check `make aws-check`
- **Code Issues**: Review lab implementation files
- **Documentation**: See README.md

---

## 🎓 What You'll Learn

After completing this workshop:
- ✅ Build AI agents with custom tools
- ✅ Implement persistent memory
- ✅ Deploy to production runtime
- ✅ Create customer-facing applications
- ✅ Integrate authentication
- ✅ Monitor with CloudWatch
- ✅ Manage multi-agent systems

---

**Ready to start? → [QUICKSTART.md](QUICKSTART.md)**

**Need help? → [README.md](README.md)**

**Want overview? → [SUMMARY.md](SUMMARY.md)**

---

*Amazon Bedrock AgentCore Workshop - Complete Implementation Package*