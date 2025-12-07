#!/usr/bin/env python3
"""
EAIO Jira Automation Runner
Interactive script to run the automation with customization options
Supports multiple Jira projects
"""

import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from eaio_jira_automation import EAIOJiraAutomation

# Load environment variables
load_dotenv()

console = Console()

def display_sprint_preview(sprint, sprint_file):
    """Display a preview of sprint epics and tasks"""
    console.print(f"\n📋 [bold blue]Sprint {sprint.number}: {sprint.name}[/bold blue]")
    console.print(f"📁 File: {sprint_file}")
    console.print(f"🎯 Layer Focus: {sprint.layer_focus}")
    console.print(f"⏱️  Duration: {sprint.duration}")
    console.print(f"📊 Story Points: {sprint.story_points}")
    
    # Create epics table
    epics_table = Table(title="📁 Epics Overview")
    epics_table.add_column("Epic", style="cyan", no_wrap=True)
    epics_table.add_column("Goal", style="green")
    epics_table.add_column("Tasks", justify="center", style="magenta")
    
    for epic in sprint.epics:
        epics_table.add_row(epic.name, epic.goal[:60] + "..." if len(epic.goal) > 60 else epic.goal, str(len(epic.tasks)))
    
    console.print(epics_table)
    
    # Show task summary
    total_tasks = sum(len(epic.tasks) for epic in sprint.epics)
    console.print(f"\n📝 [bold]Total: {len(sprint.epics)} epics, {total_tasks} tasks[/bold]")

def customize_epic(epic, epic_index):
    """Allow user to customize an epic"""
    console.print(f"\n🔧 [bold yellow]Customizing Epic {epic_index + 1}: {epic.name}[/bold yellow]")
    
    # Ask if user wants to modify epic name
    if Confirm.ask(f"Modify epic name '{epic.name}'?", default=False):
        new_name = Prompt.ask("Enter new epic name", default=epic.name)
        epic.name = new_name
    
    # Ask if user wants to modify epic goal
    if Confirm.ask(f"Modify epic goal?", default=False):
        console.print(f"Current goal: [italic]{epic.goal}[/italic]")
        new_goal = Prompt.ask("Enter new epic goal", default=epic.goal)
        epic.goal = new_goal
    
    # Show tasks in this epic
    console.print(f"\n📝 [bold]Tasks in this epic ({len(epic.tasks)} total):[/bold]")
    for i, task in enumerate(epic.tasks):
        console.print(f"  {i+1}. {task.id} - {task.title}")
    
    # Ask about task management
    while True:
        action = Prompt.ask(
            "\nTask actions", 
            choices=["keep", "remove", "modify", "done"],
            default="done"
        )
        
        if action == "done":
            break
        elif action == "remove":
            if len(epic.tasks) > 0:
                task_num = IntPrompt.ask(
                    "Remove which task number?", 
                    choices=[str(i+1) for i in range(len(epic.tasks))]
                )
                removed_task = epic.tasks.pop(task_num - 1)
                console.print(f"✅ Removed: {removed_task.title}")
        elif action == "modify":
            if len(epic.tasks) > 0:
                task_num = IntPrompt.ask(
                    "Modify which task number?", 
                    choices=[str(i+1) for i in range(len(epic.tasks))]
                )
                task = epic.tasks[task_num - 1]
                
                if Confirm.ask(f"Modify task title '{task.title}'?", default=False):
                    new_title = Prompt.ask("Enter new task title", default=task.title)
                    task.title = new_title
                
                if Confirm.ask(f"Modify assignee '{task.assignee}'?", default=False):
                    new_assignee = Prompt.ask("Enter new assignee", default=task.assignee)
                    task.assignee = new_assignee
                
                if Confirm.ask(f"Modify story points '{task.story_points}'?", default=False):
                    new_points = IntPrompt.ask("Enter story points", default=task.story_points)
                    task.story_points = new_points
    
    return epic

