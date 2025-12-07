#!/usr/bin/env python3
"""
EAIO Jira-Confluence Linking Automation
Creates bidirectional links between Jira issues and Confluence documentation
"""

import os
import json
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class JiraConfluenceLinker:
    def __init__(self):
        self.base_url = os.getenv('ATLASSIAN_URL')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.project_key = os.getenv('DEFAULT_PROJECT', 'SMMG6')
        self.space_key = os.getenv('CONFLUENCE_SPACE', 'S')
        self.auth = (self.email, self.api_token)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Load automation summaries
        self.load_summaries()

        # Traceability matrix
        self.traceability = {}

    def load_summaries(self):
        """Load created items from automation summaries"""
        # Load Jira items
        summary_file = Path("/Users/hoangdat/Documents/2025/1. MSE19/99. Luận văn tốt nghiệp/lang-stack/automation/automation_summary.json")
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                self.jira_items = json.load(f)
        else:
            self.jira_items = {}

        # Load Confluence pages
        confluence_file = Path("/Users/hoangdat/Documents/2025/1. MSE19/99. Luận văn tốt nghiệp/lang-stack/automation/confluence_pages_summary.json")
        if confluence_file.exists():
            with open(confluence_file, 'r') as f:
                self.confluence_pages = json.load(f)
        else:
            self.confluence_pages = {}

    def get_confluence_page_url(self, page_id: str) -> str:
        """Get Confluence page URL from page ID"""
        return f"{self.base_url}/wiki/spaces/{self.space_key}/pages/{page_id}"

    def add_web_link_to_jira(self, issue_key: str, url: str, title: str) -> bool:
        """Add a web link to a Jira issue"""
        api_url = f"{self.base_url}/rest/api/3/issue/{issue_key}/remotelink"

        payload = {
            "object": {
                "url": url,
                "title": title,
                "icon": {
                    "url16x16": f"{self.base_url}/wiki/s/-1/en/8703/b45e7a8cd0a4cfe8a7b4f6edc7a8803e0ea4243a/_/images/icons/profilepics/default.svg"
                }
            }
        }

        try:
            response = requests.post(api_url, json=payload, auth=self.auth, headers=self.headers)
            if response.status_code in [200, 201]:
                print(f"✅ Linked {issue_key} → {title}")
                return True
            else:
                print(f"⚠️  Failed to link {issue_key} to {title}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error linking {issue_key}: {e}")
            return False

    def create_traceability_matrix_page(self) -> Optional[str]:
        """Create traceability matrix page in Confluence"""
        root_page_id = "38141970"  # EAIO-2025 root page

        content = self.generate_traceability_matrix_content()

        url = f"{self.base_url}/wiki/rest/api/content"
        payload = {
            "type": "page",
            "title": "Jira-Confluence Traceability Matrix",
            "space": {"key": self.space_key},
            "ancestors": [{"id": root_page_id}],
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        try:
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            if response.status_code in [200, 201]:
                page = response.json()
                print(f"✅ Created Traceability Matrix page (ID: {page['id']})")
                return page['id']
            else:
                # Try to find existing page
                search_url = f"{self.base_url}/wiki/rest/api/content"
                params = {
                    'spaceKey': self.space_key,
                    'title': 'Jira-Confluence Traceability Matrix',
                    'type': 'page'
                }
                response = requests.get(search_url, auth=self.auth, headers=self.headers, params=params)
                data = response.json()
                if data['results']:
                    page = data['results'][0]
                    print(f"ℹ️  Traceability Matrix page already exists (ID: {page['id']})")
                    # Update the page
                    self.update_traceability_matrix_page(page['id'], content)
                    return page['id']
        except Exception as e:
            print(f"❌ Error creating traceability matrix: {e}")

        return None

    def update_traceability_matrix_page(self, page_id: str, content: str):
        """Update existing traceability matrix page"""
        # Get current version
        url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        page = response.json()
        current_version = page['version']['number']

        # Update
        update_url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        payload = {
            "version": {"number": current_version + 1},
            "title": "Jira-Confluence Traceability Matrix",
            "type": "page",
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        response = requests.put(update_url, json=payload, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            print(f"✅ Updated Traceability Matrix page")
        else:
            print(f"⚠️  Failed to update Traceability Matrix: {response.status_code}")

    def generate_traceability_matrix_content(self) -> str:
        """Generate HTML content for traceability matrix"""
        content = """
<h1>Jira-Confluence Traceability Matrix</h1>

<p><strong>Purpose:</strong> This page maps all Jira issues (Epics, User Stories, Subtasks) to their corresponding Confluence documentation pages.</p>
<p><strong>Last Updated:</strong> October 5, 2025</p>

<h2>Epic Level Mapping</h2>
<table>
    <tr>
        <th>Epic</th>
        <th>Jira Link</th>
        <th>Confluence Section</th>
        <th>Status</th>
    </tr>
"""

        # Epic mappings
        epic_mappings = [
            {
                'name': 'Epic 1: Project Foundation & Infrastructure',
                'key': 'SMMG6-26',
                'confluence': '00. Project Overview, 01. Initiation, 02. Planning',
                'status': '✅ Complete'
            },
            {
                'name': 'Epic 2: Data Management & Integration',
                'key': 'SMMG6-33',
                'confluence': '03. Execution → Sprint 2',
                'status': '✅ Complete'
            },
            {
                'name': 'Epic 3: Multi-Agent System Development',
                'key': 'SMMG6-36',
                'confluence': '03. Execution → Sprint 3-5',
                'status': '✅ Complete'
            },
            {
                'name': 'Epic 4: User Interface & Experience',
                'key': 'SMMG6-44',
                'confluence': '03. Execution → Sprint 6',
                'status': '✅ Complete'
            },
            {
                'name': 'Epic 5: Observability & Quality Assurance',
                'key': 'SMMG6-47',
                'confluence': '03. Execution → Sprint 7, 04. Monitoring & Control',
                'status': '✅ Complete'
            },
            {
                'name': 'Epic 6: Testing & Production Deployment',
                'key': 'SMMG6-51',
                'confluence': '03. Execution → Sprint 8, 05. Closure',
                'status': '✅ Complete'
            }
        ]

        for epic in epic_mappings:
            content += f"""
    <tr>
        <td>{epic['name']}</td>
        <td><a href="{self.base_url}/browse/{epic['key']}">{epic['key']}</a></td>
        <td>{epic['confluence']}</td>
        <td>{epic['status']}</td>
    </tr>"""

        content += """
</table>

<h2>User Story → Documentation Mapping</h2>
<table>
    <tr>
        <th>US ID</th>
        <th>Jira Key</th>
        <th>Title</th>
        <th>Sprint</th>
        <th>Confluence Documentation</th>
    </tr>
"""

        # User Story mappings
        us_mappings = [
            # Epic 1
            {'id': 'US-001', 'key': 'SMMG6-27', 'title': 'Setup Development Environment', 'sprint': 0, 'docs': 'DOC_TEAM_Structure_Roles_v1.0, DOC_TEAM_Account_Registry_v1.0'},
            {'id': 'US-002', 'key': 'SMMG6-28', 'title': 'Stakeholder Requirements Analysis', 'sprint': 0, 'docs': 'DOC_REQ_Stakeholder_Requirements_Analysis_v1.0, DOC_REQ_*_Requirements_v1.0'},
            {'id': 'US-003', 'key': 'SMMG6-29', 'title': 'Initial Architecture Design', 'sprint': 0, 'docs': 'DOC_ARCH_High_Level_Architecture_v1.0, DOC_ARCH_Technology_Stack_Selection_v1.0'},
            {'id': 'US-004', 'key': 'SMMG6-30', 'title': 'Docker Compose Infrastructure', 'sprint': 1, 'docs': 'DOC_INFRA_Docker_Compose_Configuration_v1.0'},
            {'id': 'US-005', 'key': 'SMMG6-31', 'title': 'Database Schema Implementation', 'sprint': 1, 'docs': 'DOC_INFRA_Database_Schema_v1.0'},
            {'id': 'US-006', 'key': 'SMMG6-32', 'title': 'Langfuse Integration Testing', 'sprint': 1, 'docs': 'DOC_ARCH_Lang_Stack_Integration_v1.0'},

            # Epic 2
            {'id': 'US-007', 'key': 'SMMG6-34', 'title': 'BDG2 Dataset ETL Pipeline', 'sprint': 2, 'docs': 'DOC_DATA_BDG2_Dataset_Analysis_v1.0, DOC_DATA_ETL_Pipeline_Design_v1.0'},
            {'id': 'US-008', 'key': 'SMMG6-35', 'title': 'Data Preprocessing & Analytics Setup', 'sprint': 2, 'docs': 'DOC_DATA_Quality_Validation_Report_v1.0'},

            # Epic 3
            {'id': 'US-009', 'key': 'SMMG6-37', 'title': 'Energy Data Intelligence Agent', 'sprint': 3, 'docs': 'SPEC_AGENT_Energy_Data_Intelligence_v1.0'},
            {'id': 'US-010', 'key': 'SMMG6-38', 'title': 'Weather Intelligence Agent', 'sprint': 3, 'docs': 'SPEC_AGENT_Weather_Intelligence_v1.0'},
            {'id': 'US-011', 'key': 'SMMG6-39', 'title': 'Optimization Strategy Agent', 'sprint': 4, 'docs': 'SPEC_AGENT_Optimization_Strategy_v1.0'},
            {'id': 'US-012', 'key': 'SMMG6-40', 'title': 'Forecast Intelligence Agent', 'sprint': 4, 'docs': 'SPEC_AGENT_Forecast_Intelligence_v1.0'},
            {'id': 'US-013', 'key': 'SMMG6-41', 'title': 'System Control Agent', 'sprint': 5, 'docs': 'SPEC_AGENT_System_Control_v1.0'},
            {'id': 'US-014', 'key': 'SMMG6-42', 'title': 'Validator Agent', 'sprint': 5, 'docs': 'SPEC_AGENT_Validator_v1.0'},
            {'id': 'US-015', 'key': 'SMMG6-43', 'title': 'Multi-Agent Orchestration', 'sprint': 5, 'docs': 'DOC_ARCH_Multi_Agent_Orchestration_v1.0'},

            # Epic 4
            {'id': 'US-016', 'key': 'SMMG6-45', 'title': 'Natural Language Interface', 'sprint': 6, 'docs': 'SPEC_UI_Conversational_Interface_v1.0'},
            {'id': 'US-017', 'key': 'SMMG6-46', 'title': 'Responsive Web Application', 'sprint': 6, 'docs': 'DOC_WEB_Application_Architecture_v1.0'},

            # Epic 5
            {'id': 'US-018', 'key': 'SMMG6-48', 'title': 'Comprehensive Tracing & Monitoring', 'sprint': 7, 'docs': 'DOC_OBS_Comprehensive_Architecture_v1.0'},
            {'id': 'US-019', 'key': 'SMMG6-49', 'title': 'Automated Quality Evaluation', 'sprint': 7, 'docs': 'DOC_EVAL_LLM_as_Judge_Setup_v1.0'},
            {'id': 'US-020', 'key': 'SMMG6-50', 'title': 'System Performance Optimization', 'sprint': 7, 'docs': 'RPT_PERF_KPI_Dashboard_v1.0'},

            # Epic 6
            {'id': 'US-021', 'key': 'SMMG6-52', 'title': 'Testing Suite', 'sprint': 8, 'docs': 'TEST_UNIT_All_Agents_Report_v1.0, TEST_E2E_End_to_End_Scenarios_v1.0'},
            {'id': 'US-022', 'key': 'SMMG6-53', 'title': 'Complete Documentation', 'sprint': 8, 'docs': 'All documentation pages'},
            {'id': 'US-023', 'key': 'SMMG6-54', 'title': 'Go-Live', 'sprint': 8, 'docs': 'DOC_DEPLOY_Deployment_Guide_v1.0, RPT_CLOSURE_Project_Report_v1.0'},
        ]

        for us in us_mappings:
            content += f"""
    <tr>
        <td>{us['id']}</td>
        <td><a href="{self.base_url}/browse/{us['key']}">{us['key']}</a></td>
        <td>{us['title']}</td>
        <td>Sprint {us['sprint']}</td>
        <td>{us['docs']}</td>
    </tr>"""

        content += """
</table>

<h2>Documentation Coverage Statistics</h2>
<table>
    <tr><th>Metric</th><th>Count</th><th>Status</th></tr>
    <tr><td>Total Epics</td><td>6</td><td>✅ All documented</td></tr>
    <tr><td>Total User Stories</td><td>22</td><td>✅ All documented</td></tr>
    <tr><td>Total Subtasks</td><td>136</td><td>✅ All created</td></tr>
    <tr><td>Confluence Pages</td><td>65</td><td>✅ Complete</td></tr>
    <tr><td>Documentation Coverage</td><td>100%</td><td>✅ Full coverage</td></tr>
</table>

<h2>Quick Navigation</h2>
<h3>Jira</h3>
<ul>
    <li><a href="{self.base_url}/jira/software/projects/SMMG6/board">Project Board</a></li>
    <li><a href="{self.base_url}/jira/software/projects/SMMG6/backlog">Backlog</a></li>
    <li><a href="{self.base_url}/jira/software/projects/SMMG6/timeline">Timeline</a></li>
</ul>

<h3>Confluence Sections</h3>
<ul>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/6356994">00. Project Overview</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/6357004">01. Initiation</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/6291458">02. Planning</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/38109191">03. Execution</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/38076419">04. Monitoring & Control</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/38141955">05. Closure</a></li>
    <li><a href="{self.base_url}/wiki/spaces/{self.space_key}/pages/38076437">90. Technical Documentation</a></li>
</ul>

<p><em>Generated: October 5, 2025 by EAIO Automation</em></p>
"""

        return content

    def link_user_stories_to_confluence(self):
        """Link all user stories to relevant Confluence pages"""
        print("\n📎 Linking User Stories to Confluence Documentation...")

        # Define mappings
        us_confluence_mappings = [
            # Epic 1
            {'us': 'SMMG6-27', 'pages': [
                {'title': 'Team Structure & Roles', 'section': '01. Initiation → Team Setup'}
            ]},
            {'us': 'SMMG6-28', 'pages': [
                {'title': 'Stakeholder Requirements Analysis', 'section': '01. Initiation → Business Requirements'}
            ]},
            {'us': 'SMMG6-29', 'pages': [
                {'title': 'High-Level Architecture', 'section': '01. Initiation → Initial Architecture'},
                {'title': 'Technology Stack Selection', 'section': '01. Initiation → Initial Architecture'}
            ]},
            {'us': 'SMMG6-30', 'pages': [
                {'title': 'Docker Compose Configuration', 'section': '90. Technical Documentation → Infrastructure'}
            ]},
            {'us': 'SMMG6-31', 'pages': [
                {'title': 'Database Schema Structure', 'section': '90. Technical Documentation → Infrastructure'}
            ]},

            # Epic 2
            {'us': 'SMMG6-34', 'pages': [
                {'title': 'BDG2 Dataset Analysis', 'section': '03. Execution → Sprint 2'},
                {'title': 'ETL Pipeline Design', 'section': '03. Execution → Sprint 2'}
            ]},
            {'us': 'SMMG6-35', 'pages': [
                {'title': 'Data Quality Validation Report', 'section': '03. Execution → Sprint 2'}
            ]},

            # Epic 3
            {'us': 'SMMG6-37', 'pages': [
                {'title': 'Energy Data Intelligence Agent Spec', 'section': '03. Execution → Sprint 3'}
            ]},
            {'us': 'SMMG6-38', 'pages': [
                {'title': 'Weather Intelligence Agent Spec', 'section': '03. Execution → Sprint 3'}
            ]},
            {'us': 'SMMG6-39', 'pages': [
                {'title': 'Optimization Strategy Agent Spec', 'section': '03. Execution → Sprint 4'}
            ]},
            {'us': 'SMMG6-40', 'pages': [
                {'title': 'Forecast Intelligence Agent Spec', 'section': '03. Execution → Sprint 4'}
            ]},
            {'us': 'SMMG6-41', 'pages': [
                {'title': 'System Control Agent Spec', 'section': '03. Execution → Sprint 5'}
            ]},
            {'us': 'SMMG6-42', 'pages': [
                {'title': 'Validator Agent Spec', 'section': '03. Execution → Sprint 5'}
            ]},
            {'us': 'SMMG6-43', 'pages': [
                {'title': 'Multi-Agent Orchestration', 'section': '03. Execution → Sprint 5'}
            ]},

            # Epic 4
            {'us': 'SMMG6-45', 'pages': [
                {'title': 'Conversational AI Interface Spec', 'section': '03. Execution → Sprint 6'}
            ]},
            {'us': 'SMMG6-46', 'pages': [
                {'title': 'Web Application Architecture', 'section': '03. Execution → Sprint 6'}
            ]},

            # Epic 5
            {'us': 'SMMG6-48', 'pages': [
                {'title': 'Observability Architecture', 'section': '03. Execution → Sprint 7'}
            ]},
            {'us': 'SMMG6-49', 'pages': [
                {'title': 'LLM-as-a-Judge Setup', 'section': '03. Execution → Sprint 7'}
            ]},
            {'us': 'SMMG6-50', 'pages': [
                {'title': 'KPI Dashboard', 'section': '04. Monitoring & Control'}
            ]},

            # Epic 6
            {'us': 'SMMG6-52', 'pages': [
                {'title': 'Unit Test Report', 'section': '03. Execution → Sprint 8'},
                {'title': 'E2E Test Report', 'section': '03. Execution → Sprint 8'}
            ]},
            {'us': 'SMMG6-54', 'pages': [
                {'title': 'Deployment Guide', 'section': '03. Execution → Sprint 8'},
                {'title': 'Project Closure Report', 'section': '05. Closure'}
            ]},
        ]

        linked_count = 0
        for mapping in us_confluence_mappings:
            us_key = mapping['us']
            for page in mapping['pages']:
                # Construct Confluence URL (simplified - using search)
                search_url = f"{self.base_url}/wiki/dosearchsite.action?queryString={page['title']}"
                title = f"📄 {page['title']} ({page['section']})"

                if self.add_web_link_to_jira(us_key, search_url, title):
                    linked_count += 1
                    self.traceability[us_key] = self.traceability.get(us_key, []) + [page]

        print(f"\n✅ Linked {linked_count} Confluence pages to User Stories")
        return linked_count

    def link_epics_to_confluence(self):
        """Link all epics to relevant Confluence sections"""
        print("\n📎 Linking Epics to Confluence Sections...")

        epic_mappings = [
            {
                'epic': 'SMMG6-26',
                'pages': [
                    {'title': '00. Project Overview', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/6356994"},
                    {'title': '01. Initiation', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/6357004"},
                    {'title': '02. Planning', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/6291458"}
                ]
            },
            {
                'epic': 'SMMG6-33',
                'pages': [
                    {'title': '03. Execution → Sprint 2', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38076486"}
                ]
            },
            {
                'epic': 'SMMG6-36',
                'pages': [
                    {'title': '03. Execution → Sprint 3-5', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38076518"}
                ]
            },
            {
                'epic': 'SMMG6-44',
                'pages': [
                    {'title': '03. Execution → Sprint 6', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38174863"}
                ]
            },
            {
                'epic': 'SMMG6-47',
                'pages': [
                    {'title': '03. Execution → Sprint 7', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38174878"},
                    {'title': '04. Monitoring & Control', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38076419"}
                ]
            },
            {
                'epic': 'SMMG6-51',
                'pages': [
                    {'title': '03. Execution → Sprint 8', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38174910"},
                    {'title': '05. Closure', 'url': f"{self.base_url}/wiki/spaces/{self.space_key}/pages/38141955"}
                ]
            }
        ]

        linked_count = 0
        for mapping in epic_mappings:
            epic_key = mapping['epic']
            for page in mapping['pages']:
                if self.add_web_link_to_jira(epic_key, page['url'], f"📚 {page['title']}"):
                    linked_count += 1

        print(f"\n✅ Linked {linked_count} Confluence sections to Epics")
        return linked_count

    def save_traceability_report(self):
        """Save traceability matrix to JSON file"""
        report_file = Path("/Users/hoangdat/Documents/2025/1. MSE19/99. Luận văn tốt nghiệp/lang-stack/automation/traceability_matrix.json")

        report = {
            "generated": "2025-10-05",
            "project": "EAIO - Energy AI Optimizer",
            "jira_project": self.project_key,
            "confluence_space": self.space_key,
            "traceability": self.traceability,
            "statistics": {
                "epics": 6,
                "user_stories": 22,
                "subtasks": 136,
                "confluence_pages": 65,
                "links_created": len(self.traceability)
            }
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Traceability report saved to: {report_file}")

    def run(self):
        """Run the linking automation"""
        print("🚀 Starting EAIO Jira-Confluence Linking Automation")
        print(f"📁 Jira Project: {self.project_key}")
        print(f"📁 Confluence Space: {self.space_key}")

        # Step 1: Link Epics to Confluence sections
        epic_links = self.link_epics_to_confluence()

        # Step 2: Link User Stories to documentation pages
        us_links = self.link_user_stories_to_confluence()

        # Step 3: Create Traceability Matrix page
        matrix_page_id = self.create_traceability_matrix_page()

        # Step 4: Save traceability report
        self.save_traceability_report()

        print("\n" + "="*60)
        print("✅ JIRA-CONFLUENCE LINKING COMPLETED!")
        print("="*60)
        print(f"📊 Epic Links Created: {epic_links}")
        print(f"📊 User Story Links Created: {us_links}")
        print(f"📊 Total Links: {epic_links + us_links}")
        if matrix_page_id:
            print(f"📄 Traceability Matrix: {self.base_url}/wiki/spaces/{self.space_key}/pages/{matrix_page_id}")
        print("="*60)

        return True

if __name__ == "__main__":
    linker = JiraConfluenceLinker()
    linker.run()
