#!/usr/bin/env python3
"""
Lab 2: Add Memory & Personalization

This script implements AgentCore Memory with short and long-term strategies.
"""

import boto3
import uuid
import time
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Lab2Implementation:
    """Implementation of Lab 2: Memory & Personalization"""
    
    def __init__(self, interactive: bool = False):
        self.interactive = interactive
        self.memory_id = None
        self.memory_client = None
        self.agent = None
        self.region = boto3.Session().region_name
        self.actor_id = "customer_001"
        self.session_id = str(uuid.uuid4())
        
    def create_memory_resource(self) -> bool:
        """Create AgentCore Memory resource"""
        from bedrock_agentcore.memory import MemoryClient
        from bedrock_agentcore.memory.constants import StrategyType
        
        console.print("Creating AgentCore Memory resource...")
        console.print("[dim]This will take 2-3 minutes as AWS provisions the infrastructure...[/dim]")
        
        try:
            self.memory_client = MemoryClient(region_name=self.region)
            
            # Define memory strategies
            strategies = [
                {
                    StrategyType.USER_PREFERENCE.value: {
                        "name": "CustomerPreferences",
                        "description": "Captures customer preferences and behavior patterns",
                        "namespaces": ["support/customer/{actorId}/preferences"],
                    }
                },
                {
                    StrategyType.SEMANTIC.value: {
                        "name": "CustomerSupportSemantic",
                        "description": "Stores factual information from conversations",
                        "namespaces": ["support/customer/{actorId}/semantic"],
                    }
                },
            ]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}")
            ) as progress:
                task = progress.add_task("Creating memory resource...", total=None)
                
                response = self.memory_client.create_memory_and_wait(
                    name="CustomerSupportMemory",
                    description="Customer support agent memory with preferences and semantic storage",
                    strategies=strategies,
                    event_expiry_days=90,
                    timeout=300  # 5 minutes
                )
                
                progress.update(task, completed=True)
            
            self.memory_id = response["id"]
            console.print(f"[green]✓[/green] Memory created: {self.memory_id}")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create memory: {e}")
            return False
    
    def seed_customer_history(self) -> bool:
        """Seed memory with customer interaction history"""
        console.print("\nSeeding customer history...")
        
        previous_interactions = [
            ("I'm having issues with my MacBook Pro overheating during video editing.", "USER"),
            ("I can help with that thermal issue. For video editing workloads, let's check your Activity Monitor and adjust performance settings. Your MacBook Pro order #MB-78432 is still under warranty.", "ASSISTANT"),
            ("What's the return policy on gaming headphones? I need low latency for competitive FPS games", "USER"),
            ("For gaming headphones, you have 30 days to return. Since you're into competitive FPS, I'd recommend checking the audio latency specs - most gaming models have <40ms latency.", "ASSISTANT"),
            ("I need a laptop under $1200 for programming. Prefer 16GB RAM minimum and good Linux compatibility. I like ThinkPad models.", "USER"),
            ("Perfect! For development work, I'd suggest looking at our ThinkPad E series or Dell XPS models. Both have excellent Linux support and 16GB RAM options within your budget.", "ASSISTANT"),
        ]
        
        try:
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id="previous_session",
                messages=previous_interactions
            )
            
            console.print(f"[green]✓[/green] Seeded {len(previous_interactions)//2} conversations")
            console.print("[dim]Long-term memory processing will complete in 20-30 seconds...[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to seed history: {e}")
            return False
    
    def wait_for_memory_processing(self) -> bool:
        """Wait for long-term memory to process"""
        console.print("\nWaiting for long-term memory processing...")
        
        max_retries = 6
        for retry in range(max_retries):
            try:
                memories = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=f"support/customer/{self.actor_id}/preferences",
                    query="customer preferences and past interactions"
                )
                
                if memories:
                    console.print(f"[green]✓[/green] Found {len(memories)} processed memories")
                    
                    # Display sample memories
                    console.print("\n[cyan]Sample extracted preferences:[/cyan]")
                    for i, mem in enumerate(memories[:3], 1):
                        if isinstance(mem, dict):
                            text = mem.get("content", {}).get("text", "")
                            if text:
                                console.print(f"  {i}. {text}")
                    
                    return True
                
                if retry < max_retries - 1:
                    console.print(f"[dim]Waiting... ({retry+1}/{max_retries})[/dim]")
                    time.sleep(10)
                    
            except Exception as e:
                console.print(f"[yellow]Retry {retry+1}: {e}[/yellow]")
                time.sleep(10)
        
        console.print("[yellow]⚠[/yellow] Memory processing taking longer than expected")
        console.print("[dim]Memories may still process in background[/dim]")
        return True  # Continue anyway
    
    def create_memory_hooks(self):
        """Create memory hooks for agent integration"""
        from strands.hooks import (
            HookProvider,
            HookRegistry,
            MessageAddedEvent,
            AfterInvocationEvent
        )
        
        console.print("\nCreating memory hooks...")
        
        class CustomerSupportMemoryHooks(HookProvider):
            """Memory hooks for customer support agent"""
            
            def __init__(self, memory_id: str, client, actor_id: str, session_id: str):
                self.memory_id = memory_id
                self.client = client
                self.actor_id = actor_id
                self.session_id = session_id
                
                # Get namespaces
                strategies = self.client.get_memory_strategies(self.memory_id)
                self.namespaces = {
                    s["type"]: s["namespaces"][0]
                    for s in strategies
                }
            
            def retrieve_customer_context(self, event: MessageAddedEvent):
                """Retrieve customer context before processing"""
                messages = event.agent.messages
                if messages[-1]["role"] == "user" and "toolResult" not in messages[-1]["content"][0]:
                    user_query = messages[-1]["content"][0]["text"]
                    
                    try:
                        all_context = []
                        
                        # Retrieve from all namespaces
                        for context_type, namespace in self.namespaces.items():
                            memories = self.client.retrieve_memories(
                                memory_id=self.memory_id,
                                namespace=namespace.format(actorId=self.actor_id),
                                query=user_query,
                                top_k=3
                            )
                            
                            for memory in memories:
                                if isinstance(memory, dict):
                                    text = memory.get("content", {}).get("text", "").strip()
                                    if text:
                                        all_context.append(f"[{context_type.upper()}] {text}")
                        
                        # Inject context
                        if all_context:
                            context_text = "\n".join(all_context)
                            original_text = messages[-1]["content"][0]["text"]
                            messages[-1]["content"][0]["text"] = (
                                f"Customer Context:\n{context_text}\n\n{original_text}"
                            )
                            
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not retrieve context: {e}[/yellow]")
            
            def save_support_interaction(self, event: AfterInvocationEvent):
                """Save interaction to memory"""
                try:
                    messages = event.agent.messages
                    if len(messages) >= 2 and messages[-1]["role"] == "assistant":
                        # Extract last user/assistant pair
                        customer_query = None
                        agent_response = None
                        
                        for msg in reversed(messages):
                            if msg["role"] == "assistant" and not agent_response:
                                agent_response = msg["content"][0]["text"]
                            elif msg["role"] == "user" and not customer_query and "toolResult" not in msg["content"][0]:
                                customer_query = msg["content"][0]["text"]
                                break
                        
                        if customer_query and agent_response:
                            self.client.create_event(
                                memory_id=self.memory_id,
                                actor_id=self.actor_id,
                                session_id=self.session_id,
                                messages=[
                                    (customer_query, "USER"),
                                    (agent_response, "ASSISTANT")
                                ]
                            )
                            
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not save interaction: {e}[/yellow]")
            
            def register_hooks(self, registry: HookRegistry) -> None:
                """Register hooks"""
                registry.add_callback(MessageAddedEvent, self.retrieve_customer_context)
                registry.add_callback(AfterInvocationEvent, self.save_support_interaction)
        
        self.memory_hooks = CustomerSupportMemoryHooks(
            self.memory_id,
            self.memory_client,
            self.actor_id,
            self.session_id
        )
        
        console.print("[green]✓[/green] Memory hooks created")
        return self.memory_hooks
    
    def create_agent_with_memory(self, memory_hooks) -> bool:
        """Create agent with memory integration"""
        from strands import Agent
        from strands.models import BedrockModel
        from lab1_implementation import Lab1Implementation
        
        console.print("\nCreating memory-enhanced agent...")
        
        try:
            # Get tools from Lab 1
            lab1 = Lab1Implementation()
            lab1.create_tools()
            
            # Create model
            model = BedrockModel(
                model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                temperature=0.3,
                region_name=self.region
            )
            
            # Create agent with memory hooks
            system_prompt = """You are a helpful customer support assistant with access to customer history.
Use the customer context provided to personalize your responses and remember past interactions."""
            
            self.agent = Agent(
                model=model,
                tools=lab1.tools,
                hooks=[memory_hooks],
                system_prompt=system_prompt
            )
            
            console.print("[green]✓[/green] Agent with memory created")
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to create agent: {e}")
            return False
    
    def test_personalization(self) -> bool:
        """Test agent's personalized responses"""
        console.print("\n[bold]Testing personalization...[/bold]\n")
        
        test_queries = [
            "Which headphones would you recommend?",
            "What's my preferred laptop brand?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            console.print(f"[cyan]Test {i}:[/cyan] {query}")
            console.print("[dim]Agent should use past preferences to personalize response...[/dim]")
            
            try:
                response = self.agent(query)
                console.print(Panel(
                    response.message["content"][0]["text"],
                    title="Personalized Response",
                    border_style="green"
                ))
                console.print()
                
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}\n")
                return False
        
        return True
    
    def run(self) -> bool:
        """Execute Lab 2 implementation"""
        console.print(Panel.fit(
            "[bold]Lab 2: Add Memory & Personalization[/bold]\n\n"
            "Objectives:\n"
            "  • Create AgentCore Memory resource\n"
            "  • Seed customer interaction history\n"
            "  • Implement memory hooks\n"
            "  • Test personalized responses",
            border_style="cyan"
        ))
        
        try:
            # Step 1: Create memory
            console.print("\n[bold]Step 1: Creating Memory Resource[/bold]")
            if not self.create_memory_resource():
                return False
            
            # Step 2: Seed history
            console.print("\n[bold]Step 2: Seeding Customer History[/bold]")
            if not self.seed_customer_history():
                return False
            
            # Step 3: Wait for processing
            console.print("\n[bold]Step 3: Waiting for Memory Processing[/bold]")
            self.wait_for_memory_processing()
            
            # Step 4: Create hooks
            console.print("\n[bold]Step 4: Creating Memory Hooks[/bold]")
            memory_hooks = self.create_memory_hooks()
            
            # Step 5: Create agent
            console.print("\n[bold]Step 5: Creating Memory-Enhanced Agent[/bold]")
            if not self.create_agent_with_memory(memory_hooks):
                return False
            
            # Step 6: Test
            console.print("\n[bold]Step 6: Testing Personalization[/bold]")
            if not self.test_personalization():
                return False
            
            console.print("\n[bold green]Lab 2 completed successfully! ✓[/bold green]\n")
            console.print("[cyan]What we built:[/cyan]")
            console.print("  ✓ AgentCore Memory with 2 strategies")
            console.print("  ✓ Seeded customer history")
            console.print("  ✓ Memory hooks for automatic context")
            console.print("  ✓ Personalized agent responses")
            
            # Save memory ID for next labs
            import json
            config = {"memory_id": self.memory_id}
            with open("lab_config.json", "w") as f:
                json.dump(config, f)
            
            return True
            
        except Exception as e:
            console.print(f"\n[red]Lab 2 failed: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return False


if __name__ == "__main__":
    lab2 = Lab2Implementation(interactive=True)
    success = lab2.run()
    exit(0 if success else 1)