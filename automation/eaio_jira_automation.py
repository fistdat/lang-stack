#!/usr/bin/env python3
"""
EAIO Jira Automation Script
Uses direct Jira REST API to automatically create all tasks from sprint plans
Supports multiple Jira projects

Author: AI Assistant
Date: December 2024
"""

import os
import re
import json
import asyncio
import base64
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Direct API imports
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()

@dataclass
class JiraProjectConfig:
    """Configuration for a Jira project"""
    key: str
    name: str
    description: str
    base_url: str
    board_id: Optional[str] = None

@dataclass
class Task:
    """Represents a task from sprint planning"""
    id: str
    title: str
    description: str
    story_points: int
    assignee: str
    duration: str
    priority: str
    dependencies: List[str]
    acceptance_criteria: List[str]
    epic: str
    sprint: str

@dataclass
class Epic:
    """Represents an epic from sprint planning"""
    name: str
    goal: str
    tasks: List[Task]
    sprint: str

@dataclass
class Sprint:
    """Represents a sprint with epics and tasks"""
    number: int
    name: str
    layer_focus: str
    duration: str
    story_points: int
    epics: List[Epic]

class JiraDirectAPI:
    """Direct Jira API client with multi-project support"""
    
    # Predefined project configurations
    PROJECT_CONFIGS = {
        "SCRUM": JiraProjectConfig(
            key="SCRUM",
            name="EAIO - Energy AI Optimizer",
            description="Main EAIO development project",
            base_url="https://fistdat.atlassian.net",
            board_id="1"
        ),
        "SMMG6": JiraProjectConfig(
            key="SMMG6",
            name="EAIO - Secondary Development",
            description="Secondary EAIO development project",
            base_url="https://fistdat.atlassian.net",
            board_id="34"
        )
    }
    
    def __init__(self, base_url: str, email: str, api_token: str, project_key: str = "SCRUM"):
        """Initialize with Jira credentials"""
        self.base_url = base_url
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        self.current_project = self.PROJECT_CONFIGS.get(project_key, 
            JiraProjectConfig(project_key, project_key, f"Project {project_key}", base_url))
        
        # Create auth header
        auth_string = f"{email}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Priority mapping
        self.priority_mapping = {
            "🔴": "High",
            "🟡": "Medium", 
            "🔵": "Low",
            "Highest": "Highest",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low"
        }

    def set_project(self, project_key: str) -> bool:
        """Switch to a different project"""
        if project_key in self.PROJECT_CONFIGS:
            self.project_key = project_key
            self.current_project = self.PROJECT_CONFIGS[project_key]
            console.print(f"🔄 Switched to project: {self.current_project.name} ({project_key})")
            return True
        else:
            console.print(f"❌ Unknown project: {project_key}")
            return False

    def get_available_projects(self) -> Dict[str, JiraProjectConfig]:
        """Get list of available project configurations"""
        return self.PROJECT_CONFIGS

    def test_connection(self) -> bool:
        """Test Jira connection"""
        try:
            url = f"{self.base_url}/rest/api/3/myself"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                console.print(f"✅ Connected as: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                console.print(f"❌ Connection failed: {response.text}")
                return False
        except Exception as e:
            console.print(f"❌ Connection error: {str(e)}")
            return False

    def test_project_access(self, project_key: str) -> bool:
        """Test access to specific project"""
        try:
            url = f"{self.base_url}/rest/api/3/project/{project_key}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                project_info = response.json()
                console.print(f"✅ Access confirmed for project: {project_info.get('name', project_key)}")
                return True
            else:
                console.print(f"❌ No access to project {project_key}: {response.text}")
                return False
        except Exception as e:
            console.print(f"❌ Project access error: {str(e)}")
            return False

    def create_epic(self, epic: Epic, sprint_number: int) -> Optional[str]:
        """Create epic in Jira"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"Sprint {sprint_number}: {epic.name}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Epic Goal: {epic.goal}\n\nSprint: {epic.sprint}\nTotal Tasks: {len(epic.tasks)}\nProject: {self.current_project.name}"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Epic"}
                # Removed Epic Name field to avoid configuration issues
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                result = response.json()
                epic_key = result['key']
                console.print(f"  ✅ Created Epic: {epic_key} - {epic.name}")
                return epic_key
            else:
                console.print(f"  ❌ Failed to create epic: {response.text}")
                return None
        except Exception as e:
            console.print(f"  ❌ Epic creation error: {str(e)}")
            return None

    def create_task(self, task: Task, epic_key: str) -> Optional[str]:
        """Create task in Jira"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        # Create basic task without Epic Link and Story Points (may not be configured)
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"{task.id}: {task.title}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Epic: {epic_key}\n\n{task.description}\n\nStory Points: {task.story_points}\nAssignee: {task.assignee}\nDuration: {task.duration}\nProject: {self.current_project.name}"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"}
                # Removed custom fields to avoid configuration issues
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                result = response.json()
                task_key = result['key']
                return task_key
            else:
                console.print(f"    ❌ Failed to create task {task.id}: {response.text}")
                return None
        except Exception as e:
            console.print(f"    ❌ Task creation error: {str(e)}")
            return None

class EAIOJiraAutomation:
    """Main automation class for creating EAIO tasks in Jira with multi-project support"""
    
    def __init__(self, jira_url: str, email: str, api_token: str, project_key: str = "SCRUM"):
        """Initialize automation with Jira credentials"""
        self.jira_client = JiraDirectAPI(jira_url, email, api_token, project_key)
        self.stats = {
            'sprints_processed': 0,
            'epics_created': 0,
            'epics_failed': 0,
            'tasks_created': 0,
            'tasks_failed': 0
        }
        
        # Rate limiting
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '0.5'))

    def switch_project(self, project_key: str) -> bool:
        """Switch to different Jira project"""
        return self.jira_client.set_project(project_key)

    def get_available_projects(self) -> Dict[str, JiraProjectConfig]:
        """Get available project configurations"""
        return self.jira_client.get_available_projects()

    def test_project_access(self, project_key: str) -> bool:
        """Test access to specific project"""
        return self.jira_client.test_project_access(project_key)

    def parse_sprint_file(self, file_path: Path) -> Sprint:
        """Parse a sprint markdown file and extract tasks"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sprint metadata
        sprint_match = re.search(r'# Sprint (\d+): (.+)', content)
        if not sprint_match:
            raise ValueError(f"Could not parse sprint number from {file_path}")
        
        sprint_number = int(sprint_match.group(1))
        sprint_name = sprint_match.group(2)
        
        # Extract layer focus
        layer_focus_match = re.search(r'\*\*Focus\*\*: (.+) with', content)
        layer_focus = layer_focus_match.group(1) if layer_focus_match else "Unknown"
        
        # Extract duration
        duration_match = re.search(r'\*\*Duration\*\*: (.+)', content)
        duration = duration_match.group(1) if duration_match else "14 days"
        
        # Extract total story points
        story_points_match = re.search(r'\*\*Story Points Target\*\*: (\d+)', content)
        story_points = int(story_points_match.group(1)) if story_points_match else 0
        
        # Parse epics and tasks
        epics = self._parse_epics(content, sprint_number, sprint_name)
        
        return Sprint(
            number=sprint_number,
            name=sprint_name,
            layer_focus=layer_focus,
            duration=duration,
            story_points=story_points,
            epics=epics
        )

    def _parse_epics(self, content: str, sprint_number: int, sprint_name: str) -> List[Epic]:
        """Parse epics from sprint content"""
        epics = []
        
        # First, parse all tasks in the sprint
        all_tasks = self._parse_all_tasks(content, sprint_number, sprint_name)
        print(f"  📋 Found {len(all_tasks)} total tasks in sprint")
        
        # Find epic sections with their positions
        epic_pattern = r'### Epic (\d+): (.+?)\n\*\*Goal\*\*: (.+?)(?=\n\n|\n### Epic|\Z)'
        epic_matches = list(re.finditer(epic_pattern, content, re.DOTALL))
        
        epic_count = 0
        for i, epic_match in enumerate(epic_matches):
            epic_count += 1
            epic_number = epic_match.group(1)
            epic_name = epic_match.group(2)
            epic_goal = epic_match.group(3)
            epic_start_pos = epic_match.start()
            
            # Find the next epic position or end of content
            if i + 1 < len(epic_matches):
                epic_end_pos = epic_matches[i + 1].start()
            else:
                epic_end_pos = len(content)
            
            # Get tasks that belong to this epic
            epic_tasks = [task for task in all_tasks 
                         if self._task_belongs_to_epic(content, task, epic_start_pos, epic_end_pos)]
            
            # Update epic name for tasks
            for task in epic_tasks:
                task.epic = epic_name
            
            print(f"    📝 Found Epic {epic_count}: {epic_name}")
            print(f"    📋 Assigned {len(epic_tasks)} tasks to epic: {epic_name}")
            
            epics.append(Epic(
                name=epic_name,
                goal=epic_goal,
                tasks=epic_tasks,
                sprint=sprint_name
            ))
        
        print(f"  📊 Total epics found: {len(epics)}")
        return epics

    def _parse_all_tasks(self, content: str, sprint_number: int, sprint_name: str) -> List[Task]:
        """Parse all tasks from sprint content"""
        tasks = []
        
        # Task pattern for format: **T*.*** - Task Title
        task_pattern = r'\*\*T(\d+)\.(\d+)\*\* - (.+?)\n(.*?)(?=\*\*T\d+\.|\n### Epic|\Z)'
        task_matches = re.finditer(task_pattern, content, re.DOTALL)
        
        for task_match in task_matches:
            sprint_id = task_match.group(1)
            task_id = task_match.group(2)
            task_title = task_match.group(3)
            task_content = task_match.group(4)
            
            print(f"      🎯 Found task: T{sprint_id}.{task_id} - {task_title}")
            
            # Parse task details
            story_points = self._extract_story_points(task_content)
            assignee = self._extract_assignee(task_content)
            duration = self._extract_duration(task_content)
            priority = self._extract_priority("🟡", task_content)  # Default priority
            dependencies = self._extract_dependencies(task_content)
            acceptance_criteria = self._extract_acceptance_criteria(task_content)
            
            # Generate description
            description = self._generate_task_description(
                task_content, "TBD", sprint_name, dependencies, acceptance_criteria
            )
            
            task = Task(
                id=f"T{sprint_id}.{task_id}",
                title=task_title,
                description=description,
                story_points=story_points,
                assignee=assignee,
                duration=duration,
                priority=priority,
                dependencies=dependencies,
                acceptance_criteria=acceptance_criteria,
                epic="TBD",  # Will be assigned later
                sprint=sprint_name
            )
            
            tasks.append(task)
        
        return tasks

    def _task_belongs_to_epic(self, content: str, task: Task, epic_start_pos: int, epic_end_pos: int) -> bool:
        """Determine if a task belongs to an epic based on position in content"""
        # Find task position in content
        task_pattern = f"\\*\\*{re.escape(task.id)}\\*\\*"
        task_match = re.search(task_pattern, content)
        
        if task_match:
            task_pos = task_match.start()
            return epic_start_pos <= task_pos < epic_end_pos
        
        return False

    def _parse_tasks(self, epic_content: str, epic_name: str, sprint_number: int, sprint_name: str) -> List[Task]:
        """Parse tasks from epic content"""
        tasks = []
        
        # Updated task pattern to match multiple formats
        patterns = [
            # Format 1: **T*.*** priority_emoji Task Title
            r'\*\*T(\d+)\.(\d+)\*\* (.+?) (.+?)\n(.+?)(?=\*\*T\d+\.|\n### |\Z)',
            # Format 2: **T*.*** - Task Title (multiline content)
            r'\*\*T(\d+)\.(\d+)\*\* - (.+?)\n(.*?)(?=\*\*T\d+\.|\n### |\Z)',
            # Format 3: **T*.*** Task Title (without priority emoji, multiline)
            r'\*\*T(\d+)\.(\d+)\*\* ([^-\n]+?)\n(.*?)(?=\*\*T\d+\.|\n### |\Z)'
        ]
        
        total_matches = 0
        for i, pattern in enumerate(patterns):
            task_matches = re.finditer(pattern, epic_content, re.DOTALL)
            for task_match in task_matches:
                total_matches += 1
                print(f"      🎯 Found task match (pattern {i+1}): {task_match.groups()[0:3]}")
                
                if i == 0:  # Format 1
                    sprint_id = task_match.group(1)
                    task_id = task_match.group(2)
                    priority_emoji = task_match.group(3)
                    task_title = task_match.group(4)
                    task_content = task_match.group(5)
                elif i == 1:  # Format 2  
                    sprint_id = task_match.group(1)
                    task_id = task_match.group(2)
                    task_title = task_match.group(3)
                    task_content = task_match.group(4)
                    priority_emoji = "🟡"  # Default priority
                else:  # Format 3
                    sprint_id = task_match.group(1)
                    task_id = task_match.group(2)
                    task_title = task_match.group(3)
                    task_content = task_match.group(4)
                    priority_emoji = "🟡"  # Default priority
                
                # Parse task details
                story_points = self._extract_story_points(task_content)
                assignee = self._extract_assignee(task_content)
                duration = self._extract_duration(task_content)
                priority = self._extract_priority(priority_emoji, task_content)
                dependencies = self._extract_dependencies(task_content)
                acceptance_criteria = self._extract_acceptance_criteria(task_content)
                
                # Generate description
                description = self._generate_task_description(
                    task_content, epic_name, sprint_name, dependencies, acceptance_criteria
                )
                
                task = Task(
                    id=f"T{sprint_id}.{task_id}",
                    title=task_title,
                    description=description,
                    story_points=story_points,
                    assignee=assignee,
                    duration=duration,
                    priority=priority,
                    dependencies=dependencies,
                    acceptance_criteria=acceptance_criteria,
                    epic=epic_name,
                    sprint=sprint_name
                )
                
                tasks.append(task)
                print(f"        ✅ Created task: {task.id} - {task.title}")
        
        print(f"      📈 Total task matches found: {total_matches}")
        print(f"      📋 Total tasks created: {len(tasks)}")
        return tasks

    def _extract_story_points(self, content: str) -> int:
        """Extract story points from task content"""
        sp_match = re.search(r'\*\*Story Points\*\*: (\d+)', content)
        return int(sp_match.group(1)) if sp_match else 0

    def _extract_assignee(self, content: str) -> str:
        """Extract assignee from task content"""
        assignee_match = re.search(r'\*\*Assignee\*\*: (.+)', content)
        return assignee_match.group(1) if assignee_match else "Unassigned"

    def _extract_duration(self, content: str) -> str:
        """Extract duration from task content"""
        duration_match = re.search(r'\*\*Duration\*\*: (.+)', content)
        return duration_match.group(1) if duration_match else "Unknown"

    def _extract_priority(self, emoji: str, content: str) -> str:
        """Extract priority from emoji and content"""
        if emoji in self.jira_client.priority_mapping:
            return self.jira_client.priority_mapping[emoji]
        
        priority_match = re.search(r'\*\*Priority\*\*: (.+)', content)
        if priority_match:
            priority_text = priority_match.group(1)
            return self.jira_client.priority_mapping.get(priority_text, "Medium")
        
        return "Medium"

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from task content"""
        deps_match = re.search(r'\*\*Dependencies\*\*: (.+)', content)
        if deps_match:
            deps_text = deps_match.group(1)
            if deps_text.lower() == "none":
                return []
            return [dep.strip() for dep in deps_text.split(',')]
        return []

    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria from task content"""
        criteria = []
        
        # Look for acceptance criteria section
        criteria_match = re.search(r'\*\*Acceptance Criteria\*\*:(.+?)(?=\*\*|$)', content, re.DOTALL)
        if criteria_match:
            criteria_content = criteria_match.group(1)
            
            # Extract checklist items
            checklist_pattern = r'- \[ \] (.+)'
            criteria = re.findall(checklist_pattern, criteria_content)
        
        return criteria

    def _generate_task_description(self, content: str, epic_name: str, sprint_name: str, 
                                 dependencies: List[str], acceptance_criteria: List[str]) -> str:
        """Generate comprehensive task description for Jira"""
        description_parts = [
            f"*Epic*: {epic_name}",
            f"*Sprint*: {sprint_name}",
            "",
            "*Task Details:*"
        ]
        
        # Add raw content (cleaned up)
        cleaned_content = re.sub(r'\*\*([^*]+)\*\*:', r'*\1*:', content)
        description_parts.append(cleaned_content)
        
        # Add dependencies if any
        if dependencies:
            description_parts.extend([
                "",
                "*Dependencies:*",
                "* " + "\n* ".join(dependencies)
            ])
        
        # Add acceptance criteria
        if acceptance_criteria:
            description_parts.extend([
                "",
                "*Acceptance Criteria:*"
            ])
            for criterion in acceptance_criteria:
                description_parts.append(f"* {criterion}")
        
        # Add architecture reference
        description_parts.extend([
            "",
            "*Architecture References:*",
            "* EAIO 6-Layer Architecture",
            "* Cognitive Framework Implementation",
            "* Task Management System"
        ])
        
        return "\n".join(description_parts)

    async def create_epic_in_jira(self, epic: Epic, sprint_number: int) -> str:
        """Create an epic in Jira and return its key"""
        epic_key = self.jira_client.create_epic(epic, sprint_number)
        if epic_key:
            self.stats['epics_created'] += 1
            print(f"  ✅ Created Epic: {epic_key} - {epic.name}")
            return epic_key
        else:
            self.stats['epics_failed'] += 1
            print(f"  ❌ Failed to create Epic: {epic.name}")
            return ""

    async def create_task_in_jira(self, task: Task, epic_key: str) -> str:
        """Create a task in Jira and return its key"""
        if not epic_key:
            self.stats['tasks_failed'] += 1
            print(f"    ⚠️  Skipping {task.title} - no valid epic")
            return ""
            
        task_key = self.jira_client.create_task(task, epic_key)
        if task_key:
            self.stats['tasks_created'] += 1
            print(f"    ✅ Created Task: {task_key} - {task.title}")
            return task_key
        else:
            self.stats['tasks_failed'] += 1
            print(f"    ❌ Failed to create task: {task.id} - {task.title}")
            return ""

    async def create_sprint_in_jira(self, sprint: Sprint) -> str:
        """Create a sprint in Jira and return its ID"""
        # Note: Sprint creation via API requires specific Jira permissions
        # For now, we'll skip sprint creation and focus on epics/tasks
        print(f"📝 Sprint {sprint.number}: {sprint.name} (create manually in Jira)")
        return f"SPRINT-{sprint.number}"

    async def process_all_sprints(self, sprints_directory: str = ".cursor/tasks/sprints"):
        """Process all sprint files and create them in Jira"""
        sprints_path = Path(sprints_directory)
        
        if not sprints_path.exists():
            print(f"❌ Sprints directory not found: {sprints_directory}")
            return
        
        # Get all sprint files
        sprint_files = sorted([f for f in sprints_path.glob("sprint_*.md")])
        
        print(f"🎯 Found {len(sprint_files)} sprint files to process")
        print("=" * 60)
        
        for sprint_file in sprint_files:
            print(f"\n📋 Processing: {sprint_file.name}")
            
            try:
                # Parse sprint
                sprint = self.parse_sprint_file(sprint_file)
                
                # Create sprint in Jira
                sprint_id = await self.create_sprint_in_jira(sprint)
                
                if not sprint_id:
                    print(f"⚠️  Skipping {sprint.name} due to sprint creation failure")
                    continue
                
                # Process each epic in the sprint
                for epic in sprint.epics:
                    print(f"\n  📁 Creating Epic: {epic.name}")
                    
                    # Create epic
                    epic_key = await self.create_epic_in_jira(epic, sprint.number)
                    
                    if not epic_key:
                        print(f"    ⚠️  Skipping tasks for epic {epic.name}")
                        continue
                    
                    # Create tasks for this epic
                    for task in epic.tasks:
                        await self.create_task_in_jira(task, epic_key)
                        await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                
                self.stats['sprints_processed'] += 1
                total_tasks = sum(len(e.tasks) for e in sprint.epics)
                print(f"✅ Completed Sprint {sprint.number}: {len(sprint.epics)} epics, {total_tasks} tasks")
                
            except Exception as e:
                print(f"❌ Error processing {sprint_file.name}: {str(e)}")
                continue
        
        print("\n" + "=" * 60)
        print("🎉 EAIO Jira automation completed!")

    async def create_summary_dashboard(self):
        """Create a summary dashboard issue for tracking"""
        # Note: Dashboard creation will be done manually or via separate script
        print(f"📊 Dashboard: EAIO Project Implementation Summary (create manually)")
        print(f"📈 Statistics: {self.stats}")
        return "DASHBOARD-MANUAL"

    def _generate_dashboard_description(self) -> str:
        """Generate description for the dashboard issue"""
        return """