def customize_sprint(sprint, sprint_file):
    """Allow user to customize sprint epics and tasks"""
    console.print(f"\n🎨 [bold green]Customizing Sprint {sprint.number}[/bold green]")
    
    # Option to modify sprint metadata
    if Confirm.ask("Modify sprint metadata?", default=False):
        if Confirm.ask(f"Modify sprint name '{sprint.name}'?", default=False):
            new_name = Prompt.ask("Enter new sprint name", default=sprint.name)
            sprint.name = new_name
        
        if Confirm.ask(f"Modify story points target '{sprint.story_points}'?", default=False):
            new_points = IntPrompt.ask("Enter story points target", default=sprint.story_points)
            sprint.story_points = new_points
    
    # Epic management
    console.print(f"\n📁 [bold]Epic Management ({len(sprint.epics)} epics)[/bold]")
    
    while True:
        action = Prompt.ask(
            "Epic actions",
            choices=["review", "customize", "remove", "reorder", "done"],
            default="review"
        )
        
        if action == "done":
            break
        elif action == "review":
            display_sprint_preview(sprint, sprint_file)
        elif action == "customize":
            if len(sprint.epics) > 0:
                epic_choices = [f"{i+1}" for i in range(len(sprint.epics))]
                epic_num = IntPrompt.ask(
                    "Customize which epic?",
                    choices=epic_choices + ["0"],  # 0 = all
                )
                
                if epic_num == 0:
                    for i, epic in enumerate(sprint.epics):
                        if Confirm.ask(f"Customize epic {i+1}: {epic.name}?", default=False):
                            sprint.epics[i] = customize_epic(epic, i)
                else:
                    sprint.epics[epic_num - 1] = customize_epic(sprint.epics[epic_num - 1], epic_num - 1)
        elif action == "remove":
            if len(sprint.epics) > 0:
                epic_choices = [f"{i+1}" for i in range(len(sprint.epics))]
                epic_num = IntPrompt.ask("Remove which epic?", choices=epic_choices)
                removed_epic = sprint.epics.pop(epic_num - 1)
                console.print(f"✅ Removed epic: {removed_epic.name}")
        elif action == "reorder":
            console.print("📝 Current epic order:")
            for i, epic in enumerate(sprint.epics):
                console.print(f"  {i+1}. {epic.name}")
            
            if Confirm.ask("Reorder epics?", default=False):
                console.print("💡 Enter new order as comma-separated numbers (e.g., 2,1,3)")
                current_order = ",".join([str(i+1) for i in range(len(sprint.epics))])
                new_order_str = Prompt.ask("New order", default=current_order)
                
                try:
                    new_order = [int(x.strip()) - 1 for x in new_order_str.split(",")]
                    if len(new_order) == len(sprint.epics) and all(0 <= i < len(sprint.epics) for i in new_order):
                        sprint.epics = [sprint.epics[i] for i in new_order]
                        console.print("✅ Epics reordered successfully")
                    else:
                        console.print("❌ Invalid order format")
                except ValueError:
                    console.print("❌ Invalid order format")
    
    return sprint

def interactive_sprint_selection(sprints_data):
    """Allow user to select which sprints to process"""
    console.print("\n🎯 [bold blue]Sprint Selection[/bold blue]")
    
    # Show all available sprints
    sprint_table = Table(title="📋 Available Sprints")
    sprint_table.add_column("Number", style="cyan", no_wrap=True)
    sprint_table.add_column("Sprint Name", style="green")
    sprint_table.add_column("Epics", justify="center", style="magenta")
    sprint_table.add_column("Tasks", justify="center", style="yellow")
    
    for sprint, sprint_file in sprints_data:
        total_tasks = sum(len(epic.tasks) for epic in sprint.epics)
        sprint_table.add_row(
            str(sprint.number),
            sprint.name,
            str(len(sprint.epics)),
            str(total_tasks)
        )
    
    console.print(sprint_table)
    
    # Ask user which sprints to process
    all_sprint_numbers = [str(sprint.number) for sprint, _ in sprints_data]
    
    process_all = Confirm.ask("Process all sprints?", default=True)
    
    if process_all:
        selected_sprints = list(range(len(sprints_data)))
    else:
        console.print("💡 Enter sprint numbers separated by commas (e.g., 1,3,5)")
        console.print(f"Available: {', '.join(all_sprint_numbers)}")
        selected_str = Prompt.ask("Select sprints", default=','.join(all_sprint_numbers))
        
        try:
            selected_numbers = [int(x.strip()) for x in selected_str.split(",")]
            selected_sprints = []
            for i, (sprint, _) in enumerate(sprints_data):
                if sprint.number in selected_numbers:
                    selected_sprints.append(i)
        except ValueError:
            console.print("❌ Invalid format, processing all sprints")
            selected_sprints = list(range(len(sprints_data)))
    
    return selected_sprints

