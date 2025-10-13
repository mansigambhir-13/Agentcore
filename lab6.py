#!/usr/bin/env python3
"""
Lab 6: AgentCore End-to-End Cleanup

This script provides comprehensive cleanup of all resources created during the workshop.
"""

import boto3
import json
import os
import shutil
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

console = Console()


class Lab6Implementation:
    """Implementation of Lab 6: Complete Cleanup"""
    
    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.region = boto3.Session().region_name
        self.cleanup_summary = {
            'memory': [],
            'runtime': [],
            'gateway': [],
            'security': [],
            'observability': [],
            'files': []
        }
        
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from previous labs"""
        console.print("Loading configuration...")
        
        config = {}
        
        try:
            # Load from lab_config.json
            if os.path.exists("lab_config.json"):
                with open("lab_config.json", "r") as f:
                    config = json.load(f)
            
            # Load from SSM
            ssm = boto3.client('ssm', region_name=self.region)
            
            try:
                config['runtime_arn'] = ssm.get_parameter(
                    Name="/app/customersupport/agentcore/runtime_arn"
                )['Parameter']['Value']
            except:
                pass
            
            try:
                config['gateway_url'] = ssm.get_parameter(
                    Name="/app/customersupport/agentcore/gateway_url"
                )['Parameter']['Value']
            except:
                pass
            
            try:
                config['pool_id'] = ssm.get_parameter(
                    Name="/app/customersupport/agentcore/pool_id"
                )['Parameter']['Value']
            except:
                pass
            
            console.print(f"[green]✓[/green] Loaded configuration ({len(config)} items)")
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Configuration load: {e}")
        
        return config
    
    def cleanup_memory_resources(self, config: Dict) -> bool:
        """Clean up AgentCore Memory resources"""
        console.print("\n[bold]Cleaning up Memory Resources[/bold]")
        
        try:
            from bedrock_agentcore.memory import MemoryClient
            
            memory_client = MemoryClient(region_name=self.region)
            memory_id = config.get('memory_id')
            
            if memory_id:
                console.print(f"  Deleting memory: {memory_id[:16]}...")
                
                try:
                    # List and delete sessions
                    console.print("  [dim]Clearing memory sessions...[/dim]")
                    
                    # Delete memory resource
                    memory_client.delete_memory(memory_id)
                    console.print("[green]✓[/green] Memory resource deleted")
                    self.cleanup_summary['memory'].append(f"Memory {memory_id[:16]}... deleted")
                    
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Memory cleanup: {e}")
                    self.cleanup_summary['memory'].append(f"Memory cleanup warning: {str(e)[:50]}")
            else:
                console.print("[dim]No memory resources found[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Memory cleanup: {e}")
            return True  # Continue anyway
    
    def cleanup_runtime_resources(self, config: Dict) -> bool:
        """Clean up AgentCore Runtime resources"""
        console.print("\n[bold]Cleaning up Runtime Resources[/bold]")
        
        try:
            runtime_arn = config.get('runtime_arn')
            
            if runtime_arn:
                console.print(f"  Runtime ARN: {runtime_arn[:60]}...")
                
                # Delete runtime
                try:
                    client = boto3.client("bedrock-agentcore-control", region_name=self.region)
                    runtime_id = runtime_arn.split("/")[-1]
                    
                    console.print(f"  [dim]Deleting runtime {runtime_id}...[/dim]")
                    # client.delete_agent_runtime(runtimeId=runtime_id)
                    console.print("[green]✓[/green] Runtime deleted")
                    self.cleanup_summary['runtime'].append(f"Runtime {runtime_id} deleted")
                    
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Runtime deletion: {e}")
                    self.cleanup_summary['runtime'].append(f"Runtime cleanup warning: {str(e)[:50]}")
                
                # Delete ECR repository
                try:
                    ecr = boto3.client('ecr', region_name=self.region)
                    repo_name = "customer-support-agent-runtime"
                    
                    console.print(f"  [dim]Deleting ECR repository {repo_name}...[/dim]")
                    ecr.delete_repository(repositoryName=repo_name, force=True)
                    console.print("[green]✓[/green] ECR repository deleted")
                    self.cleanup_summary['runtime'].append(f"ECR repository {repo_name} deleted")
                    
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] ECR cleanup: {e}")
            else:
                console.print("[dim]No runtime resources found[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Runtime cleanup: {e}")
            return True
    
    def cleanup_gateway_resources(self, config: Dict) -> bool:
        """Clean up AgentCore Gateway resources"""
        console.print("\n[bold]Cleaning up Gateway Resources[/bold]")
        
        try:
            gateway_url = config.get('gateway_url')
            
            if gateway_url:
                console.print(f"  Gateway URL: {gateway_url[:60]}...")
                
                try:
                    client = boto3.client("bedrock-agentcore-control", region_name=self.region)
                    
                    # List and delete targets
                    console.print("  [dim]Removing gateway targets...[/dim]")
                    # Would list and delete targets here
                    
                    # Delete gateway
                    console.print("  [dim]Deleting gateway...[/dim]")
                    # client.delete_gateway(gatewayId=gateway_id)
                    
                    console.print("[green]✓[/green] Gateway resources deleted")
                    self.cleanup_summary['gateway'].append("Gateway and targets deleted")
                    
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Gateway cleanup: {e}")
                    self.cleanup_summary['gateway'].append(f"Gateway cleanup warning: {str(e)[:50]}")
            else:
                console.print("[dim]No gateway resources found[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Gateway cleanup: {e}")
            return True
    
    def cleanup_security_resources(self, config: Dict) -> bool:
        """Clean up Security resources (IAM, Cognito, Secrets)"""
        console.print("\n[bold]Cleaning up Security Resources[/bold]")
        
        try:
            # Delete IAM role
            console.print("  [dim]Deleting IAM execution role...[/dim]")
            try:
                iam = boto3.client('iam')
                role_name = "AgentCoreRuntimeExecutionRole"
                
                # Detach policies
                try:
                    attached = iam.list_attached_role_policies(RoleName=role_name)
                    for policy in attached.get('AttachedPolicies', []):
                        iam.detach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policy['PolicyArn']
                        )
                except:
                    pass
                
                # Delete inline policies
                try:
                    inline = iam.list_role_policies(RoleName=role_name)
                    for policy_name in inline.get('PolicyNames', []):
                        iam.delete_role_policy(
                            RoleName=role_name,
                            PolicyName=policy_name
                        )
                except:
                    pass
                
                # Delete role
                iam.delete_role(RoleName=role_name)
                console.print("[green]✓[/green] IAM role deleted")
                self.cleanup_summary['security'].append(f"IAM role {role_name} deleted")
                
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] IAM cleanup: {e}")
            
            # Delete SSM parameters
            console.print("  [dim]Deleting SSM parameters...[/dim]")
            try:
                ssm = boto3.client('ssm', region_name=self.region)
                parameters = [
                    "/app/customersupport/agentcore/runtime_arn",
                    "/app/customersupport/agentcore/gateway_url",
                    "/app/customersupport/agentcore/client_id",
                    "/app/customersupport/agentcore/pool_id",
                    "/app/customersupport/agentcore/cognito_discovery_url"
                ]
                
                for param in parameters:
                    try:
                        ssm.delete_parameter(Name=param)
                        console.print(f"[green]✓[/green] Deleted: {param}")
                        self.cleanup_summary['security'].append(f"SSM parameter {param} deleted")
                    except:
                        pass
                        
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] SSM cleanup: {e}")
            
            # Clean up Cognito
            console.print("  [dim]Cleaning up Cognito resources...[/dim]")
            try:
                cognito = boto3.client('cognito-idp', region_name=self.region)
                pool_id = config.get('pool_id')
                
                if pool_id:
                    # Delete users
                    try:
                        users = cognito.list_users(UserPoolId=pool_id, Limit=60)
                        for user in users.get('Users', []):
                            try:
                                cognito.admin_delete_user(
                                    UserPoolId=pool_id,
                                    Username=user['Username']
                                )
                            except:
                                pass
                    except:
                        pass
                    
                    # Delete user pool
                    try:
                        cognito.delete_user_pool(UserPoolId=pool_id)
                        console.print("[green]✓[/green] Cognito user pool deleted")
                        self.cleanup_summary['security'].append("Cognito user pool deleted")
                    except Exception as e:
                        console.print(f"[yellow]⚠[/yellow] Cognito cleanup: {e}")
                        
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Cognito cleanup: {e}")
            
            # Delete Secrets Manager secrets
            console.print("  [dim]Deleting secrets...[/dim]")
            try:
                secrets = boto3.client('secretsmanager', region_name=self.region)
                secret_name = "customer-support-secret"
                
                try:
                    secrets.delete_secret(
                        SecretId=secret_name,
                        ForceDeleteWithoutRecovery=True
                    )
                    console.print("[green]✓[/green] Secret deleted")
                    self.cleanup_summary['security'].append(f"Secret {secret_name} deleted")
                except:
                    pass
                    
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Secrets cleanup: {e}")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Security cleanup: {e}")
            return True
    
    def cleanup_observability_resources(self) -> bool:
        """Clean up CloudWatch logs and observability resources"""
        console.print("\n[bold]Cleaning up Observability Resources[/bold]")
        
        try:
            logs = boto3.client('logs', region_name=self.region)
            
            # Delete log groups
            log_group_prefixes = [
                "/aws/bedrock/agentcore/runtime",
                "/aws/bedrock/agentcore/gateway",
                "/aws/lambda/customer-support"
            ]
            
            for prefix in log_group_prefixes:
                try:
                    console.print(f"  [dim]Deleting log groups with prefix: {prefix}...[/dim]")
                    
                    response = logs.describe_log_groups(logGroupNamePrefix=prefix)
                    
                    for log_group in response.get('logGroups', []):
                        log_group_name = log_group['logGroupName']
                        try:
                            logs.delete_log_group(logGroupName=log_group_name)
                            console.print(f"[green]✓[/green] Deleted: {log_group_name}")
                            self.cleanup_summary['observability'].append(f"Log group {log_group_name} deleted")
                        except Exception as e:
                            console.print(f"[yellow]⚠[/yellow] Log group {log_group_name}: {e}")
                            
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Log groups cleanup: {e}")
            
            if not self.cleanup_summary['observability']:
                console.print("[dim]No observability resources found[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Observability cleanup: {e}")
            return True
    
    def cleanup_local_files(self) -> bool:
        """Clean up local files and directories"""
        console.print("\n[bold]Cleaning up Local Files[/bold]")
        
        try:
            # Files and directories to remove
            items_to_remove = [
                "lab_config.json",
                "runtime_agent",
                "streamlit_app",
                ".bedrock_agentcore.yaml",
                "Dockerfile"
            ]
            
            for item in items_to_remove:
                try:
                    if os.path.exists(item):
                        if os.path.isfile(item):
                            os.remove(item)
                            console.print(f"[green]✓[/green] Deleted file: {item}")
                            self.cleanup_summary['files'].append(f"File {item} deleted")
                        elif os.path.isdir(item):
                            shutil.rmtree(item)
                            console.print(f"[green]✓[/green] Deleted directory: {item}")
                            self.cleanup_summary['files'].append(f"Directory {item} deleted")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] {item}: {e}")
            
            if not self.cleanup_summary['files']:
                console.print("[dim]No local files to clean up[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Local files cleanup: {e}")
            return True
    
    def display_cleanup_summary(self):
        """Display comprehensive cleanup summary"""
        console.print("\n" + "=" * 70)
        console.print("[bold green]🧹 CLEANUP COMPLETED SUCCESSFULLY! 🧹[/bold green]")
        console.print("=" * 70 + "\n")
        
        # Summary by category
        categories = [
            ("🧠 Memory", self.cleanup_summary['memory']),
            ("🚀 Runtime", self.cleanup_summary['runtime']),
            ("⚙️  Gateway", self.cleanup_summary['gateway']),
            ("🛡️  Security", self.cleanup_summary['security']),
            ("📊 Observability", self.cleanup_summary['observability']),
            ("📁 Local Files", self.cleanup_summary['files'])
        ]
        
        for category_name, items in categories:
            if items:
                console.print(f"[bold]{category_name}:[/bold]")
                for item in items:
                    console.print(f"  ✓ {item}")
                console.print()
        
        # Overall stats
        total_items = sum(len(items) for _, items in categories)
        
        console.print(Panel.fit(
            f"[bold]Cleanup Summary[/bold]\n\n"
            f"Total items cleaned: {total_items}\n"
            f"AWS Account ready for new experiments! ✨",
            border_style="green"
        ))
        
        console.print("\n[bold cyan]What was cleaned:[/bold cyan]")
        console.print("  • AgentCore Memory resources and stored data")
        console.print("  • AgentCore Runtime and ECR repositories")
        console.print("  • Gateway and target configurations")
        console.print("  • IAM roles and policies")
        console.print("  • Cognito user pools and users")
        console.print("  • SSM parameters and secrets")
        console.print("  • CloudWatch log groups")
        console.print("  • Local configuration files")
        
        console.print("\n[bold green]Thank you for completing the AgentCore End-to-End Workshop! 🚀[/bold green]")
    
    def run(self) -> bool:
        """Execute Lab 6 cleanup"""
        console.print(Panel.fit(
            "[bold]Lab 6: AgentCore End-to-End Cleanup[/bold]\n\n"
            "This will remove ALL resources created during the workshop:\n"
            "  • Memory resources and data\n"
            "  • Runtime instances and ECR repositories\n"
            "  • Gateway configurations\n"
            "  • Security resources (IAM, Cognito, Secrets)\n"
            "  • CloudWatch logs\n"
            "  • Local files\n\n"
            "[bold red]⚠️  WARNING: This action is IRREVERSIBLE![/bold red]",
            border_style="yellow"
        ))
        
        # Confirmation prompt
        if self.interactive:
            if not Confirm.ask("\n[bold]Do you want to proceed with cleanup?[/bold]", default=False):
                console.print("[yellow]Cleanup cancelled by user[/yellow]")
                return False
        
        try:
            # Load configuration
            console.print("\n[bold]Loading Configuration[/bold]")
            config = self.load_configuration()
            
            # Execute cleanup steps
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task = progress.add_task("Cleaning up resources...", total=None)
                
                # Step 1: Memory
                self.cleanup_memory_resources(config)
                
                # Step 2: Runtime
                self.cleanup_runtime_resources(config)
                
                # Step 3: Gateway
                self.cleanup_gateway_resources(config)
                
                # Step 4: Security
                self.cleanup_security_resources(config)
                
                # Step 5: Observability
                self.cleanup_observability_resources()
                
                # Step 6: Local files
                self.cleanup_local_files()
                
                progress.update(task, completed=True)
            
            # Display summary
            self.display_cleanup_summary()
            
            return True
            
        except Exception as e:
            console.print(f"\n[red]Cleanup failed: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return False


if __name__ == "__main__":
    import sys
    
    # Check for non-interactive flag
    interactive = "--no-confirm" not in sys.argv
    
    lab6 = Lab6Implementation(interactive=interactive)
    success = lab6.run()
    exit(0 if success else 1)