*EAIO Project Implementation Dashboard*

*Project Overview:*
* Energy AI Optimizer (EAIO) - 6-Layer Architecture Implementation
* 10 Sprints, 120+ Tasks, 792 Story Points
* Target: 15-30% energy reduction, 200-400% ROI

*Architecture Layers:*
* Layer 1: User Interface (Next.js + Streamlit)
* Layer 2: Hybrid LLM Infrastructure (Ollama + Cloud APIs)
* Layer 3: MCP Integration Layer (Event-driven)
* Layer 4: Multi-Agent Framework (LangGraph)
* Layer 5: Memory Systems (5-layer architecture)
* Layer 6: Data Infrastructure (PostgreSQL + Milvus)

*Sprint Overview:*
* Sprint 1-2: Database Foundation
* Sprint 3: LLM Infrastructure
* Sprint 4: MCP Integration
* Sprint 5: Multi-Agent Framework
* Sprint 6: Memory Systems
* Sprint 7: Frontend Development
* Sprint 8: System Integration
* Sprint 9: Deployment Optimization
* Sprint 10: Production Launch

*Key Performance Targets:*
* Database queries: <100ms
* LLM inference: <2s
* Vector search: <50ms
* System availability: 99.9%

*Technology Stack:*
* Database: PostgreSQL + TimescaleDB + Milvus + Redis
* LLM: Qwen2.5-7B + Llama-3.2-3B + External APIs
* Frontend: Next.js + Streamlit + PWA
* Infrastructure: Docker + Kubernetes + AWS EKS
* Data: BDG2 dataset (53.6M data points, 1,636 buildings)