def create_creation_summary(sprints_data, selected_indices):
    """Create a summary of what will be created"""
    console.print("\n📊 [bold green]Creation Summary[/bold green]")
    
    summary_table = Table(title="📋 Items to be Created in Jira")
    summary_table.add_column("Sprint", style="cyan")
    summary_table.add_column("Epics", justify="center", style="green")
    summary_table.add_column("Tasks", justify="center", style="yellow")
    summary_table.add_column("Story Points", justify="center", style="magenta")
    
    total_epics = 0
    total_tasks = 0
    total_points = 0
    
    for index in selected_indices:
        sprint, _ = sprints_data[index]
        epic_count = len(sprint.epics)
        task_count = sum(len(epic.tasks) for epic in sprint.epics)
        points_count = sum(sum(task.story_points for task in epic.tasks) for epic in sprint.epics)
        
        summary_table.add_row(
            f"Sprint {sprint.number}",
            str(epic_count),
            str(task_count), 
            str(points_count)
        )
        
        total_epics += epic_count
        total_tasks += task_count
        total_points += points_count
    
    summary_table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_epics}[/bold]",
        f"[bold]{total_tasks}[/bold]",
        f"[bold]{total_points}[/bold]"
    )
    
    console.print(summary_table)
    
    return {
        'total_epics': total_epics,
        'total_tasks': total_tasks,
        'total_points': total_points
    }

def validate_creation_results(automation: EAIOJiraAutomation) -> dict:
    """Validate the results of task and epic creation"""
    stats = automation.stats
    
    validation_results = {
        'total_sprints': stats['sprints_processed'],
        'total_epics_attempted': stats['epics_created'] + stats.get('epics_failed', 0),
        'total_tasks_attempted': stats['tasks_created'] + stats['tasks_failed'],
        'epics_success_rate': 0,
        'tasks_success_rate': 0,
        'status': 'UNKNOWN'
    }
    
    # Calculate success rates
    if validation_results['total_epics_attempted'] > 0:
        validation_results['epics_success_rate'] = (stats['epics_created'] / validation_results['total_epics_attempted']) * 100
    
    if validation_results['total_tasks_attempted'] > 0:
        validation_results['tasks_success_rate'] = (stats['tasks_created'] / validation_results['total_tasks_attempted']) * 100
    
    # Determine overall status
    if stats['tasks_created'] == 0:
        validation_results['status'] = 'FAILED'
    elif stats['tasks_failed'] == 0:
        validation_results['status'] = 'SUCCESS'
    elif validation_results['tasks_success_rate'] >= 80:
        validation_results['status'] = 'MOSTLY_SUCCESS'
    elif validation_results['tasks_success_rate'] >= 50:
        validation_results['status'] = 'PARTIAL_SUCCESS'
    else:
        validation_results['status'] = 'MOSTLY_FAILED'
    
    return validation_results

