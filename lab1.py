#!/usr/bin/env python3
"""
Lab 1: Create Agent Prototype

This script implements a customer support agent with local tools using Strands framework.
"""

import boto3
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Lab1Implementation:
    """Implementation of Lab 1: Agent Prototype"""
    
    def __init__(self, interactive: bool = False):
        self.interactive = interactive
        self.agent = None
        self.model = None
        self.tools = []
        self.region = boto3.Session().region_name
        
    def create_tools(self):
        """Create customer support tools"""
        from strands.tools import tool
        
        console.print("Creating customer support tools...")
        
        # Tool 1: Get Product Info
        @tool
        def get_product_info(product_type: str) -> str:
            """Get detailed technical specifications and information for electronics products.
            
            Args:
                product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')
            Returns:
                Formatted product information including warranty, features, and policies
            """
            products = {
                "laptops": {
                    "warranty": "1-year manufacturer warranty + optional extended coverage",
                    "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
                    "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
                    "compatibility": "Windows 11, macOS, Linux support varies by model",
                    "support": "Technical support and driver updates included",
                },
                "smartphones": {
                    "warranty": "1-year manufacturer warranty",
                    "specs": "5G/4G connectivity, 128GB-1TB storage, multiple camera systems",
                    "features": "Wireless charging, water resistance, biometric security",
                    "compatibility": "iOS/Android, carrier unlocked options available",
                    "support": "Software updates and technical support included",
                },
                "headphones": {
                    "warranty": "1-year manufacturer warranty",
                    "specs": "Wired/wireless options, noise cancellation, 20Hz-20kHz frequency",
                    "features": "Active noise cancellation, touch controls, voice assistant",
                    "compatibility": "Bluetooth 5.0+, 3.5mm jack, USB-C charging",
                    "support": "Firmware updates via companion app",
                },
                "monitors": {
                    "warranty": "3-year manufacturer warranty",
                    "specs": "4K/1440p/1080p resolutions, IPS/OLED panels, various sizes",
                    "features": "HDR support, high refresh rates, adjustable stands",
                    "compatibility": "HDMI, DisplayPort, USB-C inputs",
                    "support": "Color calibration and technical support",
                },
            }
            
            product = products.get(product_type.lower())
            if not product:
                return f"Technical specifications for {product_type} not available. Please contact our technical support team."
            
            return (
                f"Technical Information - {product_type.title()}:\n\n"
                f"• Warranty: {product['warranty']}\n"
                f"• Specifications: {product['specs']}\n"
                f"• Key Features: {product['features']}\n"
                f"• Compatibility: {product['compatibility']}\n"
                f"• Support: {product['support']}"
            )
        
        # Tool 2: Get Return Policy
        @tool
        def get_return_policy(product_category: str) -> str:
            """Get return policy information for a specific product category.
            
            Args:
                product_category: Electronics category (e.g., 'smartphones', 'laptops', 'accessories')
            Returns:
                Formatted return policy details including timeframes and conditions
            """
            return_policies = {
                "smartphones": {
                    "window": "30 days",
                    "condition": "Original packaging, no physical damage, factory reset required",
                    "process": "Online RMA portal or technical support",
                    "refund_time": "5-7 business days after inspection",
                    "shipping": "Free return shipping, prepaid label provided",
                    "warranty": "1-year manufacturer warranty included",
                },
                "laptops": {
                    "window": "30 days",
                    "condition": "Original packaging, all accessories, no software modifications",
                    "process": "Technical support verification required before return",
                    "refund_time": "7-10 business days after inspection",
                    "shipping": "Free return shipping with original packaging",
                    "warranty": "1-year manufacturer warranty, extended options available",
                },
                "accessories": {
                    "window": "30 days",
                    "condition": "Unopened packaging preferred, all components included",
                    "process": "Online return portal",
                    "refund_time": "3-5 business days after receipt",
                    "shipping": "Customer pays return shipping under $50",
                    "warranty": "90-day manufacturer warranty",
                },
            }
            
            default_policy = {
                "window": "30 days",
                "condition": "Original condition with all included components",
                "process": "Contact technical support",
                "refund_time": "5-7 business days after inspection",
                "shipping": "Return shipping policies vary",
                "warranty": "Standard manufacturer warranty applies",
            }
            
            policy = return_policies.get(product_category.lower(), default_policy)
            return (
                f"Return Policy - {product_category.title()}:\n\n"
                f"• Return window: {policy['window']} from delivery\n"
                f"• Condition: {policy['condition']}\n"
                f"• Process: {policy['process']}\n"
                f"• Refund timeline: {policy['refund_time']}\n"
                f"• Shipping: {policy['shipping']}\n"
                f"• Warranty: {policy['warranty']}"
            )
        
        # Tool 3: Web Search
        @tool
        def web_search(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
            """Search the web for updated information.
            
            Args:
                keywords: The search query keywords
                region: The search region (e.g., us-en, uk-en, ru-ru)
                max_results: The maximum number of results to return
            Returns:
                List of search results or error message
            """
            try:
                from ddgs import DDGS
                results = DDGS().text(keywords, region=region, max_results=max_results)
                return str(results) if results else "No results found."
            except Exception as e:
                return f"Search error: {str(e)}"
        
        # Tool 4: Get Technical Support (Mock - would use KB in real implementation)
        @tool
        def get_technical_support(issue_description: str) -> str:
            """Get technical support and troubleshooting guidance.
            
            Args:
                issue_description: Description of the technical issue
            Returns:
                Technical support guidance and troubleshooting steps
            """
            # Mock responses for common issues
            support_db = {
                "overheating": {
                    "steps": [
                        "Check if device is in a well-ventilated area",
                        "Close unnecessary background applications",
                        "Clean dust from ventilation ports",
                        "Update to latest software version",
                        "Check battery health in settings"
                    ],
                    "warning": "If overheating persists, device may need professional service"
                },
                "won't turn on": {
                    "steps": [
                        "Ensure device is charged (connect to power for 30+ minutes)",
                        "Try different power cable and adapter",
                        "Perform hard reset: Hold power button for 10-15 seconds",
                        "Check for physical damage to charging port",
                        "Try booting in safe mode if possible"
                    ],
                    "warning": "If device still won't turn on, contact support for service"
                },
                "slow performance": {
                    "steps": [
                        "Restart device to clear temporary files",
                        "Check available storage (aim for 20%+ free space)",
                        "Update to latest software version",
                        "Clear browser cache and unused apps",
                        "Run built-in diagnostic tools",
                        "Disable startup programs"
                    ],
                    "warning": "Performance may improve after updates and optimization"
                },
                "connectivity": {
                    "steps": [
                        "Toggle airplane mode on/off",
                        "Forget and reconnect to WiFi network",
                        "Restart router and device",
                        "Check for software updates",
                        "Reset network settings (saves passwords first)",
                        "Ensure correct network password entered"
                    ],
                    "warning": "Contact ISP if issue persists across multiple devices"
                }
            }
            
            # Find matching issue
            issue_lower = issue_description.lower()
            for key, support_info in support_db.items():
                if key in issue_lower:
                    steps_text = "\n".join([f"  {i+1}. {step}" for i, step in enumerate(support_info["steps"])])
                    return (
                        f"Technical Support - {key.title()}:\n\n"
                        f"Troubleshooting Steps:\n{steps_text}\n\n"
                        f"⚠️  {support_info['warning']}"
                    )
            
            # Generic response
            return (
                "Technical Support:\n\n"
                "For specific technical assistance:\n"
                "  1. Visit our online support portal\n"
                "  2. Contact technical support: 1-800-SUPPORT\n"
                "  3. Schedule an appointment at service center\n\n"
                "Please provide device model and detailed issue description."
            )
        
        self.tools = [get_product_info, get_return_policy, web_search, get_technical_support]
        console.print(f"[green]✓[/green] Created {len(self.tools)} tools")
        
    def create_model(self):
        """Create Bedrock model"""
        from strands.models import BedrockModel
        
        console.print("Initializing Bedrock model...")
        
        model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        
        try:
            self.model = BedrockModel(
                model_id=model_id,
                temperature=0.3,
                region_name=self.region
            )
            console.print(f"[green]✓[/green] Model initialized: {model_id}")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize model: {e}")
            return False
    
    def create_agent(self):
        """Create the customer support agent"""
        from strands import Agent
        
        console.print("Creating customer support agent...")
        
        system_prompt = """You are a helpful and professional customer support assistant for an electronics e-commerce company.
Your role is to:
- Provide accurate information using the tools available to you
- Support customers with technical information, product specifications, and maintenance questions
- Be friendly, patient, and understanding with customers
- Always offer additional help after answering questions
- If you can't help with something, direct customers to the appropriate contact

You have access to the following tools:
1. get_product_info() - For product specifications and features
2. get_return_policy() - For warranty and return policy questions
3. web_search() - For current information and troubleshooting
4. get_technical_support() - For technical issues and troubleshooting

Always use the appropriate tool to get accurate information."""
        
        try:
            self.agent = Agent(
                model=self.model,
                tools=self.tools,
                system_prompt=system_prompt
            )
            console.print("[green]✓[/green] Customer support agent created")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create agent: {e}")
            return False
    
    def test_agent(self):
        """Test the agent with sample queries"""
        console.print("\n[bold]Testing agent with sample queries...[/bold]\n")
        
        test_queries = [
            "What's the return policy for laptops?",
            "My smartphone is overheating. What should I do?",
            "What are the specifications for your headphones?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            console.print(f"[cyan]Test {i}:[/cyan] {query}")
            
            try:
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Agent thinking...", total=None)
                    response = self.agent(query)
                    progress.update(task, completed=True)
                
                console.print(Panel(
                    response.message["content"][0]["text"],
                    title="Agent Response",
                    border_style="green"
                ))
                console.print()
                
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}\n")
                return False
        
        return True
    
    def run(self) -> bool:
        """Execute Lab 1 implementation"""
        console.print(Panel.fit(
            "[bold]Lab 1: Create Agent Prototype[/bold]\n\n"
            "Objectives:\n"
            "  • Create custom tools for customer support\n"
            "  • Initialize Bedrock model\n"
            "  • Build agent with Strands framework\n"
            "  • Test agent functionality",
            border_style="cyan"
        ))
        
        try:
            # Step 1: Create tools
            console.print("\n[bold]Step 1: Creating Tools[/bold]")
            self.create_tools()
            
            # Step 2: Create model
            console.print("\n[bold]Step 2: Initializing Model[/bold]")
            if not self.create_model():
                return False
            
            # Step 3: Create agent
            console.print("\n[bold]Step 3: Creating Agent[/bold]")
            if not self.create_agent():
                return False
            
            # Step 4: Test agent
            console.print("\n[bold]Step 4: Testing Agent[/bold]")
            if not self.test_agent():
                return False
            
            console.print("\n[bold green]Lab 1 completed successfully! ✓[/bold green]\n")
            console.print("[cyan]What we built:[/cyan]")
            console.print("  ✓ 4 customer support tools")
            console.print("  ✓ Claude 3.7 Sonnet model")
            console.print("  ✓ Functional customer support agent")
            console.print("  ✓ Tool calling and response generation")
            
            return True
            
        except Exception as e:
            console.print(f"\n[red]Lab 1 failed: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return False


if __name__ == "__main__":
    lab1 = Lab1Implementation(interactive=True)
    success = lab1.run()
    exit(0 if success else 1)