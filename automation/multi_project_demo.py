#!/usr/bin/env python3
"""
EAIO Multi-Project Demo
Demonstrates switching between different Jira projects
"""

import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from eaio_jira_automation import EAIOJiraAutomation

# Load environment variables
load_dotenv()

console = Console()

async def demo_multi_project():
    """Demo multi-project functionality"""
    console.print("🏢 [bold blue]EAIO Multi-Project Demo[/bold blue]")
    console.print("=" * 60)
    
    # Get credentials
    jira_url = os.getenv('ATLASSIAN_URL', 'https://fistdat.atlassian.net')
    email = os.getenv('ATLASSIAN_EMAIL', 'fistdat@gmail.com')
    api_token = os.getenv('ATLASSIAN_API_TOKEN')
    
    if not api_token:
        console.print("❌ Missing ATLASSIAN_API_TOKEN environment variable")
        return
    
    console.print(f"🔧 Configuration:")
    console.print(f"   Jira URL: {jira_url}")
    console.print(f"   Email: {email}")
    
    # Initialize with default project (SCRUM)
    automation = EAIOJiraAutomation(
        jira_url=jira_url,
        email=email,
        api_token=api_token,
        project_key="SCRUM"
    )
    
    # Test connection
    console.print("\n🔍 Testing Jira connection...")
    if not automation.jira_client.test_connection():
        console.print("❌ Failed to connect to Jira")
        return
    
    console.print("✅ Connected successfully")
    
    # Show available projects
    console.print("\n📋 Available Projects:")
    projects = automation.get_available_projects()
    
    project_table = Table()
    project_table.add_column("Key", style="cyan")
    project_table.add_column("Name", style="green")
    project_table.add_column("Description", style="yellow")
    project_table.add_column("Board URL", style="blue")
    
    for key, config in projects.items():
        board_url = f"{config.base_url}/jira/software/projects/{key}/boards/{config.board_id}" if config.board_id else "N/A"
        project_table.add_row(key, config.name, config.description, board_url)
    
    console.print(project_table)
    
    # Test access to each project
    console.print("\n🔍 Testing project access...")
    for project_key in projects.keys():
        console.print(f"\n📌 Testing {project_key}:")
        automation.test_project_access(project_key)
    
    # Interactive project switching
    while True:
        current_project = automation.jira_client.project_key
        console.print(f"\n📌 Current project: [bold green]{current_project}[/bold green]")
        
        if not Confirm.ask("Switch to different project?", default=False):
            break
        
        project_choices = list(projects.keys())
        selected_project = Prompt.ask(
            "Select project",
            choices=project_choices,
            default=current_project
        )
        
        if selected_project != current_project:
            console.print(f"\n🔄 Switching from {current_project} to {selected_project}...")
            if automation.switch_project(selected_project):
                console.print("✅ Successfully switched!")
                
                # Show Sprint 0 tasks would be created in this project
                console.print(f"\n📝 Sprint 0 tasks would be created in:")
                console.print(f"   Project: {projects[selected_project].name}")
                console.print(f"   URL: {jira_url}/jira/software/projects/{selected_project}/boards/{projects[selected_project].board_id}")
            else:
                console.print("❌ Failed to switch project")
    
    console.print("\n🎉 Multi-project demo completed!")
    console.print("\n💡 Usage:")
    console.print("   1. Set ATLASSIAN_API_TOKEN in your environment")
    console.print("   2. Run: python3 run_automation.py")
    console.print("   3. Select target project when prompted")
    console.print("   4. Choose sprints to create")

if __name__ == "__main__":
    asyncio.run(demo_multi_project()) 