*Cognitive Framework:*
* Architecture Mode (A.*): Business-first system design
* Development Mode (T.*): Task-driven implementation
* Hybrid Mode: Coordinated design-implementation

*Business Value:*
* Real-time energy intelligence
* Predictive analytics
* Autonomous optimization
* Natural language interface
* Portfolio management
"""

    async def process_single_sprint(self, sprint: Sprint):
        """Process a single sprint and create epics/tasks in Jira"""
        # Create sprint in Jira (manual for now)
        sprint_id = await self.create_sprint_in_jira(sprint)
        
        if not sprint_id:
            print(f"⚠️  Skipping {sprint.name} due to sprint creation failure")
            return
        
        # Process each epic in the sprint
        for epic in sprint.epics:
            print(f"\n  📁 Creating Epic: {epic.name}")
            
            # Create epic
            epic_key = await self.create_epic_in_jira(epic, sprint.number)
            
            if not epic_key:
                print(f"    ⚠️  Skipping tasks for epic {epic.name}")
                continue
            
            # Create tasks for this epic
            for task in epic.tasks:
                await self.create_task_in_jira(task, epic_key)
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
        
        print(f"✅ Completed Sprint {sprint.number}: {len(sprint.epics)} epics, {sum(len(epic.tasks) for epic in sprint.epics)} tasks")

    def _get_sprints_path(self, sprints_directory: str):
        """Get the path to sprints directory"""
        from pathlib import Path
        return Path(sprints_directory)

def main():
    """Main function to run the automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EAIO Jira Automation")
    parser.add_argument("--jira-url", required=True, help="Jira URL (e.g., https://fistdat.atlassian.net)")
    parser.add_argument("--email", required=True, help="Jira email")
    parser.add_argument("--api-token", required=True, help="Jira API token")
    parser.add_argument("--project-key", default="SCRUM", help="Jira project key")
    parser.add_argument("--sprints-dir", default=".cursor/tasks/sprints", help="Sprints directory")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't create in Jira")
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = EAIOJiraAutomation(
        jira_url=args.jira_url,
        email=args.email,
        api_token=args.api_token,
        project_key=args.project_key
    )
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Parsing sprints only")
        # Add dry run logic here
    else:
        # Run the automation
        asyncio.run(automation.process_all_sprints(args.sprints_dir))
        asyncio.run(automation.create_summary_dashboard())


if __name__ == "__main__":
    main() 