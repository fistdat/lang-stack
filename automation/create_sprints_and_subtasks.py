#!/usr/bin/env python3
"""
Complete EAIO Jira & Confluence Automation
Step 2: Create Sprints, Subtasks, Confluence Pages, and Mappings
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class EAIOCompleteAutomation:
    def __init__(self):
        self.base_url = os.getenv('ATLASSIAN_URL')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.project_key = os.getenv('DEFAULT_PROJECT', 'SMMG6')
        self.space_key = os.getenv('CONFLUENCE_SPACE', 'S')

        self.auth = (self.email, self.api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Load existing automation summary
        self.load_existing_items()

    def load_existing_items(self):
        """Load existing epics and stories from automation_summary.json"""
        summary_file = Path('automation_summary.json')
        if summary_file.exists():
            with open(summary_file) as f:
                self.existing = json.load(f)
        else:
            self.existing = {'epics': {}, 'user_stories': {}, 'tasks': {}, 'sprints': {}}

    def get_board_id(self) -> Optional[int]:
        """Get the board ID for the project"""
        url = f"{self.base_url}/rest/agile/1.0/board?projectKeyOrId={self.project_key}"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            boards = response.json()
            if boards.get('values'):
                board_id = boards['values'][0]['id']
                print(f"✅ Found board ID: {board_id}")
                return board_id
        except Exception as e:
            print(f"❌ Error getting board: {e}")
        return None

    def create_sprint(self, board_id: int, sprint_data: Dict) -> Optional[Dict]:
        """Create a sprint in Jira"""
        url = f"{self.base_url}/rest/agile/1.0/sprint"

        payload = {
            "name": sprint_data['name'],
            "startDate": sprint_data['startDate'],
            "endDate": sprint_data['endDate'],
            "originBoardId": board_id
        }

        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Created Sprint: {sprint_data['name']} (ID: {result['id']})")
            return result
        except Exception as e:
            print(f"❌ Error creating sprint {sprint_data['name']}: {e}")
            return None

    def create_all_sprints(self):
        """Create all 9 sprints"""
        print("\n" + "="*60)
        print("STEP 1: CREATING SPRINTS")
        print("="*60 + "\n")

        board_id = self.get_board_id()
        if not board_id:
            print("❌ Cannot create sprints without board ID")
            return

        # Define sprints with 2-week duration each
        start_date = datetime.now()
        sprints_definition = [
            ("Sprint 0: EAIO - Project Initiation (26pts)", 0, 26),
            ("Sprint 1: EAIO - Infrastructure (34pts)", 1, 34),
            ("Sprint 2: EAIO - Data Integration (34pts)", 2, 34),
            ("Sprint 3: EAIO - Core Agents 1 (34pts)", 3, 34),
            ("Sprint 4: EAIO - Core Agents 2 (42pts)", 4, 42),
            ("Sprint 5: EAIO - Control & Validation (39pts)", 5, 39),
            ("Sprint 6: EAIO - UI & Experience (42pts)", 6, 42),
            ("Sprint 7: EAIO - Observability (39pts)", 7, 39),
            ("Sprint 8: EAIO - Testing & Deployment (47pts)", 8, 47),
        ]

        created_sprints = {}
        for name, sprint_num, points in sprints_definition:
            sprint_start = start_date + timedelta(weeks=sprint_num*2)
            sprint_end = sprint_start + timedelta(days=13, hours=23, minutes=59)

            sprint_data = {
                'name': name,
                'startDate': sprint_start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'endDate': sprint_end.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }

            result = self.create_sprint(board_id, sprint_data)
            if result:
                created_sprints[f"sprint_{sprint_num}"] = result

        # Save sprint IDs
        self.existing['sprints'] = created_sprints
        self.save_summary()

        print(f"\n✅ Created {len(created_sprints)} sprints successfully!")
        return created_sprints

    def add_issue_to_sprint(self, issue_key: str, sprint_id: int):
        """Add an issue to a sprint"""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        payload = {"issues": [issue_key]}

        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            print(f"  ✓ Added {issue_key} to sprint")
            return True
        except Exception as e:
            print(f"  ✗ Error adding {issue_key} to sprint: {e}")
            return False

    def create_subtask(self, parent_key: str, summary: str, description: str = "") -> Optional[Dict]:
        """Create a subtask under a user story"""
        url = f"{self.base_url}/rest/api/3/issue"

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "parent": {"key": parent_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{
                            "type": "text",
                            "text": description or summary
                        }]
                    }]
                },
                "issuetype": {"name": "Subtask"}
            }
        }

        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            print(f"    ✓ Created subtask: {summary} ({result['key']})")
            return result
        except Exception as e:
            print(f"    ✗ Error creating subtask '{summary}': {e}")
            return None

    def create_all_subtasks(self):
        """Create all subtasks based on EAIO Agile Plan"""
        print("\n" + "="*60)
        print("STEP 2: CREATING SUBTASKS")
        print("="*60 + "\n")

        # Define all subtasks for each user story
        subtasks_map = {
            'SMMG6-27': [  # US-001: Setup Development Environment
                "Task 1.1: Cài đặt Docker Desktop và configure daemon",
                "Task 1.2: Setup Git repository với branching strategy",
                "Task 1.3: Configure VS Code với extensions",
                "Task 1.4: Setup Docker Hub account và test push/pull"
            ],
            'SMMG6-28': [  # US-002: Stakeholder Requirements Analysis
                "Task 2.1: Conduct interviews với 3 stakeholder groups",
                "Task 2.2: Tạo Requirements Traceability Matrix",
                "Task 2.3: Document functional requirements (Tables 1-5)",
                "Task 2.4: Define non-functional requirements",
                "Task 2.5: Create acceptance criteria cho từng requirement"
            ],
            'SMMG6-29': [  # US-003: Initial Architecture Design
                "Task 3.1: Design Lang Stack architecture (Figure 1)",
                "Task 3.2: Create technology decision matrix",
                "Task 3.3: Document infrastructure requirements",
                "Task 3.4: Risk assessment cho architecture",
                "Task 3.5: Architecture review presentation"
            ],
            'SMMG6-30': [  # US-004: Docker Compose Infrastructure
                "Task 4.1: Create docker-compose.yml với 8+ services",
                "Task 4.2: Configure Langflow container (port 7860)",
                "Task 4.3: Configure Langfuse stack (web, worker, DB)",
                "Task 4.4: Setup service networking và dependencies",
                "Task 4.5: Create health check endpoints",
                "Task 4.6: Test full stack deployment end-to-end"
            ],
            'SMMG6-31': [  # US-005: Database Schema Implementation
                "Task 5.1: Create buildings table với indexes",
                "Task 5.2: Create energy_meters table",
                "Task 5.3: Setup TimescaleDB extension",
                "Task 5.4: Create weather_data hypertable",
                "Task 5.5: Create energy_analytics table",
                "Task 5.6: Create ERD (Figure 9)",
                "Task 5.7: Write database migration scripts"
            ],
            'SMMG6-32': [  # US-006: Langfuse Integration Testing
                "Task 6.1: Configure Langfuse API keys",
                "Task 6.2: Test automated trace collection",
                "Task 6.3: Create sample traces from Langflow",
                "Task 6.4: Verify traces in Langfuse UI",
                "Task 6.5: Setup monitoring dashboards",
                "Task 6.6: Test trace persistence và retrieval"
            ],
            'SMMG6-34': [  # US-007: BDG2 Dataset ETL Pipeline
                "Task 7.1: Download BDG2 dataset (53.6M records)",
                "Task 7.2: Analyze dataset structure",
                "Task 7.3: Create ETL pipeline cho buildings",
                "Task 7.4: Create ETL pipeline cho meter readings",
                "Task 7.5: Create ETL pipeline cho weather data",
                "Task 7.6: Data quality validation",
                "Task 7.7: Performance optimization"
            ],
            'SMMG6-35': [  # US-008: Data Preprocessing & Analytics Setup
                "Task 8.1: Calculate baseline metrics (EUI, ENERGY STAR)",
                "Task 8.2: Create aggregated views",
                "Task 8.3: Create materialized views",
                "Task 8.4: Setup continuous aggregates (TimescaleDB)",
                "Task 8.5: Create indexes for analytics queries",
                "Task 8.6: Generate test datasets",
                "Task 8.7: Benchmark query performance"
            ],
            'SMMG6-37': [  # US-009: Energy Data Intelligence Agent
                "Task 9.1: Design Langflow workflow architecture",
                "Task 9.2: Integrate Granite TTM foundation model",
                "Task 9.3: Implement anomaly detection (IQR, Z-score)",
                "Task 9.4: Create SQL query generation",
                "Task 9.5: Implement pattern analysis",
                "Task 9.6: Integrate Langfuse tracing",
                "Task 9.7: Create comprehensive test cases"
            ],
            'SMMG6-38': [  # US-010: Weather Intelligence Agent
                "Task 10.1: Setup AccuWeather API integration",
                "Task 10.2: Implement location-based weather retrieval",
                "Task 10.3: Create weather-energy correlation analysis",
                "Task 10.4: Implement degree day calculations (HDD/CDD)",
                "Task 10.5: Build seasonal pattern recognition",
                "Task 10.6: Create Langflow workflow",
                "Task 10.7: Setup monitoring and alerting"
            ],
            'SMMG6-39': [  # US-011: Optimization Strategy Agent
                "Task 11.1: Design ROI calculation framework (NPV, IRR)",
                "Task 11.2: Integrate GRPO reinforcement learning",
                "Task 11.3: Create investment prioritization algorithm",
                "Task 11.4: Implement ENERGY STAR certification pathway",
                "Task 11.5: Build carbon footprint calculator",
                "Task 11.6: Create load shifting optimizer",
                "Task 11.7: Risk assessment framework"
            ],
            'SMMG6-40': [  # US-012: Forecast Intelligence Agent
                "Task 12.1: Implement time-series forecasting (ARIMA, Prophet)",
                "Task 12.2: Create long-term energy forecasting",
                "Task 12.3: Build equipment failure prediction",
                "Task 12.4: Implement peak demand forecasting",
                "Task 12.5: Create renewable integration assessment",
                "Task 12.6: Build ensemble validation framework",
                "Task 12.7: Implement Langflow workflow"
            ],
            'SMMG6-41': [  # US-013: System Control Agent
                "Task 13.1: Design HVAC optimization logic",
                "Task 13.2: Implement setpoint management",
                "Task 13.3: Create zone-based control strategies",
                "Task 13.4: Physics-informed validation",
                "Task 13.5: Build BMS integration framework",
                "Task 13.6: Implement optimal control strategies"
            ],
            'SMMG6-42': [  # US-014: Validator Agent
                "Task 14.1: Create data quality validation framework",
                "Task 14.2: Implement compliance verification (ASHRAE, ISO)",
                "Task 14.3: Build safety validation engine",
                "Task 14.4: Create error detection mechanisms",
                "Task 14.5: Implement recommendation validation"
            ],
            'SMMG6-43': [  # US-015: Multi-Agent Orchestration
                "Task 15.1: Design orchestration workflows in Langflow",
                "Task 15.2: Implement conditional routing logic",
                "Task 15.3: Create state management system",
                "Task 15.4: Build agent handoff mechanisms",
                "Task 15.5: Setup performance monitoring"
            ],
            'SMMG6-45': [  # US-016: Natural Language Interface
                "Task 16.1: Design conversation flow architecture",
                "Task 16.2: Implement query processing pipeline",
                "Task 16.3: Create multi-turn conversation management",
                "Task 16.4: Build context preservation mechanism",
                "Task 16.5: Implement query routing logic",
                "Task 16.6: Integrate all 6 agents",
                "Task 16.7: Create response generation system"
            ],
            'SMMG6-46': [  # US-017: Responsive Web Application
                "Task 17.1: Design UI/UX for 3 stakeholder types",
                "Task 17.2: Implement React components",
                "Task 17.3: Create role-based access control",
                "Task 17.4: Build real-time monitoring displays",
                "Task 17.5: Integrate Langflow API endpoints",
                "Task 17.6: Implement data visualization (Recharts)",
                "Task 17.7: Create responsive layouts"
            ],
            'SMMG6-48': [  # US-018: Comprehensive Tracing & Monitoring
                "Task 18.1: Setup distributed tracing",
                "Task 18.2: Configure session tracking",
                "Task 18.3: Implement cost tracking dashboards",
                "Task 18.4: Create latency monitoring (P50, P95, P99)",
                "Task 18.5: Setup environment management",
                "Task 18.6: Create comprehensive monitoring dashboards"
            ],
            'SMMG6-49': [  # US-019: Automated Quality Evaluation
                "Task 19.1: Configure 8 evaluators with thresholds",
                "Task 19.2: Setup scoring threshold system",
                "Task 19.3: Implement automated scoring pipeline",
                "Task 19.4: Create evaluation dashboards",
                "Task 19.5: Setup alerting system"
            ],
            'SMMG6-50': [  # US-020: System Performance Optimization
                "Task 20.1: Database query optimization",
                "Task 20.2: Implement caching strategy (Redis)",
                "Task 20.3: Conduct load testing (100 users)",
                "Task 20.4: Perform bottleneck analysis",
                "Task 20.5: Response time optimization"
            ],
            'SMMG6-52': [  # US-021: Testing Suite
                "Task 21.1: Unit testing all agents (≥80% coverage)",
                "Task 21.2: Integration testing workflows",
                "Task 21.3: End-to-end testing scenarios",
                "Task 21.4: Performance testing with full dataset",
                "Task 21.5: Security testing (OWASP Top 10)"
            ],
            'SMMG6-53': [  # US-022: Complete Documentation
                "Task 22.1: Technical documentation",
                "Task 22.2: User manuals for 3 stakeholder types",
                "Task 22.3: API documentation (Swagger/OpenAPI)",
                "Task 22.4: Deployment guides",
                "Task 22.5: Thesis finalization"
            ],
            'SMMG6-54': [  # US-023: Go-Live
                "Task 23.1: Production environment setup",
                "Task 23.2: Data migration to production",
                "Task 23.3: Monitoring configuration",
                "Task 23.4: Backup & disaster recovery",
                "Task 23.5: Go-live execution và training"
            ]
        }

        created_subtasks = {}
        total_created = 0

        for parent_key, subtasks in subtasks_map.items():
            print(f"\n📝 Creating subtasks for {parent_key}:")
            for subtask in subtasks:
                result = self.create_subtask(parent_key, subtask)
                if result:
                    created_subtasks[result['key']] = {
                        'parent': parent_key,
                        'summary': subtask
                    }
                    total_created += 1

        self.existing['tasks'] = created_subtasks
        self.save_summary()

        print(f"\n✅ Created {total_created} subtasks successfully!")
        return created_subtasks

    def save_summary(self):
        """Save automation summary"""
        with open('automation_summary.json', 'w') as f:
            json.dump(self.existing, f, indent=2)

    def run_complete_automation(self):
        """Run all automation steps"""
        print("\n" + "="*80)
        print("EAIO COMPLETE AUTOMATION - PHASE 2")
        print("="*80 + "\n")

        # Step 1: Create Sprints
        sprints = self.create_all_sprints()

        # Step 2: Create Subtasks
        subtasks = self.create_all_subtasks()

        print("\n" + "="*80)
        print("AUTOMATION COMPLETED!")
        print("="*80)
        print(f"\n✅ Sprints created: {len(sprints) if sprints else 0}")
        print(f"✅ Subtasks created: {len(subtasks) if subtasks else 0}")
        print(f"\n📊 Check your project: {self.base_url}/jira/software/projects/{self.project_key}")


def main():
    automation = EAIOCompleteAutomation()
    automation.run_complete_automation()


if __name__ == "__main__":
    main()
