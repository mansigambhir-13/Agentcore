#!/usr/bin/env python3
"""
Amazon Bedrock AgentCore - Complete Demo Script

This script demonstrates the full capabilities of AgentCore from prototype to production.
Run this after completing the workshop setup to showcase key features.

Usage:
    python demo_agentcore.py --mode [quick|full|specific]
    
Modes:
    quick    - 5-minute executive demo (default)
    full     - 15-minute technical deep dive
    specific - Run specific lab demos
"""

import sys
import time
import argparse
import uuid
from typing import Dict, Any
import boto3
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class AgentCoreDemo:
    """Orchestrates AgentCore capability demonstrations"""
    
    def __init__(self):
        self.session = boto3.Session()
        self.region = self.session.region_name
        console.print(f"[bold cyan]🌍 Region:[/bold cyan] {self.region}")
        
    def welcome(self):
        """Display welcome message"""
        console.print(Panel.fit(
            "[bold magenta]Amazon Bedrock AgentCore[/bold magenta]\n"
            "[cyan]From Prototype to Production[/cyan]\n\n"
            "This demo showcases:\n"
            "  1️⃣  Local Agent Prototype\n"
            "  2️⃣  Persistent Memory & Personalization\n"
            "  3️⃣  Shared Tools via Gateway\n"
            "  4️⃣  Production Runtime Deployment\n"
            "  5️⃣  Customer-Facing Application\n",
            title="🚀 Workshop Demo",
            border_style="cyan"
        ))
        
    def demo_1_prototype(self):
        """Lab 1: Simple agent prototype"""
        console.print("\n[bold yellow]═══ Demo 1: Agent Prototype ═══[/bold yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Creating agent with local tools...", total=None)
            
            try:
                # Import required modules
                from strands import Agent
                from strands.models import BedrockModel
                from lab_helpers.lab1_strands_agent import (
                    get_product_info, 
                    get_return_policy,
                    get_technical_support,
                    web_search,
                    SYSTEM_PROMPT,
                    MODEL_ID
                )
                
                # Create model and agent
                model = BedrockModel(model_id=MODEL_ID, region_name=self.region)
                agent = Agent(
                    model=model,
                    tools=[get_product_info, get_return_policy, web_search, get_technical_support],
                    system_prompt=SYSTEM_PROMPT
                )
                
                progress.update(task, completed=True)
                console.print("[green]✓[/green] Agent created successfully!")
                
                # Demo query
                console.print("\n[cyan]Customer Query:[/cyan] 'What's the return policy for laptops?'")
                
                task2 = progress.add_task("Agent processing query...", total=None)
                response = agent("What's the return policy for laptops?")
                progress.update(task2, completed=True)
                
                # Display response
                console.print("\n[bold green]Agent Response:[/bold green]")
                console.print(Panel(response.message["content"][0]["text"], border_style="green"))
                
                # Show limitations
                console.print("\n[yellow]⚠️  Prototype Limitations:[/yellow]")
                console.print("   • No conversation memory beyond session")
                console.print("   • Tools not reusable across agents")
                console.print("   • Single user, local execution only")
                
            except Exception as e:
                console.print(f"[red]✗ Error:[/red] {str(e)}")
                console.print("[yellow]💡 Tip:[/yellow] Ensure Lab 1 notebook has been run first")
                
    def demo_2_memory(self):
        """Lab 2: Memory and personalization"""
        console.print("\n[bold yellow]═══ Demo 2: Memory & Personalization ═══[/bold yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            try:
                from bedrock_agentcore.memory import MemoryClient
                from lab_helpers.lab2_memory import (
                    CustomerSupportMemoryHooks,
                    create_or_get_memory_resource,
                    CUSTOMER_ID,
                    SESSION_ID
                )
                from strands import Agent
                from strands.models import BedrockModel
                from lab_helpers.lab1_strands_agent import (
                    get_product_info,
                    get_return_policy, 
                    web_search,
                    get_technical_support,
                    SYSTEM_PROMPT,
                    MODEL_ID
                )
                
                task = progress.add_task("Setting up memory...", total=None)
                
                # Get or create memory
                memory_id = create_or_get_memory_resource()
                memory_client = MemoryClient(region_name=self.region)
                
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Memory ID: {memory_id[:20]}...")
                
                # Create memory hooks
                task2 = progress.add_task("Creating memory-enhanced agent...", total=None)
                session_id = str(uuid.uuid4())
                memory_hooks = CustomerSupportMemoryHooks(
                    memory_id, memory_client, CUSTOMER_ID, session_id
                )
                
                model = BedrockModel(model_id=MODEL_ID, region_name=self.region)
                agent = Agent(
                    model=model,
                    tools=[get_product_info, get_return_policy, web_search, get_technical_support],
                    hooks=[memory_hooks],
                    system_prompt=SYSTEM_PROMPT
                )
                
                progress.update(task2, completed=True)
                console.print("[green]✓[/green] Memory-enhanced agent ready!")
                
                # Test personalization
                console.print("\n[cyan]Customer Query:[/cyan] 'Which headphones would you recommend?'")
                console.print("[dim]Note: Agent will use preferences from past interactions[/dim]")
                
                task3 = progress.add_task("Agent retrieving customer context...", total=None)
                response = agent("Which headphones would you recommend?")
                progress.update(task3, completed=True)
                
                console.print("\n[bold green]Agent Response (Personalized):[/bold green]")
                console.print(Panel(response.message["content"][0]["text"], border_style="green"))
                
                # Show capabilities
                console.print("\n[green]✓ Memory Capabilities:[/green]")
                console.print("   • Remembers customer preferences")
                console.print("   • Tracks past interactions")
                console.print("   • Provides personalized recommendations")
                console.print("   • Multi-tenant memory isolation")
                
            except Exception as e:
                console.print(f"[red]✗ Error:[/red] {str(e)}")
                console.print("[yellow]💡 Tip:[/yellow] Ensure Lab 2 notebook has been run first")
                
    def demo_3_gateway(self):
        """Lab 3: Gateway and identity"""
        console.print("\n[bold yellow]═══ Demo 3: Gateway & Shared Tools ═══[/bold yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            try:
                from lab_helpers.utils import get_ssm_parameter, get_or_create_cognito_pool
                from strands.tools.mcp import MCPClient
                from mcp.client.streamable_http import streamablehttp_client
                from strands import Agent
                from strands.models import BedrockModel
                from lab_helpers.lab1_strands_agent import (
                    get_product_info,
                    get_return_policy,
                    get_technical_support,
                    SYSTEM_PROMPT,
                    MODEL_ID
                )
                from lab_helpers.lab2_memory import (
                    CustomerSupportMemoryHooks,
                    create_or_get_memory_resource
                )
                from bedrock_agentcore.memory import MemoryClient
                
                task = progress.add_task("Setting up gateway connection...", total=None)
                
                # Get gateway details
                gateway_url = get_ssm_parameter("/app/customersupport/agentcore/gateway_url")
                cognito_config = get_or_create_cognito_pool(refresh_token=True)
                
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Gateway URL: {gateway_url[:40]}...")
                
                # Create MCP client
                task2 = progress.add_task("Authenticating with gateway...", total=None)
                mcp_client = MCPClient(
                    lambda: streamablehttp_client(
                        gateway_url,
                        headers={"Authorization": f"Bearer {cognito_config['bearer_token']}"}
                    )
                )
                progress.update(task2, completed=True)
                console.print("[green]✓[/green] Authentication successful!")
                
                # Create agent with gateway tools
                task3 = progress.add_task("Loading gateway tools...", total=None)
                
                with mcp_client:
                    gateway_tools = mcp_client.list_tools_sync()
                    progress.update(task3, completed=True)
                    
                    # Display available tools
                    table = Table(title="Available Tools")
                    table.add_column("Type", style="cyan")
                    table.add_column("Tool Name", style="green")
                    table.add_column("Description", style="white")
                    
                    # Local tools
                    table.add_row("Local", "get_product_info", "Product specifications")
                    table.add_row("Local", "get_return_policy", "Return policies")
                    table.add_row("Local", "get_technical_support", "KB retrieval")
                    
                    # Gateway tools
                    for tool in gateway_tools:
                        table.add_row("Gateway", tool.name, tool.description[:50] + "...")
                    
                    console.print(table)
                    
                    # Test gateway tool
                    console.print("\n[cyan]Customer Query:[/cyan] 'Check warranty for serial MNO33333333'")
                    
                    memory_id = create_or_get_memory_resource()
                    memory_client = MemoryClient(region_name=self.region)
                    memory_hooks = CustomerSupportMemoryHooks(
                        memory_id, memory_client, "customer_001", str(uuid.uuid4())
                    )
                    
                    model = BedrockModel(model_id=MODEL_ID, region_name=self.region)
                    agent = Agent(
                        model=model,
                        tools=[get_product_info, get_return_policy, get_technical_support] + gateway_tools,
                        hooks=[memory_hooks],
                        system_prompt=SYSTEM_PROMPT
                    )
                    
                    task4 = progress.add_task("Agent using gateway tool...", total=None)
                    response = agent("Check warranty for serial MNO33333333")
                    progress.update(task4, completed=True)
                    
                    console.print("\n[bold green]Agent Response:[/bold green]")
                    console.print(Panel(response.message["content"][0]["text"], border_style="green"))
                    
                console.print("\n[green]✓ Gateway Benefits:[/green]")
                console.print("   • Centralized tool infrastructure")
                console.print("   • Reusable across multiple agents")
                console.print("   • Secure JWT authentication")
                console.print("   • Access to existing enterprise APIs")
                
            except Exception as e:
                console.print(f"[red]✗ Error:[/red] {str(e)}")
                console.print("[yellow]💡 Tip:[/yellow] Ensure Lab 3 notebook has been run first")
                
    def demo_4_runtime(self):
        """Lab 4: Production runtime"""
        console.print("\n[bold yellow]═══ Demo 4: Production Runtime ═══[/bold yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            try:
                from bedrock_agentcore_starter_toolkit import Runtime
                from lab_helpers.utils import get_ssm_parameter, get_or_create_cognito_pool
                
                task = progress.add_task("Connecting to runtime...", total=None)
                
                # Get runtime details
                runtime_arn = get_ssm_parameter("/app/customersupport/agentcore/runtime_arn")
                cognito_config = get_or_create_cognito_pool(refresh_token=True)
                
                runtime = Runtime()
                
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] Runtime ARN: {runtime_arn[:50]}...")
                
                # Check runtime status
                task2 = progress.add_task("Checking runtime status...", total=None)
                status_response = runtime.status()
                status = status_response.endpoint["status"]
                progress.update(task2, completed=True)
                
                if status == "READY":
                    console.print(f"[green]✓[/green] Runtime Status: {status}")
                else:
                    console.print(f"[yellow]⚠[/yellow] Runtime Status: {status}")
                    console.print("[dim]Runtime may still be deploying...[/dim]")
                    return
                
                # Test invocation
                console.print("\n[cyan]Test Query:[/cyan] 'List all of your tools'")
                
                task3 = progress.add_task("Invoking production runtime...", total=None)
                session_id = str(uuid.uuid4())
                
                response = runtime.invoke(
                    {"prompt": "List all of your tools"},
                    bearer_token=cognito_config["bearer_token"],
                    session_id=session_id
                )
                
                progress.update(task3, completed=True)
                
                console.print("\n[bold green]Runtime Response:[/bold green]")
                console.print(Panel(response["response"], border_style="green"))
                
                # Test session continuity
                console.print("\n[cyan]Follow-up Query (Same Session):[/cyan] 'What can you help me with?'")
                
                task4 = progress.add_task("Testing session persistence...", total=None)
                response2 = runtime.invoke(
                    {"prompt": "What can you help me with?"},
                    bearer_token=cognito_config["bearer_token"],
                    session_id=session_id  # Same session
                )
                progress.update(task4, completed=True)
                
                console.print("\n[bold green]Runtime Response:[/bold green]")
                console.print(Panel(response2["response"], border_style="green"))
                
                # Show production features
                console.print("\n[green]✓ Production Features:[/green]")
                console.print("   • Serverless auto-scaling")
                console.print("   • Session persistence across invocations")
                console.print("   • Built-in observability (CloudWatch)")
                console.print("   • JWT authentication & authorization")
                console.print("   • Multi-user support")
                
                console.print("\n[cyan]💡 View traces:[/cyan]")
                console.print("   AWS Console → CloudWatch → GenAI Observability → Bedrock AgentCore")
                
            except Exception as e:
                console.print(f"[red]✗ Error:[/red] {str(e)}")
                console.print("[yellow]💡 Tip:[/yellow] Ensure Lab 4 notebook has been run and runtime is deployed")
                
    def demo_5_frontend(self):
        """Lab 5: Frontend application"""
        console.print("\n[bold yellow]═══ Demo 5: Customer-Facing Application ═══[/bold yellow]\n")
        
        try:
            from lab_helpers.lab5_frontend.sagemaker_helper import get_streamlit_url
            
            streamlit_url = get_streamlit_url()
            
            console.print(Panel.fit(
                f"[bold cyan]Streamlit Application URL:[/bold cyan]\n\n"
                f"[link={streamlit_url}]{streamlit_url}[/link]\n\n"
                f"[yellow]Features:[/yellow]\n"
                f"  • Secure Cognito authentication\n"
                f"  • Real-time chat interface\n"
                f"  • Session persistence\n"
                f"  • Response streaming\n"
                f"  • Performance metrics\n\n"
                f"[green]To start:[/green]\n"
                f"  cd lab_helpers/lab5_frontend/\n"
                f"  streamlit run main.py",
                title="🖥️  Frontend Demo",
                border_style="cyan"
            ))
            
            console.print("\n[cyan]Test Scenarios:[/cyan]")
            console.print("  1. Login with Cognito credentials")
            console.print("  2. Ask: 'What are laptop specifications?'")
            console.print("  3. Ask: 'What's the return policy?'")
            console.print("  4. Ask: 'My iPhone is overheating, help!'")
            console.print("  5. Refresh page - conversation persists!")
            
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {str(e)}")
            console.print("[yellow]💡 Tip:[/yellow] Ensure Lab 5 dependencies are installed")
            
    def show_architecture_summary(self):
        """Display architecture summary"""
        console.print("\n[bold cyan]═══ Architecture Summary ═══[/bold cyan]\n")
        
        table = Table(title="AgentCore Components")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Service", style="green")
        table.add_column("Purpose", style="white")
        
        table.add_row(
            "Agent", 
            "Strands Framework", 
            "Agentic orchestration & tool calling"
        )
        table.add_row(
            "Memory", 
            "AgentCore Memory", 
            "Short & long-term memory storage"
        )
        table.add_row(
            "Gateway", 
            "AgentCore Gateway", 
            "Centralized MCP tool endpoints"
        )
        table.add_row(
            "Runtime", 
            "AgentCore Runtime", 
            "Production deployment & scaling"
        )
        table.add_row(
            "Identity", 
            "Cognito + AgentCore", 
            "JWT authentication & authorization"
        )
        table.add_row(
            "Observability", 
            "CloudWatch GenAI", 
            "Traces, metrics, and logging"
        )
        table.add_row(
            "Frontend", 
            "Streamlit", 
            "Customer-facing web application"
        )
        
        console.print(table)
        
    def run_quick_demo(self):
        """Run 5-minute executive demo"""
        self.welcome()
        time.sleep(2)
        
        self.demo_1_prototype()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        self.demo_2_memory()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        self.demo_3_gateway()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        self.demo_4_runtime()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        self.demo_5_frontend()
        
        self.show_architecture_summary()
        
        console.print("\n[bold green]✓ Demo Complete![/bold green]")
        console.print("[cyan]You've seen the complete journey from prototype to production! 🚀[/cyan]")
        
    def run_full_demo(self):
        """Run 15-minute technical deep dive"""
        self.welcome()
        time.sleep(2)
        
        console.print("\n[bold magenta]═══ PART 1: Architecture Evolution ═══[/bold magenta]")
        self.show_architecture_summary()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        console.print("\n[bold magenta]═══ PART 2: Memory Intelligence ═══[/bold magenta]")
        self.demo_2_memory()
        
        # Additional memory analysis
        console.print("\n[cyan]Memory Analysis:[/cyan]")
        try:
            from bedrock_agentcore.memory import MemoryClient
            from lab_helpers.utils import get_ssm_parameter
            
            memory_id = get_ssm_parameter("/app/customersupport/agentcore/memory_id")
            memory_client = MemoryClient(region_name=self.region)
            
            # Retrieve preference memories
            pref_memories = memory_client.retrieve_memories(
                memory_id=memory_id,
                namespace="support/customer/customer_001/preferences",
                query="customer preferences",
                top_k=5
            )
            
            console.print(f"\n[green]Found {len(pref_memories)} preference memories:[/green]")
            for i, mem in enumerate(pref_memories[:3], 1):
                if isinstance(mem, dict):
                    text = mem.get("content", {}).get("text", "")
                    console.print(f"  {i}. {text}")
                    
        except Exception as e:
            console.print(f"[yellow]Could not retrieve memories: {e}[/yellow]")
            
        input("\n[dim]Press Enter to continue...[/dim]")
        
        console.print("\n[bold magenta]═══ PART 3: Gateway & Identity ═══[/bold magenta]")
        self.demo_3_gateway()
        input("\n[dim]Press Enter to continue...[/dim]")
        
        console.print("\n[bold magenta]═══ PART 4: Production Operations ═══[/bold magenta]")
        self.demo_4_runtime()
        
        console.print("\n[cyan]Observability Deep Dive:[/cyan]")
        console.print("  Navigate to: CloudWatch → GenAI Observability → Bedrock AgentCore")
        console.print("  View:")
        console.print("    • Agents - All deployed runtimes")
        console.print("    • Sessions - User conversation sessions")
        console.print("    • Traces - Detailed execution with timing")
        console.print("    • Metrics - Performance and error rates")
        
        input("\n[dim]Press Enter to continue...[/dim]")
        
        self.demo_5_frontend()
        
        console.print("\n[bold green]✓ Full Demo Complete![/bold green]")
        console.print("[cyan]You've completed the technical deep dive! 🎓[/cyan]")


def main():
    parser = argparse.ArgumentParser(description="AgentCore Demo Script")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "specific"],
        default="quick",
        help="Demo mode (default: quick)"
    )
    parser.add_argument(
        "--lab",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Specific lab to demo (use with --mode specific)"
    )
    
    args = parser.parse_args()
    
    demo = AgentCoreDemo()
    
    try:
        if args.mode == "quick":
            demo.run_quick_demo()
        elif args.mode == "full":
            demo.run_full_demo()
        elif args.mode == "specific":
            if not args.lab:
                console.print("[red]Error: --lab required with --mode specific[/red]")
                sys.exit(1)
            
            demo.welcome()
            
            if args.lab == 1:
                demo.demo_1_prototype()
            elif args.lab == 2:
                demo.demo_2_memory()
            elif args.lab == 3:
                demo.demo_3_gateway()
            elif args.lab == 4:
                demo.demo_4_runtime()
            elif args.lab == 5:
                demo.demo_5_frontend()
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Demo error: {str(e)}[/red]")
        console.print("\n[yellow]💡 Troubleshooting tips:[/yellow]")
        console.print("  1. Ensure all lab notebooks have been run")
        console.print("  2. Check AWS credentials are configured")
        console.print("  3. Verify region has required services")
        console.print("  4. Check CloudFormation stack deployed successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()