def create_validation_report(validation_results: dict, automation: EAIOJiraAutomation):
    """Create a detailed validation report"""
    stats = automation.stats
    
    # Status colors
    status_colors = {
        'SUCCESS': 'green',
        'MOSTLY_SUCCESS': 'yellow',
        'PARTIAL_SUCCESS': 'orange',
        'MOSTLY_FAILED': 'red',
        'FAILED': 'red'
    }
    
    # Create summary table
    table = Table(title="📊 EAIO Jira Automation Validation Report")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Status", justify="center")
    
    # Add rows
    table.add_row("Sprints Processed", str(validation_results['total_sprints']), "✅")
    table.add_row("Epics Created", f"{stats['epics_created']}/{validation_results['total_epics_attempted']}", 
                 f"{validation_results['epics_success_rate']:.1f}%")
    table.add_row("Tasks Created", f"{stats['tasks_created']}/{validation_results['total_tasks_attempted']}", 
                 f"{validation_results['tasks_success_rate']:.1f}%")
    table.add_row("Tasks Failed", str(stats['tasks_failed']), "❌" if stats['tasks_failed'] > 0 else "✅")
    table.add_row("Overall Status", validation_results['status'], 
                 f"[{status_colors[validation_results['status']]}]{validation_results['status']}[/]")
    
    console.print(table)
    
    # Create detailed analysis panel
    analysis_content = []
    
    if validation_results['status'] == 'SUCCESS':
        analysis_content.append("🎉 All tasks and epics created successfully!")
        analysis_content.append("✅ Ready to proceed with development work")
    elif validation_results['status'] == 'MOSTLY_SUCCESS':
        analysis_content.append("⚠️  Most tasks created successfully with minor issues")
        analysis_content.append("💡 Review failed items and retry if needed")
    elif validation_results['status'] == 'PARTIAL_SUCCESS':
        analysis_content.append("🔄 Partial success - significant issues detected")
        analysis_content.append("🔧 Check custom field configurations in Jira")
        analysis_content.append("📝 Consider manual creation for failed items")
    else:
        analysis_content.append("❌ Major issues detected in automation")
        analysis_content.append("🔍 Check Jira connection and permissions")
        analysis_content.append("⚙️  Review custom field mappings")
        analysis_content.append("📋 Manual task creation may be required")
    
    # Add specific recommendations
    if stats['tasks_failed'] > 10:
        analysis_content.append(f"\n🚨 High failure rate: {stats['tasks_failed']} tasks failed")
        analysis_content.append("💡 Consider reviewing custom field configuration")
    
    if stats['epics_created'] > 0 and stats['tasks_created'] == 0:
        analysis_content.append("\n⚠️  Epics created but no tasks - check task parsing logic")
    
    analysis_panel = Panel(
        "\n".join(analysis_content),
        title="📈 Analysis & Recommendations",
        border_style=status_colors[validation_results['status']]
    )
    
    console.print(analysis_panel)
    
    return validation_results

def display_project_selection(automation: EAIOJiraAutomation):
    """Display available projects and allow selection"""
    console.print("\n🏢 [bold blue]Project Selection[/bold blue]")
    
    available_projects = automation.get_available_projects()
    
    # Show project table
    project_table = Table(title="📋 Available Jira Projects")
    project_table.add_column("Key", style="cyan", no_wrap=True)
    project_table.add_column("Project Name", style="green")
    project_table.add_column("Description", style="yellow")
    project_table.add_column("Board ID", style="magenta")
    
    for key, config in available_projects.items():
        project_table.add_row(
            key,
            config.name,
            config.description,
            config.board_id or "N/A"
        )
    
    console.print(project_table)
    
    # Get current project
    current_project = automation.jira_client.project_key
    console.print(f"\n📌 Current project: [bold green]{current_project}[/bold green]")
    
    # Ask if user wants to change project
    if Confirm.ask("Change project?", default=False):
        project_choices = list(available_projects.keys())
        selected_project = Prompt.ask(
            "Select project",
            choices=project_choices,
            default=current_project
        )
        
        if selected_project != current_project:
            # Test access to selected project
            console.print(f"\n🔍 Testing access to project {selected_project}...")
            if automation.test_project_access(selected_project):
                if automation.switch_project(selected_project):
                    console.print(f"✅ Successfully switched to project: {selected_project}")
                    return selected_project
                else:
                    console.print(f"❌ Failed to switch to project: {selected_project}")
                    return current_project
            else:
                console.print(f"❌ No access to project {selected_project}. Staying with {current_project}")
                return current_project
    
    return current_project

