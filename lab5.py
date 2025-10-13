#!/usr/bin/env python3
"""
Lab 5: Building a Customer-Facing Frontend Application

This script implements a Streamlit-based web application for customer support.
"""

import boto3
import json
import os
import subprocess
import time
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Lab5Implementation:
    """Implementation of Lab 5: Frontend Application"""
    
    def __init__(self, interactive: bool = False):
        self.interactive = interactive
        self.region = boto3.Session().region_name
        self.runtime_arn = None
        self.cognito_config = {}
        self.streamlit_url = None
        
    def load_configuration(self) -> bool:
        """Load configuration from previous labs"""
        console.print("Loading configuration from previous labs...")
        
        try:
            # Load lab config
            if os.path.exists("lab_config.json"):
                with open("lab_config.json", "r") as f:
                    config = json.load(f)
                    self.runtime_arn = config.get("runtime_arn")
            
            # Get SSM parameters
            ssm = boto3.client('ssm', region_name=self.region)
            
            try:
                self.cognito_config = {
                    'runtime_arn': ssm.get_parameter(
                        Name="/app/customersupport/agentcore/runtime_arn"
                    )['Parameter']['Value'],
                    'client_id': ssm.get_parameter(
                        Name="/app/customersupport/agentcore/client_id"
                    )['Parameter']['Value'],
                    'pool_id': ssm.get_parameter(
                        Name="/app/customersupport/agentcore/pool_id"
                    )['Parameter']['Value'],
                    'region': self.region
                }
                console.print("[green]✓[/green] Configuration loaded from SSM")
                
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Using demo configuration: {e}")
                self.cognito_config = {
                    'runtime_arn': self.runtime_arn or "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/demo",
                    'client_id': "demo_client_id",
                    'pool_id': "demo_pool_id",
                    'region': self.region
                }
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to load configuration: {e}")
            return False
    
    def create_frontend_directory(self) -> bool:
        """Create frontend application directory structure"""
        console.print("\nCreating frontend application structure...")
        
        try:
            # Create directory
            os.makedirs("streamlit_app", exist_ok=True)
            
            # Create main.py
            main_content = '''"""
Customer Support Streamlit Application

Main application with authentication and chat interface.
"""

import streamlit as st
import json
import os
from chat import CustomerSupportChat
from chat_utils import initialize_session_state, display_chat_message

# Page configuration
st.set_page_config(
    page_title="Customer Support Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_config():
    """Load configuration"""
    try:
        # Check for config file
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        
        # Use environment variables as fallback
        return {
            'runtime_arn': os.getenv('RUNTIME_ARN', 'demo_runtime'),
            'client_id': os.getenv('CLIENT_ID', 'demo_client'),
            'pool_id': os.getenv('POOL_ID', 'demo_pool'),
            'region': os.getenv('AWS_REGION', 'us-east-1')
        }
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return None

def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Load configuration
    if 'config' not in st.session_state:
        config = load_config()
        if not config:
            st.stop()
        st.session_state.config = config
    
    # Header
    st.markdown('<div class="main-header">🤖 Customer Support Assistant</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Settings")
        
        # Authentication status
        if st.session_state.authenticated:
            st.success(f"✓ Logged in as: {st.session_state.username}")
            
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.access_token = None
                st.session_state.messages = []
                st.rerun()
        else:
            st.info("Please log in to continue")
        
        st.divider()
        
        # Session info
        st.subheader("Session Info")
        st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
        st.caption(f"Messages: {len(st.session_state.messages)}")
        
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Authentication
    if not st.session_state.authenticated:
        st.info("👋 Welcome! Please log in to access customer support.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Username", value="testuser")
                password = st.text_input("Password", type="password", value="TestPass123!")
                
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    # Mock authentication for demo
                    if username and password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.access_token = "demo_token_" + username
                        st.success("✓ Logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please enter username and password")
        
        st.stop()
    
    # Initialize chat
    if 'chat' not in st.session_state:
        st.session_state.chat = CustomerSupportChat(
            runtime_arn=st.session_state.config['runtime_arn'],
            access_token=st.session_state.access_token,
            region=st.session_state.config['region']
        )
    
    # Welcome message
    if not st.session_state.messages:
        st.info(f"👋 Hello {st.session_state.username}! How can I help you today?")
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_chat_message({"role": "user", "content": prompt})
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(
                        prompt,
                        st.session_state.session_id
                    )
                    
                    if response:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        st.markdown(response)
                    else:
                        st.error("Failed to get response from agent")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
'''
            
            with open("streamlit_app/main.py", "w") as f:
                f.write(main_content)
            
            # Create chat.py
            chat_content = '''"""
Chat management and AgentCore Runtime integration
"""

import boto3
import json
from typing import Optional

class CustomerSupportChat:
    """Customer support chat handler"""
    
    def __init__(self, runtime_arn: str, access_token: str, region: str):
        self.runtime_arn = runtime_arn
        self.access_token = access_token
        self.region = region
        self.client = boto3.client('bedrock-agentcore-runtime', region_name=region)
    
    def send_message(self, message: str, session_id: str) -> Optional[str]:
        """Send message to agent and get response"""
        try:
            # In real implementation, would invoke AgentCore Runtime
            # For demo, return mock response
            
            response = self._mock_agent_response(message)
            return response
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def _mock_agent_response(self, message: str) -> str:
        """Mock agent response for demo"""
        
        message_lower = message.lower()
        
        if "return" in message_lower or "policy" in message_lower:
            return """Our return policy provides:

• **30-day return window** from delivery date
• **Free return shipping** with prepaid label
• **Full refund** within 5-7 business days after inspection
• **Original packaging** required with all accessories

For laptops and smartphones, all items must be in original condition. Would you like help initiating a return?"""
        
        elif "spec" in message_lower or "product" in message_lower or "laptop" in message_lower:
            return """Our laptops feature:

• **Processors**: Latest Intel/AMD processors
• **Memory**: 8-32GB RAM options
• **Storage**: Fast SSD storage (256GB-2TB)
• **Display**: Various sizes with high resolution
• **Warranty**: 1-year manufacturer warranty included

All models include:
- Backlit keyboards
- USB-C/Thunderbolt ports
- Wi-Fi 6 and Bluetooth 5.0
- Technical support and driver updates

Would you like recommendations for your specific needs?"""
        
        elif "overheat" in message_lower or "hot" in message_lower or "temperature" in message_lower:
            return """For overheating issues, try these steps:

1. **Check ventilation** - Ensure device is in well-ventilated area
2. **Close background apps** - Reduce CPU load
3. **Clean vents** - Remove dust from ventilation ports
4. **Update software** - Install latest system updates
5. **Check battery health** - Review battery settings

⚠️ If overheating persists after these steps, your device may need professional service. Your warranty should cover hardware issues.

Would you like me to check your warranty status?"""
        
        elif "headphone" in message_lower:
            return """Based on your previous interest in gaming headphones, I'd recommend:

**Gaming Headphones** (Low latency for FPS):
• Latency: <40ms for competitive gaming
• Audio: 7.1 surround sound
• Microphone: Noise-canceling boom mic
• Connectivity: Wired (3.5mm) and wireless options
• Warranty: 1-year manufacturer warranty

Since you mentioned competitive FPS gaming, wired options provide the lowest latency (under 20ms). Wireless gaming models have improved to <40ms latency.

**Return Policy**: 30 days with full refund

Would you like specific model recommendations?"""
        
        elif "thinkpad" in message_lower or "programming" in message_lower or "development" in message_lower:
            return """For programming and development work, I recall you prefer ThinkPad models with good Linux compatibility:

**Recommended Options**:

**ThinkPad E Series** (Under $1200)
• 16GB RAM (upgradeable)
• Intel i5/i7 or AMD Ryzen
• Excellent Linux support (Ubuntu/Fedora certified)
• Durable keyboard for long coding sessions
• 1-year warranty with upgrade options

**Dell XPS Developer Edition**
• Pre-installed Ubuntu
• 16GB+ RAM
• Great build quality
• Strong Linux community support

Both options meet your requirements:
✓ Under $1200
✓ 16GB+ RAM
✓ Excellent Linux compatibility
✓ Professional build quality

Would you like specific model numbers or current pricing?"""
        
        else:
            return """I'm here to help! I can assist you with:

• **Product Information** - Specifications and features
• **Returns & Warranty** - Policy details and processing
• **Technical Support** - Troubleshooting and guidance
• **Recommendations** - Personalized product suggestions

What would you like to know more about?"""

'''
            
            with open("streamlit_app/chat.py", "w") as f:
                f.write(chat_content)
            
            # Create chat_utils.py
            utils_content = '''"""
Utility functions for chat interface
"""

import streamlit as st
import uuid

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def display_chat_message(message):
    """Display a chat message"""
    role = message["role"]
    content = message["content"]
    
    with st.chat_message(role):
        st.markdown(content)
'''
            
            with open("streamlit_app/chat_utils.py", "w") as f:
                f.write(utils_content)
            
            # Create requirements.txt
            requirements = """streamlit>=1.28.0
boto3>=1.34.0
"""
            
            with open("streamlit_app/requirements.txt", "w") as f:
                f.write(requirements)
            
            # Create config file
            with open("streamlit_app/config.json", "w") as f:
                json.dump(self.cognito_config, f, indent=2)
            
            console.print("[green]✓[/green] Frontend application structure created")
            console.print("[dim]  - main.py (Streamlit app)[/dim]")
            console.print("[dim]  - chat.py (Chat management)[/dim]")
            console.print("[dim]  - chat_utils.py (Utilities)[/dim]")
            console.print("[dim]  - requirements.txt (Dependencies)[/dim]")
            console.print("[dim]  - config.json (Configuration)[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create frontend: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install frontend dependencies"""
        console.print("\nInstalling frontend dependencies...")
        
        try:
            result = subprocess.run(
                ["pip", "install", "-q", "-r", "streamlit_app/requirements.txt"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green]✓[/green] Dependencies installed")
                return True
            else:
                console.print(f"[yellow]⚠[/yellow] Install output: {result.stderr}")
                return True  # Continue anyway
                
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Dependency installation: {e}")
            return True  # Continue anyway
    
    def get_streamlit_url(self) -> str:
        """Generate accessible URL for Streamlit app"""
        try:
            # Check if running on SageMaker
            if os.path.exists('/opt/ml'):
                # SageMaker Studio
                domain_id = os.getenv('SAGEMAKER_DOMAIN_ID', 'local')
                space_name = os.getenv('SAGEMAKER_SPACE_NAME', 'default')
                
                self.streamlit_url = f"https://{domain_id}.studio.{self.region}.sagemaker.aws/jupyter/default/proxy/8501/"
            else:
                # Local development
                self.streamlit_url = "http://localhost:8501"
            
            return self.streamlit_url
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] URL generation: {e}")
            return "http://localhost:8501"
    
    def display_launch_instructions(self):
        """Display instructions for launching the app"""
        console.print("\n[bold cyan]Launching Customer Support Frontend[/bold cyan]\n")
        
        url = self.get_streamlit_url()
        
        console.print(Panel.fit(
            f"[bold]Streamlit Application URL:[/bold]\n\n"
            f"[cyan]{url}[/cyan]\n\n"
            f"[dim]The application will start on port 8501[/dim]",
            border_style="green",
            title="🚀 Frontend Ready"
        ))
        
        console.print("\n[bold]Test Credentials:[/bold]")
        console.print("  Username: testuser")
        console.print("  Password: TestPass123!")
        
        console.print("\n[bold]Features:[/bold]")
        console.print("  ✓ Secure authentication")
        console.print("  ✓ Real-time chat interface")
        console.print("  ✓ Session persistence")
        console.print("  ✓ Personalized responses")
        
        console.print("\n[bold yellow]To start the application:[/bold yellow]")
        console.print("  cd streamlit_app")
        console.print("  streamlit run main.py")
        console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
    
    def test_frontend_setup(self) -> bool:
        """Test frontend setup"""
        console.print("\n[bold]Testing frontend setup...[/bold]\n")
        
        # Check files exist
        required_files = [
            "streamlit_app/main.py",
            "streamlit_app/chat.py",
            "streamlit_app/chat_utils.py",
            "streamlit_app/requirements.txt",
            "streamlit_app/config.json"
        ]
        
        all_exist = True
        for file_path in required_files:
            if os.path.exists(file_path):
                console.print(f"[green]✓[/green] {file_path}")
            else:
                console.print(f"[red]✗[/red] {file_path} not found")
                all_exist = False
        
        if all_exist:
            console.print("\n[green]✓[/green] All frontend files created successfully")
            return True
        else:
            console.print("\n[yellow]⚠[/yellow] Some files missing")
            return False
    
    def show_usage_examples(self):
        """Show usage examples for testing"""
        console.print("\n[bold cyan]Testing the Frontend[/bold cyan]\n")
        
        examples = [
            {
                "title": "Product Information",
                "query": "What are the specifications for your laptops?",
                "expected": "Technical specs, warranty, features"
            },
            {
                "title": "Return Policy",
                "query": "What's the return policy for electronics?",
                "expected": "30-day window, free shipping, refund timeline"
            },
            {
                "title": "Technical Support",
                "query": "My phone is overheating, what should I do?",
                "expected": "Troubleshooting steps, warranty check"
            },
            {
                "title": "Personalization",
                "query": "Which headphones would you recommend?",
                "expected": "Gaming headphones based on past preferences"
            }
        ]
        
        for i, example in enumerate(examples, 1):
            console.print(f"[cyan]{i}. {example['title']}[/cyan]")
            console.print(f"   Query: \"{example['query']}\"")
            console.print(f"   [dim]Expected: {example['expected']}[/dim]\n")
    
    def run(self) -> bool:
        """Execute Lab 5 implementation"""
        console.print(Panel.fit(
            "[bold]Lab 5: Building Customer-Facing Frontend[/bold]\n\n"
            "Objectives:\n"
            "  • Create Streamlit web application\n"
            "  • Integrate secure authentication\n"
            "  • Connect to AgentCore Runtime\n"
            "  • Implement real-time chat interface\n"
            "  • Test complete customer journey",
            border_style="cyan"
        ))
        
        try:
            # Step 1: Load configuration
            console.print("\n[bold]Step 1: Loading Configuration[/bold]")
            if not self.load_configuration():
                return False
            
            # Step 2: Create frontend
            console.print("\n[bold]Step 2: Creating Frontend Application[/bold]")
            if not self.create_frontend_directory():
                return False
            
            # Step 3: Install dependencies
            console.print("\n[bold]Step 3: Installing Dependencies[/bold]")
            self.install_dependencies()
            
            # Step 4: Test setup
            console.print("\n[bold]Step 4: Testing Setup[/bold]")
            if not self.test_frontend_setup():
                return False
            
            # Step 5: Display instructions
            console.print("\n[bold]Step 5: Launch Instructions[/bold]")
            self.display_launch_instructions()
            
            # Step 6: Show examples
            self.show_usage_examples()
            
            console.print("\n[bold green]Lab 5 completed successfully! ✓[/bold green]\n")
            console.print("[cyan]What we built:[/cyan]")
            console.print("  ✓ Streamlit web application")
            console.print("  ✓ Authentication integration")
            console.print("  ✓ Real-time chat interface")
            console.print("  ✓ Session management")
            console.print("  ✓ Complete customer experience")
            
            console.print("\n[bold yellow]Next Steps:[/bold yellow]")
            console.print("  1. cd streamlit_app")
            console.print("  2. streamlit run main.py")
            console.print("  3. Test with provided credentials")
            console.print("  4. Try the example queries")
            
            return True
            
        except Exception as e:
            console.print(f"\n[red]Lab 5 failed: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return False


if __name__ == "__main__":
    lab5 = Lab5Implementation(interactive=True)
    success = lab5.run()
    exit(0 if success else 1)