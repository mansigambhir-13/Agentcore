#!/usr/bin/env python3
"""
AgentCore End-to-End Workshop Runner

This script runs all labs in sequence to demonstrate the complete AgentCore journey.
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

# Import lab implementations
from lab1 import Lab1Implementation
from lab2 import Lab2Implementation
from lab4 import Lab4Implementation
from lab5 import Lab5Implementation
from lab6 import Lab6Implementation

console = Console()


class WorkshopRunner:
    """Main workshop runner"""
    
    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.labs_completed = []
        self.labs_failed = []
        
    def run_lab(self, lab_num: int, lab_name: str, lab_implementation) -> bool:
        """Run a single lab"""
        console.print("\n" + "=" * 70)
        console.print(f"[bold cyan]Starting Lab {lab_num}: {lab_name}[/bold cyan]")
        console.print("=" * 70 + "\n")
        
        try:
            success = lab_implementation.run()
            
            if success:
                self.labs_completed.append(f"Lab {lab_num}: {lab_name}")
                console.print(f"\n[bold green]✓ Lab {lab_num} completed successfully![/bold green]\n")
                
                if self.interactive and lab_num < 5:
                    if not Confirm.ask(f"[bold]Continue to Lab {lab_num + 1}?[/bold]", default=True):
                        console.print("[yellow]Workshop paused by user[/yellow]")
                        return False
            else:
                self.labs_failed.append(f"Lab {lab_num}: {lab_name}")
                console.print(f"\n[bold red]✗ Lab {lab_num} failed[/bold red]\n")
                
                if self.interactive:
                    if not Confirm.ask("[bold]Continue despite failure?[/bold]", default=False):
                        return False
            
            return success
            
        except Exception as e:
            console.print(f"\n[red]Lab {lab_num} error: {e}[/red]")
            self.labs_failed.append(f"Lab {lab_num}: {lab_name}")
            return False
    
    def display_workshop_intro(self):
        """Display workshop introduction"""
        console.print(Panel.fit(
            "[bold]Amazon Bedrock AgentCore End-to-End Workshop[/bold]\n\n"
            "This workshop demonstrates building a production-ready AI agent\n"
            "from prototype to customer-facing application.\n\n"
            "[cyan]Labs:[/cyan]\n"
            "  1. Create Agent Prototype\n"
            "  2. Add Memory & Personalization\n"
            "  3. Scale with Gateway & Identity (Lab 3 implementation available separately)\n"
            "  4. Deploy to Production Runtime\n"
            "  5. Build Customer-Facing Frontend\n"
            "  6. Complete Cleanup\n\n"
            "[bold]Duration:[/bold] ~30-45 minutes\n"
            "[bold]Prerequisites:[/bold] AWS credentials configured",
            border_style="cyan",
            title="🚀 Welcome"
        ))
    
    def display_final_summary(self):
        """Display final workshop summary"""
        console.print("\n" + "=" * 70)
        console.print("[bold]Workshop Complete![/bold]")
        console.print("=" * 70 + "\n")
        
        console.print("[bold green]✓ Completed Labs:[/bold green]")
        for lab in self.labs_completed:
            console.print(f"  • {lab}")
        
        if self.labs_failed:
            console.print("\n[bold yellow]⚠ Failed/Skipped Labs:[/bold yellow]")
            for lab in self.labs_failed:
                console.print(f"  • {lab}")
        
        console.print("\n[bold cyan]What You Built:[/bold cyan]")
        console.print("  ✓ AI-powered customer support agent")
        console.print("  ✓ Persistent memory with personalization")
        console.print("  ✓ Production-ready runtime deployment")
        console.print("  ✓ Customer-facing web application")
        console.print("  ✓ Complete end-to-end solution")
        
        console.print("\n[bold]Key Capabilities Demonstrated:[/bold]")
        console.print("  • Custom tool creation")
        console.print("  • Memory strategies (short-term & long-term)")
        console.print("  • Gateway for tool sharing")
        console.print("  • Secure authentication & authorization")
        console.print("  • Serverless runtime deployment")
        console.print("  • CloudWatch observability")
        console.print("  • Real-time streaming responses")
        
        console.print("\n[bold green]🎉 Congratulations on completing the AgentCore Workshop! 🎉[/bold green]")
    
    def run_all_labs(self) -> bool:
        """Run all workshop labs"""
        self.display_workshop_intro()
        
        if self.interactive:
            console.print()
            if not Confirm.ask("[bold]Ready to start the workshop?[/bold]", default=True):
                console.print("[yellow]Workshop cancelled[/yellow]")
                return False
        
        # Lab 1: Agent Prototype
        lab1 = Lab1Implementation(interactive=False)
        if not self.run_lab(1, "Create Agent Prototype", lab1):
            return False
        
        time.sleep(2)
        
        # Lab 2: Memory & Personalization
        lab2 = Lab2Implementation(interactive=False)
        if not self.run_lab(2, "Add Memory & Personalization", lab2):
            return False
        
        time.sleep(2)
        
        # Lab 3 is separate (Gateway implementation)
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]Lab 3: Scale with Gateway & Identity[/bold cyan]")
        console.print("=" * 70)
        console.print("[dim]Note: Lab 3 implementation available as separate module[/dim]")
        console.print("[dim]Run lab3_implementation.py for Gateway setup[/dim]\n")
        time.sleep(1)
        
        # Lab 4: Production Runtime
        lab4 = Lab4Implementation(interactive=False)
        if not self.run_lab(4, "Deploy to Production Runtime", lab4):
            return False
        
        time.sleep(2)
        
        # Lab 5: Frontend Application
        lab5 = Lab5Implementation(interactive=False)
        if not self.run_lab(5, "Build Customer-Facing Frontend", lab5):
            return False
        
        # Display summary
        self.display_final_summary()
        
        # Ask about cleanup
        if self.interactive:
            console.print("\n" + "-" * 70)
            if Confirm.ask("\n[bold]Run Lab 6 to clean up all resources?[/bold]", default=False):
                time.sleep(2)
                lab6 = Lab6Implementation(interactive=True)
                self.run_lab(6, "Complete Cleanup", lab6)
            else:
                console.print("\n[yellow]Cleanup skipped. Resources remain active.[/yellow]")
                console.print("[dim]Run 'python lab6_implementation.py' later to clean up[/dim]")
        
        return True
    
    def run_single_lab(self, lab_num: int) -> bool:
        """Run a single lab by number"""
        labs = {
            1: ("Create Agent Prototype", Lab1Implementation),
            2: ("Add Memory & Personalization", Lab2Implementation),
            4: ("Deploy to Production Runtime", Lab4Implementation),
            5: ("Build Customer-Facing Frontend", Lab5Implementation),
            6: ("Complete Cleanup", Lab6Implementation)
        }
        
        if lab_num not in labs:
            console.print(f"[red]Error: Lab {lab_num} not found[/red]")
            console.print("Available labs: 1, 2, 4, 5, 6")
            return False
        
        lab_name, lab_class = labs[lab_num]
        lab_impl = lab_class(interactive=True)
        
        return self.run_lab(lab_num, lab_name, lab_impl)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AgentCore End-to-End Workshop Runner"
    )
    parser.add_argument(
        '--lab',
        type=int,
        choices=[1, 2, 4, 5, 6],
        help='Run a specific lab (1, 2, 4, 5, or 6)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all labs in sequence'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run without prompts (auto-continue)'
    )
    
    args = parser.parse_args()
    
    interactive = not args.non_interactive
    runner = WorkshopRunner(interactive=interactive)
    
    try:
        if args.lab:
            # Run single lab
            success = runner.run_single_lab(args.lab)
        elif args.all or len(sys.argv) == 1:
            # Run all labs
            success = runner.run_all_labs()
        else:
            parser.print_help()
            return
        
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Workshop interrupted by user[/yellow]")
        exit(1)
    except Exception as e:
        console.print(f"\n[red]Workshop error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        exit(1)


if __name__ == "__main__":
    main()