async def main():
    """Main function to run EAIO Jira automation"""
    console.print("🎯 [bold blue]EAIO Interactive Jira Automation[/bold blue]")
    console.print("=" * 60)
    
    # Get credentials from environment
    jira_url = os.getenv('ATLASSIAN_URL')
    email = os.getenv('ATLASSIAN_EMAIL')
    api_token = os.getenv('ATLASSIAN_API_TOKEN')
    project_key = os.getenv('JIRA_PROJECT_KEY', 'SCRUM')
    sprints_dir = os.getenv('SPRINTS_DIRECTORY', '../.cursor/tasks/sprints')
    
    # Validate required environment variables
    if not all([jira_url, email, api_token]):
        console.print("❌ Missing required environment variables:", style="red")
        console.print("   - ATLASSIAN_URL")
        console.print("   - ATLASSIAN_EMAIL") 
        console.print("   - ATLASSIAN_API_TOKEN")
        console.print("\nPlease check your .env file")
        return 1
    
    console.print(f"🔧 Configuration:")
    console.print(f"   Jira URL: {jira_url}")
    console.print(f"   Email: {email}")
    console.print(f"   Project: {project_key}")
    console.print(f"   Sprints Dir: {sprints_dir}")
    
    # Initialize automation
    try:
        automation = EAIOJiraAutomation(
            jira_url=str(jira_url),
            email=str(email),
            api_token=str(api_token),
            project_key=project_key
        )
        
        # Test connection first
        console.print("\n🔍 Testing Jira connection...")
        if not automation.jira_client.test_connection():
            console.print("❌ Failed to connect to Jira. Check your credentials.", style="red")
            return 1
        
        console.print("✅ Jira connection successful", style="green")
        
        # Project selection
        selected_project = display_project_selection(automation)
        console.print(f"\n✅ Using project: [bold green]{selected_project}[/bold green]")
        
        # Parse all sprint files first
        console.print("\n📋 Parsing sprint files...")
        sprints_path = automation._get_sprints_path(sprints_dir)
        sprint_files = sorted([f for f in sprints_path.glob("sprint_*.md")])
        
        sprints_data = []
        for sprint_file in sprint_files:
            try:
                sprint = automation.parse_sprint_file(sprint_file)
                sprints_data.append((sprint, sprint_file.name))
                console.print(f"  ✅ Parsed: {sprint_file.name} ({len(sprint.epics)} epics)")
            except Exception as e:
                console.print(f"  ❌ Failed to parse {sprint_file.name}: {e}")
        
        if not sprints_data:
            console.print("❌ No valid sprint files found", style="red")
            return 1
        
        # Interactive sprint selection
        selected_indices = interactive_sprint_selection(sprints_data)
        
        # Ask if user wants to customize sprints
        if Confirm.ask("\n🎨 Customize sprints before creation?", default=False):
            for index in selected_indices:
                sprint, sprint_file = sprints_data[index]
                
                # Show sprint preview
                display_sprint_preview(sprint, sprint_file)
                
                # Ask if user wants to customize this sprint
                if Confirm.ask(f"\nCustomize Sprint {sprint.number}?", default=False):
                    sprints_data[index] = (customize_sprint(sprint, sprint_file), sprint_file)
        
        # Create creation summary
        summary = create_creation_summary(sprints_data, selected_indices)
        
        # Final confirmation
        if not Confirm.ask(f"\n🚀 Proceed with creating {summary['total_epics']} epics and {summary['total_tasks']} tasks?", default=True):
            console.print("❌ Automation cancelled by user")
            return 0
        
        # Run automation for selected sprints
        console.print("\n🚀 Starting automation...")
        for index in selected_indices:
            sprint, sprint_file = sprints_data[index]
            
            console.print(f"\n📋 Processing: Sprint {sprint.number}")
            
            # Process this sprint
            await automation.process_single_sprint(sprint)
            automation.stats['sprints_processed'] += 1
        
        # Validate results
        console.print("\n🔍 Validating creation results...")
        validation_results = validate_creation_results(automation)
        
        # Create detailed validation report
        console.print("\n" + "=" * 60)
        create_validation_report(validation_results, automation)
        
        # Create summary dashboard if tasks were created
        if automation.stats['tasks_created'] > 0:
            console.print("\n📊 Creating summary dashboard...")
            await automation.create_summary_dashboard()
        
        # Final status message
        console.print("\n" + "=" * 50)
        if validation_results['status'] in ['SUCCESS', 'MOSTLY_SUCCESS']:
            console.print("🎉 Automation completed successfully!", style="bold green")
            console.print("✅ Ready to start sprint work in Jira")
        else:
            console.print("⚠️  Automation completed with issues", style="bold yellow")
            console.print("🔧 Manual intervention may be required")
        
        # Return appropriate exit code
        return 0 if validation_results['status'] in ['SUCCESS', 'MOSTLY_SUCCESS'] else 1
        
    except Exception as e:
        console.print(f"❌ Automation failed: {str(e)}", style="red")
        import traceback
        console.print(f"🔍 Error details: {traceback.format_exc()}", style="dim")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 