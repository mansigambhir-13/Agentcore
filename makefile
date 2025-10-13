# AgentCore Workshop Makefile
# Convenient commands for running the workshop

.PHONY: help install validate run-all lab1 lab2 lab4 lab5 lab6 frontend cleanup clean

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "AgentCore Workshop - Available Commands"
	@echo "========================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make install    # Install dependencies"
	@echo "  make validate   # Validate environment"
	@echo "  make run-all    # Run complete workshop"
	@echo ""

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

validate: ## Validate environment setup
	@echo "🔍 Validating environment..."
	python validate_env.py

run-all: ## Run all labs in sequence
	@echo "🚀 Starting complete workshop..."
	python run_workshop.py --all

run-all-auto: ## Run all labs automatically (non-interactive)
	@echo "🚀 Starting automated workshop..."
	python run_workshop.py --all --non-interactive

lab1: ## Run Lab 1: Agent Prototype
	@echo "🤖 Running Lab 1: Agent Prototype..."
	python lab1_implementation.py

lab2: ## Run Lab 2: Memory & Personalization
	@echo "🧠 Running Lab 2: Memory & Personalization..."
	python lab2_implementation.py

lab4: ## Run Lab 4: Production Runtime
	@echo "🚀 Running Lab 4: Production Runtime..."
	python lab4_implementation.py

lab5: ## Run Lab 5: Customer Frontend
	@echo "🎨 Running Lab 5: Customer Frontend..."
	python lab5_implementation.py

lab6: ## Run Lab 6: Complete Cleanup
	@echo "🧹 Running Lab 6: Cleanup..."
	python lab6_implementation.py

frontend: ## Launch the Streamlit frontend
	@echo "🎨 Launching Streamlit frontend..."
	@echo "📱 Access at: http://localhost:8501"
	cd streamlit_app && streamlit run main.py

cleanup: lab6 ## Alias for lab6 (complete cleanup)

clean: ## Clean local generated files
	@echo "🧹 Cleaning local files..."
	rm -f lab_config.json
	rm -rf runtime_agent/
	rm -rf streamlit_app/
	rm -f .bedrock_agentcore.yaml
	rm -f Dockerfile
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Local cleanup complete!"

test: ## Run environment validation
	@echo "🧪 Testing environment..."
	python validate_env.py

check: validate ## Alias for validate

info: ## Show workshop information
	@echo "Amazon Bedrock AgentCore Workshop"
	@echo "================================="
	@echo ""
	@echo "📚 Labs:"
	@echo "  Lab 1: Agent Prototype"
	@echo "  Lab 2: Memory & Personalization"
	@echo "  Lab 3: Gateway & Identity (separate)"
	@echo "  Lab 4: Production Runtime"
	@echo "  Lab 5: Customer Frontend"
	@echo "  Lab 6: Complete Cleanup"
	@echo ""
	@echo "⏱️  Duration: ~30-45 minutes"
	@echo "🎯 What You'll Build:"
	@echo "  ✓ AI agent with custom tools"
	@echo "  ✓ Persistent memory system"
	@echo "  ✓ Production serverless runtime"
	@echo "  ✓ Customer-facing web application"
	@echo ""
	@echo "📖 Documentation:"
	@echo "  README.md        - Full documentation"
	@echo "  QUICKSTART.md    - Quick start guide"
	@echo "  SUMMARY.md       - Implementation summary"
	@echo ""

quick-start: install validate run-all ## Full quick start (install, validate, run)

# Development commands
dev-install: ## Install with development dependencies
	pip install -r requirements.txt
	pip install black pylint pytest pytest-asyncio

lint: ## Run code linting
	@echo "🔍 Running linters..."
	pylint lab*_implementation.py run_workshop.py --disable=C0111,R0913,R0914 || true
	black --check *.py || true

format: ## Format code with black
	@echo "✨ Formatting code..."
	black *.py

# AWS commands
aws-check: ## Check AWS credentials
	@echo "🔐 Checking AWS credentials..."
	aws sts get-caller-identity

aws-region: ## Show current AWS region
	@echo "🌍 Current AWS region:"
	@aws configure get region || echo "Not set"

aws-logs: ## Tail CloudWatch logs (if available)
	@echo "📊 Tailing CloudWatch logs..."
	aws logs tail /aws/bedrock/agentcore/runtime --follow || echo "No logs found"

# Docker commands (for Lab 4)
docker-check: ## Check Docker status
	@echo "🐳 Checking Docker..."
	docker --version || echo "Docker not installed"
	docker ps 2>/dev/null || echo "Docker not running"

docker-clean: ## Clean Docker images (Lab 4)
	@echo "🐳 Cleaning Docker resources..."
	docker system prune -f || echo "Docker not available"

# Streamlit commands
streamlit-hello: ## Test Streamlit installation
	@echo "🎨 Testing Streamlit..."
	streamlit hello

streamlit-port: ## Launch Streamlit on custom port
	@echo "🎨 Launching Streamlit on port 8502..."
	cd streamlit_app && streamlit run main.py --server.port 8502

# Utility commands
tree: ## Show project structure
	@echo "📁 Project structure:"
	@tree -L 2 -I '__pycache__|*.pyc|.git' || ls -la

status: ## Show workshop status
	@echo "📊 Workshop Status"
	@echo "=================="
	@echo ""
	@echo "Generated files:"
	@test -f lab_config.json && echo "  ✓ lab_config.json" || echo "  ✗ lab_config.json"
	@test -d runtime_agent && echo "  ✓ runtime_agent/" || echo "  ✗ runtime_agent/"
	@test -d streamlit_app && echo "  ✓ streamlit_app/" || echo "  ✗ streamlit_app/"
	@echo ""

version: ## Show Python and package versions
	@echo "🐍 Python: $$(python --version)"
	@echo "📦 pip: $$(pip --version)"
	@echo "🤖 boto3: $$(pip show boto3 2>/dev/null | grep Version || echo 'Not installed')"
	@echo "🎨 streamlit: $$(pip show streamlit 2>/dev/null | grep Version || echo 'Not installed')"

# Complete workflow
workshop: install validate run-all ## Complete workshop workflow

workshop-auto: install validate run-all-auto ## Complete workshop (automated)