#!/usr/bin/env python3
"""
EAIO Project Automation Script
Automates creation of Epics, Features, User Stories, Tasks, Sprints in Jira
and Documentation structure in Confluence
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. Using environment variables directly.")
    pass

class AtlassianAutomation:
    def __init__(self, jira_url: str, confluence_url: str, email: str, api_token: str):
        self.jira_url = jira_url.rstrip('/')
        self.confluence_url = confluence_url.rstrip('/')
        self.auth = (email, api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.project_key = 'SMMG6'
        self.space_key = 'S'
        self.created_items = {
            'epics': {},
            'features': {},
            'user_stories': {},
            'tasks': {},
            'sprints': {},
            'confluence_pages': {}
        }

    def create_jira_issue(self, issue_data: Dict) -> Optional[Dict]:
        """Create a Jira issue"""
        url = f"{self.jira_url}/rest/api/3/issue"
        try:
            response = requests.post(url, json=issue_data, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created: {issue_data['fields']['summary']} ({result['key']})")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating issue: {issue_data['fields']['summary']}")
            print(f"  Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None

    def create_sprint(self, sprint_data: Dict) -> Optional[Dict]:
        """Create a sprint"""
        # First, get the board ID for the project
        board_url = f"{self.jira_url}/rest/agile/1.0/board?projectKeyOrId={self.project_key}"
        try:
            board_response = requests.get(board_url, auth=self.auth, headers=self.headers)
            board_response.raise_for_status()
            boards = board_response.json()

            if not boards.get('values'):
                print(f"✗ No board found for project {self.project_key}")
                return None

            board_id = boards['values'][0]['id']

            # Create sprint
            sprint_url = f"{self.jira_url}/rest/agile/1.0/sprint"
            sprint_payload = {
                "name": sprint_data['name'],
                "startDate": sprint_data['startDate'],
                "endDate": sprint_data['endDate'],
                "originBoardId": board_id
            }

            response = requests.post(sprint_url, json=sprint_payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created Sprint: {sprint_data['name']} (ID: {result['id']})")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating sprint: {sprint_data['name']}")
            print(f"  Error: {e}")
            return None

    def add_issue_to_sprint(self, issue_key: str, sprint_id: int):
        """Add an issue to a sprint"""
        url = f"{self.jira_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        payload = {
            "issues": [issue_key]
        }
        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            print(f"  ✓ Added {issue_key} to sprint {sprint_id}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error adding {issue_key} to sprint: {e}")

    def create_confluence_page(self, page_data: Dict) -> Optional[Dict]:
        """Create a Confluence page"""
        url = f"{self.confluence_url}/rest/api/content"
        try:
            response = requests.post(url, json=page_data, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created Page: {page_data['title']} (ID: {result['id']})")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating page: {page_data['title']}")
            print(f"  Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None

    def link_jira_to_confluence(self, issue_key: str, confluence_page_id: str):
        """Create a link between Jira issue and Confluence page"""
        # Add web link to Jira issue
        confluence_page_url = f"{self.confluence_url}/pages/viewpage.action?pageId={confluence_page_id}"
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/remotelink"
        payload = {
            "object": {
                "url": confluence_page_url,
                "title": "Related Documentation"
            }
        }
        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            print(f"  ✓ Linked {issue_key} to Confluence page")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error linking {issue_key} to Confluence: {e}")

    def create_eaio_project_structure(self):
        """Create the complete EAIO project structure"""
        print("\n" + "="*80)
        print("EAIO PROJECT AUTOMATION - STARTING")
        print("="*80 + "\n")

        # Define sprints (8 sprints x 2 weeks, starting from today)
        sprints = self.create_sprints()

        # Create all epics, features, user stories, and tasks
        self.create_epic_1_foundation(sprints)
        self.create_epic_2_data_management(sprints)
        self.create_epic_3_multi_agent(sprints)
        self.create_epic_4_ui_experience(sprints)
        self.create_epic_5_observability(sprints)
        self.create_epic_6_testing_deployment(sprints)

        # Create Confluence documentation structure
        self.create_confluence_structure()

        print("\n" + "="*80)
        print("EAIO PROJECT AUTOMATION - COMPLETED")
        print("="*80 + "\n")

        # Save summary
        self.save_summary()

    def create_sprints(self) -> Dict:
        """Create 8 sprints"""
        print("\n--- CREATING SPRINTS ---\n")
        sprints = {}
        start_date = datetime.now()

        sprint_definitions = [
            ("Sprint 0", 0, 26),
            ("Sprint 1", 1, 34),
            ("Sprint 2", 2, 34),
            ("Sprint 3", 3, 34),
            ("Sprint 4", 4, 42),
            ("Sprint 5", 5, 39),
            ("Sprint 6", 6, 42),
            ("Sprint 7", 7, 39),
            ("Sprint 8", 8, 47),
        ]

        for sprint_name, sprint_num, story_points in sprint_definitions:
            sprint_start = start_date + timedelta(weeks=sprint_num*2)
            sprint_end = sprint_start + timedelta(weeks=2, days=-1)

            sprint_data = {
                'name': f"{sprint_name}: EAIO ({story_points}pts)",
                'startDate': sprint_start.isoformat() + 'Z',
                'endDate': sprint_end.isoformat() + 'Z'
            }

            result = self.create_sprint(sprint_data)
            if result:
                sprints[sprint_num] = result
            time.sleep(0.5)  # Rate limiting

        return sprints

    def create_epic_1_foundation(self, sprints: Dict):
        """Epic 1: Project Foundation & Infrastructure"""
        print("\n--- EPIC 1: PROJECT FOUNDATION & INFRASTRUCTURE ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 1: Project Foundation & Infrastructure",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Thiết lập nền tảng cho toàn bộ dự án. Duration: Sprint 0-1. Story Points: 60. Success Criteria: Lang Stack hoạt động ổn định, database schema deployed"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic1'] = epic
        epic_key = epic['key']

        # Feature 1.1: Project Initiation
        print("\n  Feature 1.1: Project Initiation")

        # US-001: Setup Development Environment (5 pts)
        us001 = self.create_user_story(
            epic_key, "US-001: Setup Development Environment",
            "Setup Development Environment với Docker, Git, VSCode",
            5, ["High"], sprints.get(0)
        )

        if us001:
            self.create_task(us001['key'], "Task 1.1: Cài đặt Docker Desktop và configure daemon", sprints.get(0))
            self.create_task(us001['key'], "Task 1.2: Setup Git repository với branching strategy", sprints.get(0))
            self.create_task(us001['key'], "Task 1.3: Configure VS Code với extensions", sprints.get(0))
            self.create_task(us001['key'], "Task 1.4: Setup Docker Hub account", sprints.get(0))

        # US-002: Stakeholder Requirements Analysis (8 pts)
        us002 = self.create_user_story(
            epic_key, "US-002: Stakeholder Requirements Analysis",
            "Conduct stakeholder interviews and document requirements",
            8, ["Critical"], sprints.get(0)
        )

        if us002:
            self.create_task(us002['key'], "Task 2.1: Conduct interviews với 3 stakeholder groups", sprints.get(0))
            self.create_task(us002['key'], "Task 2.2: Tạo Requirements Traceability Matrix", sprints.get(0))
            self.create_task(us002['key'], "Task 2.3: Document functional requirements (Tables 1-5)", sprints.get(0))
            self.create_task(us002['key'], "Task 2.4: Define non-functional requirements", sprints.get(0))
            self.create_task(us002['key'], "Task 2.5: Create acceptance criteria", sprints.get(0))

        # US-003: Initial Architecture Design (13 pts)
        us003 = self.create_user_story(
            epic_key, "US-003: Initial Architecture Design",
            "Design Lang Stack integrated architecture",
            13, ["Critical"], sprints.get(0)
        )

        if us003:
            self.create_task(us003['key'], "Task 3.1: Design Lang Stack architecture (Figure 1)", sprints.get(0))
            self.create_task(us003['key'], "Task 3.2: Create technology decision matrix", sprints.get(0))
            self.create_task(us003['key'], "Task 3.3: Document infrastructure requirements", sprints.get(0))
            self.create_task(us003['key'], "Task 3.4: Risk assessment", sprints.get(0))
            self.create_task(us003['key'], "Task 3.5: Architecture review presentation", sprints.get(0))

        # Feature 1.2: Docker Infrastructure Deployment (Sprint 1)
        print("\n  Feature 1.2: Docker Infrastructure Deployment")

        # US-004: Docker Compose Infrastructure (13 pts)
        us004 = self.create_user_story(
            epic_key, "US-004: Docker Compose Infrastructure",
            "Setup docker-compose với 8+ services (Langflow, Langfuse, PostgreSQL, ClickHouse, Redis, MinIO)",
            13, ["Critical"], sprints.get(1)
        )

        if us004:
            self.create_task(us004['key'], "Task 4.1: Create docker-compose.yml với 8+ services", sprints.get(1))
            self.create_task(us004['key'], "Task 4.2: Configure Langflow container", sprints.get(1))
            self.create_task(us004['key'], "Task 4.3: Configure Langfuse stack", sprints.get(1))
            self.create_task(us004['key'], "Task 4.4: Setup service networking", sprints.get(1))
            self.create_task(us004['key'], "Task 4.5: Create health check endpoints", sprints.get(1))
            self.create_task(us004['key'], "Task 4.6: Test full stack deployment", sprints.get(1))

        # US-005: Database Schema Implementation (13 pts)
        us005 = self.create_user_story(
            epic_key, "US-005: Database Schema Implementation",
            "Implement database schema với TimescaleDB hypertables",
            13, ["Critical"], sprints.get(1)
        )

        if us005:
            self.create_task(us005['key'], "Task 5.1: Create buildings table với indexes", sprints.get(1))
            self.create_task(us005['key'], "Task 5.2: Create energy_meters table", sprints.get(1))
            self.create_task(us005['key'], "Task 5.3: Setup TimescaleDB extension", sprints.get(1))
            self.create_task(us005['key'], "Task 5.4: Create weather_data hypertable", sprints.get(1))
            self.create_task(us005['key'], "Task 5.5: Create energy_analytics table", sprints.get(1))
            self.create_task(us005['key'], "Task 5.6: Create ERD (Figure 9)", sprints.get(1))
            self.create_task(us005['key'], "Task 5.7: Write database migration scripts", sprints.get(1))

        # US-006: Langfuse Integration Testing (8 pts)
        us006 = self.create_user_story(
            epic_key, "US-006: Langfuse Integration Testing",
            "Configure và test Langfuse integration với Langflow",
            8, ["High"], sprints.get(1)
        )

        if us006:
            self.create_task(us006['key'], "Task 6.1: Configure Langfuse API keys", sprints.get(1))
            self.create_task(us006['key'], "Task 6.2: Test automated trace collection", sprints.get(1))
            self.create_task(us006['key'], "Task 6.3: Create sample traces from Langflow", sprints.get(1))
            self.create_task(us006['key'], "Task 6.4: Verify traces in Langfuse UI", sprints.get(1))
            self.create_task(us006['key'], "Task 6.5: Setup monitoring dashboards", sprints.get(1))
            self.create_task(us006['key'], "Task 6.6: Test trace persistence", sprints.get(1))

    def create_epic_2_data_management(self, sprints: Dict):
        """Epic 2: Data Management & Integration"""
        print("\n--- EPIC 2: DATA MANAGEMENT & INTEGRATION ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 2: Data Management & Integration",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Tích hợp BDG2 dataset để validate hệ thống. Duration: Sprint 2. Story Points: 34. Success Criteria: 53.6M records imported thành công"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic2'] = epic
        epic_key = epic['key']

        # US-007: BDG2 Dataset ETL Pipeline (21 pts)
        us007 = self.create_user_story(
            epic_key, "US-007: BDG2 Dataset ETL Pipeline",
            "Create ETL pipeline để import 53.6M records từ BDG2 dataset",
            21, ["Critical"], sprints.get(2)
        )

        if us007:
            self.create_task(us007['key'], "Task 7.1: Download BDG2 dataset", sprints.get(2))
            self.create_task(us007['key'], "Task 7.2: Analyze dataset structure", sprints.get(2))
            self.create_task(us007['key'], "Task 7.3: Create ETL pipeline cho buildings", sprints.get(2))
            self.create_task(us007['key'], "Task 7.4: Create ETL pipeline cho meter readings", sprints.get(2))
            self.create_task(us007['key'], "Task 7.5: Create ETL pipeline cho weather data", sprints.get(2))
            self.create_task(us007['key'], "Task 7.6: Data quality validation", sprints.get(2))
            self.create_task(us007['key'], "Task 7.7: Performance optimization", sprints.get(2))

        # US-008: Data Preprocessing & Analytics Setup (13 pts)
        us008 = self.create_user_story(
            epic_key, "US-008: Data Preprocessing & Analytics Setup",
            "Calculate baseline metrics và create aggregated views",
            13, ["High"], sprints.get(2)
        )

        if us008:
            self.create_task(us008['key'], "Task 8.1: Calculate baseline metrics (EUI, ENERGY STAR)", sprints.get(2))
            self.create_task(us008['key'], "Task 8.2: Create aggregated views", sprints.get(2))
            self.create_task(us008['key'], "Task 8.3: Create materialized views", sprints.get(2))
            self.create_task(us008['key'], "Task 8.4: Setup continuous aggregates (TimescaleDB)", sprints.get(2))
            self.create_task(us008['key'], "Task 8.5: Create indexes for analytics queries", sprints.get(2))
            self.create_task(us008['key'], "Task 8.6: Generate test datasets", sprints.get(2))
            self.create_task(us008['key'], "Task 8.7: Benchmark query performance", sprints.get(2))

    def create_epic_3_multi_agent(self, sprints: Dict):
        """Epic 3: Multi-Agent System Development"""
        print("\n--- EPIC 3: MULTI-AGENT SYSTEM DEVELOPMENT ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 3: Multi-Agent System Development",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Core AI agents cung cấp năng lực phân tích và tối ưu năng lượng. Duration: Sprint 3-5. Story Points: 115. Success Criteria: 6 agents hoạt động độc lập và orchestration thành công"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic3'] = epic
        epic_key = epic['key']

        # Sprint 3: Core Agents Part 1
        print("\n  Sprint 3: Core Agents Part 1")

        # US-009: Energy Data Intelligence Agent (21 pts)
        us009 = self.create_user_story(
            epic_key, "US-009: Energy Data Intelligence Agent",
            "Develop Energy Data Intelligence Agent với Granite TTM và anomaly detection",
            21, ["Critical"], sprints.get(3)
        )

        if us009:
            self.create_task(us009['key'], "Task 9.1: Design Langflow workflow architecture", sprints.get(3))
            self.create_task(us009['key'], "Task 9.2: Integrate Granite TTM foundation model", sprints.get(3))
            self.create_task(us009['key'], "Task 9.3: Implement anomaly detection algorithms", sprints.get(3))
            self.create_task(us009['key'], "Task 9.4: Create SQL query generation", sprints.get(3))
            self.create_task(us009['key'], "Task 9.5: Implement pattern analysis", sprints.get(3))
            self.create_task(us009['key'], "Task 9.6: Integrate Langfuse tracing", sprints.get(3))
            self.create_task(us009['key'], "Task 9.7: Create comprehensive test cases", sprints.get(3))

        # US-010: Weather Intelligence Agent (13 pts)
        us010 = self.create_user_story(
            epic_key, "US-010: Weather Intelligence Agent",
            "Develop Weather Intelligence Agent với AccuWeather API integration",
            13, ["High"], sprints.get(3)
        )

        if us010:
            self.create_task(us010['key'], "Task 10.1: Setup AccuWeather API integration", sprints.get(3))
            self.create_task(us010['key'], "Task 10.2: Implement location-based weather retrieval", sprints.get(3))
            self.create_task(us010['key'], "Task 10.3: Create weather-energy correlation analysis", sprints.get(3))
            self.create_task(us010['key'], "Task 10.4: Implement degree day calculations (HDD/CDD)", sprints.get(3))
            self.create_task(us010['key'], "Task 10.5: Build seasonal pattern recognition", sprints.get(3))
            self.create_task(us010['key'], "Task 10.6: Create Langflow workflow", sprints.get(3))
            self.create_task(us010['key'], "Task 10.7: Setup monitoring and alerting", sprints.get(3))

        # Sprint 4: Core Agents Part 2
        print("\n  Sprint 4: Core Agents Part 2")

        # US-011: Optimization Strategy Agent (21 pts)
        us011 = self.create_user_story(
            epic_key, "US-011: Optimization Strategy Agent",
            "Develop Optimization Strategy Agent với GRPO RL và ROI calculations",
            21, ["Critical"], sprints.get(4)
        )

        if us011:
            self.create_task(us011['key'], "Task 11.1: Design ROI calculation framework", sprints.get(4))
            self.create_task(us011['key'], "Task 11.2: Integrate GRPO reinforcement learning", sprints.get(4))
            self.create_task(us011['key'], "Task 11.3: Create investment prioritization algorithm", sprints.get(4))
            self.create_task(us011['key'], "Task 11.4: Implement ENERGY STAR certification pathway", sprints.get(4))
            self.create_task(us011['key'], "Task 11.5: Build carbon footprint calculator", sprints.get(4))
            self.create_task(us011['key'], "Task 11.6: Create load shifting optimizer", sprints.get(4))
            self.create_task(us011['key'], "Task 11.7: Risk assessment framework", sprints.get(4))

        # US-012: Forecast Intelligence Agent (21 pts)
        us012 = self.create_user_story(
            epic_key, "US-012: Forecast Intelligence Agent",
            "Develop Forecast Intelligence Agent với time-series forecasting (R² ≥ 0.95)",
            21, ["Critical"], sprints.get(4)
        )

        if us012:
            self.create_task(us012['key'], "Task 12.1: Implement time-series forecasting models", sprints.get(4))
            self.create_task(us012['key'], "Task 12.2: Create long-term energy forecasting", sprints.get(4))
            self.create_task(us012['key'], "Task 12.3: Build equipment failure prediction", sprints.get(4))
            self.create_task(us012['key'], "Task 12.4: Implement peak demand forecasting", sprints.get(4))
            self.create_task(us012['key'], "Task 12.5: Create renewable integration assessment", sprints.get(4))
            self.create_task(us012['key'], "Task 12.6: Build ensemble validation framework", sprints.get(4))
            self.create_task(us012['key'], "Task 12.7: Implement Langflow workflow", sprints.get(4))

        # Sprint 5: Control & Validation
        print("\n  Sprint 5: Control & Validation")

        # US-013: System Control Agent (13 pts)
        us013 = self.create_user_story(
            epic_key, "US-013: System Control Agent",
            "Develop System Control Agent với HVAC optimization (<100ms response)",
            13, ["High"], sprints.get(5)
        )

        if us013:
            self.create_task(us013['key'], "Task 13.1: Design HVAC optimization logic", sprints.get(5))
            self.create_task(us013['key'], "Task 13.2: Implement setpoint management", sprints.get(5))
            self.create_task(us013['key'], "Task 13.3: Create zone-based control strategies", sprints.get(5))
            self.create_task(us013['key'], "Task 13.4: Physics-informed validation", sprints.get(5))
            self.create_task(us013['key'], "Task 13.5: Build BMS integration framework", sprints.get(5))
            self.create_task(us013['key'], "Task 13.6: Implement optimal control strategies", sprints.get(5))

        # US-014: Validator Agent (13 pts)
        us014 = self.create_user_story(
            epic_key, "US-014: Validator Agent",
            "Develop Validator Agent với compliance checks và safety validation",
            13, ["High"], sprints.get(5)
        )

        if us014:
            self.create_task(us014['key'], "Task 14.1: Create data quality validation framework", sprints.get(5))
            self.create_task(us014['key'], "Task 14.2: Implement compliance verification (ASHRAE, ISO)", sprints.get(5))
            self.create_task(us014['key'], "Task 14.3: Build safety validation engine", sprints.get(5))
            self.create_task(us014['key'], "Task 14.4: Create error detection mechanisms", sprints.get(5))
            self.create_task(us014['key'], "Task 14.5: Implement recommendation validation", sprints.get(5))

        # US-015: Multi-Agent Orchestration (13 pts)
        us015 = self.create_user_story(
            epic_key, "US-015: Multi-Agent Orchestration",
            "Implement multi-agent orchestration với state management",
            13, ["Critical"], sprints.get(5)
        )

        if us015:
            self.create_task(us015['key'], "Task 15.1: Design orchestration workflows in Langflow", sprints.get(5))
            self.create_task(us015['key'], "Task 15.2: Implement conditional routing logic", sprints.get(5))
            self.create_task(us015['key'], "Task 15.3: Create state management system", sprints.get(5))
            self.create_task(us015['key'], "Task 15.4: Build agent handoff mechanisms", sprints.get(5))
            self.create_task(us015['key'], "Task 15.5: Setup performance monitoring", sprints.get(5))

    def create_epic_4_ui_experience(self, sprints: Dict):
        """Epic 4: User Interface & Experience"""
        print("\n--- EPIC 4: USER INTERFACE & EXPERIENCE ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 4: User Interface & Experience",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Conversational AI và UI làm hệ thống accessible cho stakeholders. Duration: Sprint 6. Story Points: 42. Success Criteria: 3 stakeholder roles có thể sử dụng hệ thống hiệu quả"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic4'] = epic
        epic_key = epic['key']

        # US-016: Natural Language Interface (21 pts)
        us016 = self.create_user_story(
            epic_key, "US-016: Natural Language Interface",
            "Develop conversational AI interface với intent classification (≥90% accuracy)",
            21, ["Critical"], sprints.get(6)
        )

        if us016:
            self.create_task(us016['key'], "Task 16.1: Design conversation flow architecture", sprints.get(6))
            self.create_task(us016['key'], "Task 16.2: Implement query processing pipeline", sprints.get(6))
            self.create_task(us016['key'], "Task 16.3: Create multi-turn conversation management", sprints.get(6))
            self.create_task(us016['key'], "Task 16.4: Build context preservation mechanism", sprints.get(6))
            self.create_task(us016['key'], "Task 16.5: Implement query routing logic", sprints.get(6))
            self.create_task(us016['key'], "Task 16.6: Integrate all 6 agents", sprints.get(6))
            self.create_task(us016['key'], "Task 16.7: Create response generation system", sprints.get(6))

        # US-017: Responsive Web Application (21 pts)
        us017 = self.create_user_story(
            epic_key, "US-017: Responsive Web Application",
            "Build responsive web app cho 3 stakeholder roles (React + Recharts)",
            21, ["Critical"], sprints.get(6)
        )

        if us017:
            self.create_task(us017['key'], "Task 17.1: Design UI/UX for 3 stakeholder types", sprints.get(6))
            self.create_task(us017['key'], "Task 17.2: Implement React components", sprints.get(6))
            self.create_task(us017['key'], "Task 17.3: Create role-based access control", sprints.get(6))
            self.create_task(us017['key'], "Task 17.4: Build real-time monitoring displays", sprints.get(6))
            self.create_task(us017['key'], "Task 17.5: Integrate Langflow API endpoints", sprints.get(6))
            self.create_task(us017['key'], "Task 17.6: Implement data visualization (Recharts)", sprints.get(6))
            self.create_task(us017['key'], "Task 17.7: Create responsive layouts", sprints.get(6))

    def create_epic_5_observability(self, sprints: Dict):
        """Epic 5: Observability & Quality Assurance"""
        print("\n--- EPIC 5: OBSERVABILITY & QUALITY ASSURANCE ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 5: Observability & Quality Assurance",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Comprehensive monitoring đảm bảo production-ready system. Duration: Sprint 7. Story Points: 39. Success Criteria: 99.5% uptime với automated quality evaluation"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic5'] = epic
        epic_key = epic['key']

        # US-018: Comprehensive Tracing & Monitoring (13 pts)
        us018 = self.create_user_story(
            epic_key, "US-018: Comprehensive Tracing & Monitoring",
            "Setup Langfuse observability với distributed tracing và cost tracking",
            13, ["Critical"], sprints.get(7)
        )

        if us018:
            self.create_task(us018['key'], "Task 18.1: Setup distributed tracing", sprints.get(7))
            self.create_task(us018['key'], "Task 18.2: Configure session tracking", sprints.get(7))
            self.create_task(us018['key'], "Task 18.3: Implement cost tracking dashboards", sprints.get(7))
            self.create_task(us018['key'], "Task 18.4: Create latency monitoring", sprints.get(7))
            self.create_task(us018['key'], "Task 18.5: Setup environment management", sprints.get(7))
            self.create_task(us018['key'], "Task 18.6: Create comprehensive monitoring dashboards", sprints.get(7))

        # US-019: Automated Quality Evaluation (13 pts)
        us019 = self.create_user_story(
            epic_key, "US-019: Automated Quality Evaluation",
            "Configure LLM-as-a-Judge với 8 evaluators và threshold management",
            13, ["High"], sprints.get(7)
        )

        if us019:
            self.create_task(us019['key'], "Task 19.1: Configure 8 evaluators with thresholds", sprints.get(7))
            self.create_task(us019['key'], "Task 19.2: Setup scoring threshold system", sprints.get(7))
            self.create_task(us019['key'], "Task 19.3: Implement automated scoring pipeline", sprints.get(7))
            self.create_task(us019['key'], "Task 19.4: Create evaluation dashboards", sprints.get(7))
            self.create_task(us019['key'], "Task 19.5: Setup alerting system", sprints.get(7))

        # US-020: System Performance Optimization (13 pts)
        us020 = self.create_user_story(
            epic_key, "US-020: System Performance Optimization",
            "Optimize performance để achieve 99.5% uptime và response time targets",
            13, ["High"], sprints.get(7)
        )

        if us020:
            self.create_task(us020['key'], "Task 20.1: Database query optimization", sprints.get(7))
            self.create_task(us020['key'], "Task 20.2: Implement comprehensive caching strategy", sprints.get(7))
            self.create_task(us020['key'], "Task 20.3: Conduct load testing (100 concurrent users)", sprints.get(7))
            self.create_task(us020['key'], "Task 20.4: Perform bottleneck analysis", sprints.get(7))
            self.create_task(us020['key'], "Task 20.5: Response time optimization", sprints.get(7))

    def create_epic_6_testing_deployment(self, sprints: Dict):
        """Epic 6: Testing & Production Deployment"""
        print("\n--- EPIC 6: TESTING & PRODUCTION DEPLOYMENT ---\n")

        epic_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": "EPIC 6: Testing & Production Deployment",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": "Production-ready deployment với comprehensive testing. Duration: Sprint 8. Story Points: 47. Success Criteria: System deployed thành công với full documentation"
                        }]
                    }]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        epic = self.create_jira_issue(epic_data)
        if not epic:
            return

        self.created_items['epics']['epic6'] = epic
        epic_key = epic['key']

        # US-021: Testing Suite (21 pts)
        us021 = self.create_user_story(
            epic_key, "US-021: Testing Suite",
            "Comprehensive testing (unit, integration, E2E, performance, security)",
            21, ["Critical"], sprints.get(8)
        )

        if us021:
            self.create_task(us021['key'], "Task 21.1: Unit testing all agents (≥80% coverage)", sprints.get(8))
            self.create_task(us021['key'], "Task 21.2: Integration testing workflows", sprints.get(8))
            self.create_task(us021['key'], "Task 21.3: End-to-end testing scenarios", sprints.get(8))
            self.create_task(us021['key'], "Task 21.4: Performance testing with full dataset", sprints.get(8))
            self.create_task(us021['key'], "Task 21.5: Security testing (OWASP Top 10)", sprints.get(8))

        # US-022: Complete Documentation (13 pts)
        us022 = self.create_user_story(
            epic_key, "US-022: Complete Documentation",
            "Create complete documentation for technical, user, API, and deployment",
            13, ["High"], sprints.get(8)
        )

        if us022:
            self.create_task(us022['key'], "Task 22.1: Technical documentation", sprints.get(8))
            self.create_task(us022['key'], "Task 22.2: User manuals for 3 stakeholder types", sprints.get(8))
            self.create_task(us022['key'], "Task 22.3: API documentation (Swagger/OpenAPI)", sprints.get(8))
            self.create_task(us022['key'], "Task 22.4: Deployment guides", sprints.get(8))
            self.create_task(us022['key'], "Task 22.5: Thesis finalization", sprints.get(8))

        # US-023: Go-Live (13 pts)
        us023 = self.create_user_story(
            epic_key, "US-023: Go-Live",
            "Production deployment với monitoring, backup, và user training",
            13, ["Critical"], sprints.get(8)
        )

        if us023:
            self.create_task(us023['key'], "Task 23.1: Production environment setup", sprints.get(8))
            self.create_task(us023['key'], "Task 23.2: Data migration to production", sprints.get(8))
            self.create_task(us023['key'], "Task 23.3: Monitoring configuration", sprints.get(8))
            self.create_task(us023['key'], "Task 23.4: Backup & disaster recovery", sprints.get(8))
            self.create_task(us023['key'], "Task 23.5: Go-live execution", sprints.get(8))

    def create_user_story(self, epic_key: str, summary: str, description: str,
                         story_points: int, labels: List[str], sprint: Optional[Dict]) -> Optional[Dict]:
        """Create a user story linked to an epic"""
        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": description
                        }]
                    }]
                },
                "issuetype": {"name": "Story"},
                "parent": {"key": epic_key},
                "labels": labels,
                "customfield_10016": story_points  # Story Points
            }
        }

        result = self.create_jira_issue(issue_data)
        if result and sprint:
            self.add_issue_to_sprint(result['key'], sprint['id'])

        time.sleep(0.3)  # Rate limiting
        return result

    def create_task(self, parent_key: str, summary: str, sprint: Optional[Dict]) -> Optional[Dict]:
        """Create a task under a user story"""
        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "issuetype": {"name": "Task"},
                "parent": {"key": parent_key}
            }
        }

        result = self.create_jira_issue(issue_data)
        if result and sprint:
            self.add_issue_to_sprint(result['key'], sprint['id'])

        time.sleep(0.2)  # Rate limiting
        return result

    def create_confluence_structure(self):
        """Create Confluence documentation structure"""
        print("\n--- CREATING CONFLUENCE DOCUMENTATION STRUCTURE ---\n")

        # This would create the complete Confluence page hierarchy
        # For brevity, showing structure for Epic 1 only

        # Create root page
        root_page = self.create_confluence_page({
            "type": "page",
            "title": "EAIO-2025 Project Documentation",
            "space": {"key": self.space_key},
            "body": {
                "storage": {
                    "value": "<h1>EAIO - Energy AI Optimizer Project</h1><p>Master documentation hub for the EAIO project</p>",
                    "representation": "storage"
                }
            }
        })

        if not root_page:
            return

        root_id = root_page['id']

        # Create main sections
        sections = [
            "00. Project Overview",
            "01. Initiation",
            "02. Planning",
            "03. Execution",
            "04. Monitoring & Control",
            "05. Closure",
            "80. Integration & APIs",
            "90. Technical Documentation"
        ]

        for section in sections:
            section_page = self.create_confluence_page({
                "type": "page",
                "title": section,
                "space": {"key": self.space_key},
                "ancestors": [{"id": root_id}],
                "body": {
                    "storage": {
                        "value": f"<h1>{section}</h1>",
                        "representation": "storage"
                    }
                }
            })
            time.sleep(0.5)

        print("\n✓ Confluence structure created successfully")

    def save_summary(self):
        """Save automation summary to file"""
        summary_file = '/Users/hoangdat/Documents/2025/1. MSE19/99. Luận văn tốt nghiệp/lang-stack/automation/automation_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.created_items, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Summary saved to: {summary_file}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("EAIO PROJECT AUTOMATION SCRIPT")
    print("="*80 + "\n")

    # Configuration
    JIRA_URL = "https://fistdat.atlassian.net"
    CONFLUENCE_URL = "https://fistdat.atlassian.net/wiki"

    # Get credentials from environment variables or prompt
    email = os.getenv('ATLASSIAN_EMAIL')
    api_token = os.getenv('ATLASSIAN_API_TOKEN')

    if not email or not api_token:
        print("Please set environment variables:")
        print("  export ATLASSIAN_EMAIL='your-email@example.com'")
        print("  export ATLASSIAN_API_TOKEN='your-api-token'")
        print("\nOr create a .env file with:")
        print("  ATLASSIAN_EMAIL=your-email@example.com")
        print("  ATLASSIAN_API_TOKEN=your-api-token")
        return

    # Create automation instance
    automation = AtlassianAutomation(JIRA_URL, CONFLUENCE_URL, email, api_token)

    # Run automation
    automation.create_eaio_project_structure()


if __name__ == "__main__":
    main()
