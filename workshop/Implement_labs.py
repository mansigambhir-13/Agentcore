#!/usr/bin/env python3
"""
Amazon Bedrock AgentCore - Complete Lab Implementation Script

This script orchestrates the execution of all 5 labs, providing a complete
implementation of the AgentCore workshop from prototype to production.

Usage:
    python implement_labs.py --all                    # Run all labs sequentially
    python implement_labs.py --lab 1                  # Run specific lab
    python implement_labs.py --lab 1 --interactive    # Interactive mode with prompts
    python implement_labs.py --cleanup                # Run cleanup (Lab 6)

Author: AWS AgentCore Team
Version: 1.0
"""

import argparse
import sys
import os
import time
from pathlib import Path
from typing import Optional

# Add lab implementations to path
sys.path.insert(0, str(Path(__file__).parent / "lab_implementations"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


class LabOrchestrator:
    """Orchestrates the execution of all workshop labs"""
    
    def __init__(self, interactive: bool = False):
        self.interactive = interactive
        self.lab_results = {}
        
    def show_welcome(self):
        """Display welcome message"""
        console.print(Panel.fit(
            "[bold cyan]Amazon Bedrock AgentCore Workshop[/bold cyan]\n"
            "[yellow]Complete Lab Implementation[/yellow]\n\n"
            "This script will guide you through:\n"
            "  🏗️  Lab 1: Agent Prototype\n"
            "  🧠 Lab 2: Memory & Personalization\n"
            "  🌐 Lab 3: Gateway & Shared Tools\n"
            "  🚀 Lab 4: Production Runtime\n"
            "  🖥️  Lab 5: Customer Frontend\n"
            "  🧹 Lab 6: Complete Cleanup\n\n"
            "[dim]Estimated completion time: 4-5 hours[/dim]",
            title="🎯 Workshop Implementation",
            border_style="cyan"
        ))
        
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        console.print("\n[bold yellow]Checking Prerequisites...[/bold yellow]\n")
        
        checks = {
            "Python 3.10+": self._check_python_version(),
            "AWS Credentials": self._check_aws_credentials(),
            "Required Packages": self._check_packages(),
            "Docker/Finch": self._check_docker(),
        }
        
        table = Table(title="Prerequisites Check")
        table.add_column("Requirement", style="cyan")
        table.add_column("Status", style="white")
        
        all_passed = True
        for requirement, passed in checks.items():
            status = "[green]✓ Passed[/green]" if passed else "[red]✗ Failed[/red]"
            table.add_row(requirement, status)
            if not passed:
                all_passed = False
        
        console.print(table)
        
        if not all_passed:
            console.print("\n[red]Some prerequisites are not met. Please fix them before continuing.[/red]")
            if self.interactive:
                if not Confirm.ask("Do you want to continue anyway?"):
                    return False
        
        return True
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        import sys
        return sys.version_info >= (3, 10)
    
    def _check_aws_credentials(self) -> bool:
        """Check AWS credentials"""
        try:
            import boto3
            sts = boto3.client('sts')
            sts.get_caller_identity()
            return True
        except Exception:
            return False
    
    def _check_packages(self) -> bool:
        """Check required packages"""
        required = ['boto3', 'strands', 'bedrock_agentcore']
        try:
            for package in required:
                __import__(package.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def _check_docker(self) -> bool:
        """Check Docker/Finch availability"""
        import subprocess
        try:
            # Try Docker first
            result = subprocess.run(
                ['docker', 'ps'], 
                capture_output=True, 
                timeout=5
            )
            if result.returncode == 0:
                return True
            
            # Try Finch
            result = subprocess.run(
                ['finch', 'ps'], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def run_lab_1(self) -> bool:
        """Execute Lab 1: Agent Prototype"""
        console.print("\n[bold cyan]═══ Lab 1: Creating Agent Prototype ═══[/bold cyan]\n")
        
        try:
            from lab1_implementation import Lab1Implementation
            
            lab1 = Lab1Implementation(interactive=self.interactive)
            success = lab1.run()
            
            self.lab_results['lab1'] = {
                'success': success,
                'agent': lab1.agent if success else None
            }
            
            if success:
                console.print("[green]✓ Lab 1 completed successfully![/green]")
            else:
                console.print("[red]✗ Lab 1 failed. Check errors above.[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in Lab 1: {e}[/red]")
            return False
    
    def run_lab_2(self) -> bool:
        """Execute Lab 2: Memory"""
        console.print("\n[bold cyan]═══ Lab 2: Adding Memory & Personalization ═══[/bold cyan]\n")
        
        try:
            from lab2_implementation import Lab2Implementation
            
            lab2 = Lab2Implementation(interactive=self.interactive)
            success = lab2.run()
            
            self.lab_results['lab2'] = {
                'success': success,
                'memory_id': lab2.memory_id if success else None,
                'agent': lab2.agent if success else None
            }
            
            if success:
                console.print("[green]✓ Lab 2 completed successfully![/green]")
            else:
                console.print("[red]✗ Lab 2 failed. Check errors above.[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in Lab 2: {e}[/red]")
            return False
    
    def run_lab_3(self) -> bool:
        """Execute Lab 3: Gateway"""
        console.print("\n[bold cyan]═══ Lab 3: Gateway & Shared Tools ═══[/bold cyan]\n")
        
        try:
            from lab3_implementation import Lab3Implementation
            
            lab3 = Lab3Implementation(
                interactive=self.interactive,
                memory_id=self.lab_results.get('lab2', {}).get('memory_id')
            )
            success = lab3.run()
            
            self.lab_results['lab3'] = {
                'success': success,
                'gateway_id': lab3.gateway_id if success else None,
                'gateway_url': lab3.gateway_url if success else None,
                'agent': lab3.agent if success else None
            }
            
            if success:
                console.print("[green]✓ Lab 3 completed successfully![/green]")
            else:
                console.print("[red]✗ Lab 3 failed. Check errors above.[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in Lab 3: {e}[/red]")
            return False
    
    def run_lab_4(self) -> bool:
        """Execute Lab 4: Runtime"""
        console.print("\n[bold cyan]═══ Lab 4: Production Runtime Deployment ═══[/bold cyan]\n")
        
        try:
            from lab4_implementation import Lab4Implementation
            
            lab4 = Lab4Implementation(
                interactive=self.interactive,
                gateway_id=self.lab_results.get('lab3', {}).get('gateway_id')
            )
            success = lab4.run()
            
            self.lab_results['lab4'] = {
                'success': success,
                'runtime_arn': lab4.runtime_arn if success else None,
                'runtime': lab4.runtime if success else None
            }
            
            if success:
                console.print("[green]✓ Lab 4 completed successfully![/green]")
            else:
                console.print("[red]✗ Lab 4 failed. Check errors above.[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in Lab 4: {e}[/red]")
            return False
    
    def run_lab_5(self) -> bool:
        """Execute Lab 5: Frontend"""
        console.print("\n[bold cyan]═══ Lab 5: Customer-Facing Frontend ═══[/bold cyan]\n")
        
        try:
            from lab5_implementation import Lab5Implementation
            
            lab5 = Lab5Implementation(
                interactive=self.interactive,
                runtime_arn=self.lab_results.get('lab4', {}).get('runtime_arn')
            )
            success = lab5.run()
            
            self.lab_results['lab5'] = {
                'success': success,
                'streamlit_url': lab5.streamlit_url if success else None
            }
            
            if success:
                console.print("[green]✓ Lab 5 completed successfully![/green]")
            else:
                console.print("[red]✗ Lab 5 failed. Check errors above.[/red]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in Lab 5: {e}[/red]")
            return False
    
    def run_cleanup(self) -> bool:
        """Execute Lab 6: Cleanup"""
        console.print("\n[bold cyan]═══ Lab 6: Complete Cleanup ═══[/bold cyan]\n")
        
        if self.interactive:
            console.print("[yellow]⚠️  This will delete all resources created during the workshop.[/yellow]")
            if not Confirm.ask("Are you sure you want to continue?"):
                console.print("[yellow]Cleanup cancelled.[/yellow]")
                return False
        
        try:
            from lab6_cleanup import Lab6Cleanup
            
            cleanup = Lab6Cleanup(interactive=self.interactive)
            success = cleanup.run()
            
            if success:
                console.print("[green]✓ Cleanup completed successfully![/green]")
            else:
                console.print("[yellow]⚠️  Cleanup completed with some warnings.[/yellow]")
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error in cleanup: {e}[/red]")
            return False
    
    def run_all_labs(self):
        """Run all labs sequentially"""
        self.show_welcome()
        
        if not self.check_prerequisites():
            console.print("[red]Prerequisites check failed. Exiting.[/red]")
            return
        
        if self.interactive:
            if not Confirm.ask("\nReady to start Lab 1?"):
                console.print("Exiting.")
                return
        
        labs = [
            ("Lab 1: Agent Prototype", self.run_lab_1),
            ("Lab 2: Memory", self.run_lab_2),
            ("Lab 3: Gateway", self.run_lab_3),
            ("Lab 4: Runtime", self.run_lab_4),
            ("Lab 5: Frontend", self.run_lab_5),
        ]
        
        for lab_name, lab_func in labs:
            console.print(f"\n[bold]Starting {lab_name}...[/bold]")
            
            success = lab_func()
            
            if not success:
                console.print(f"\n[red]{lab_name} failed.[/red]")
                if self.interactive:
                    if not Confirm.ask("Continue to next lab anyway?"):
                        break
                else:
                    console.print("[red]Stopping execution due to failure.[/red]")
                    break
            
            if self.interactive and lab_name != labs[-1][0]:
                if not Confirm.ask(f"\n{lab_name} complete. Continue to next lab?"):
                    break
            
            time.sleep(2)  # Brief pause between labs
        
        # Show summary
        self.show_summary()
    
    def show_summary(self):
        """Display execution summary"""
        console.print("\n[bold cyan]═══ Workshop Summary ═══[/bold cyan]\n")
        
        table = Table(title="Lab Results")
        table.add_column("Lab", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Key Outputs", style="yellow")
        
        lab_info = {
            'lab1': ('Lab 1: Agent Prototype', 'agent'),
            'lab2': ('Lab 2: Memory', 'memory_id'),
            'lab3': ('Lab 3: Gateway', 'gateway_url'),
            'lab4': ('Lab 4: Runtime', 'runtime_arn'),
            'lab5': ('Lab 5: Frontend', 'streamlit_url'),
        }
        
        for lab_key, (lab_name, output_key) in lab_info.items():
            if lab_key in self.lab_results:
                result = self.lab_results[lab_key]
                status = "[green]✓ Success[/green]" if result['success'] else "[red]✗ Failed[/red]"
                output = str(result.get(output_key, 'N/A'))[:50] if result['success'] else 'N/A'
                table.add_row(lab_name, status, output)
        
        console.print(table)
        
        # Show next steps
        all_success = all(r.get('success', False) for r in self.lab_results.values())
        
        if all_success:
            console.print("\n[bold green]🎉 All labs completed successfully![/bold green]\n")
            console.print("[cyan]Next Steps:[/cyan]")
            console.print("  1. Test your deployed agent")
            console.print("  2. Explore CloudWatch observability")
            console.print("  3. Customize for your use case")
            console.print("  4. When done, run: python implement_labs.py --cleanup")
        else:
            console.print("\n[yellow]⚠️  Some labs did not complete successfully.[/yellow]")
            console.print("Review the errors above and refer to TROUBLESHOOTING_GUIDE.md")


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Bedrock AgentCore Lab Implementation"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all labs sequentially'
    )
    parser.add_argument(
        '--lab',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help='Run specific lab'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Run cleanup (Lab 6)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode with prompts'
    )
    
    args = parser.parse_args()
    
    orchestrator = LabOrchestrator(interactive=args.interactive)
    
    try:
        if args.cleanup:
            orchestrator.run_cleanup()
        elif args.all:
            orchestrator.run_all_labs()
        elif args.lab:
            if args.lab == 1:
                orchestrator.run_lab_1()
            elif args.lab == 2:
                orchestrator.run_lab_2()
            elif args.lab == 3:
                orchestrator.run_lab_3()
            elif args.lab == 4:
                orchestrator.run_lab_4()
            elif args.lab == 5:
                orchestrator.run_lab_5()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()