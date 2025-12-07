#!/usr/bin/env python3
"""
EAIO Jira Automation Runner
Non-interactive mode to create all sprints
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import automation
from eaio_jira_automation import EAIOJiraAutomation

def main():
    # Configuration
    base_url = os.getenv('ATLASSIAN_URL')
    email = os.getenv('ATLASSIAN_EMAIL')
    api_token = os.getenv('ATLASSIAN_API_TOKEN')
    project_key = os.getenv('DEFAULT_PROJECT', 'SMMG6')

    if not all([base_url, email, api_token]):
        print("❌ Missing required environment variables")
        print("   Set: ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN")
        sys.exit(1)

    print(f"🚀 Starting EAIO Jira Automation")
    print(f"📁 Project: {project_key}")
    print(f"🌐 URL: {base_url}")
    print(f"👤 Email: {email}")
    print()

    # Initialize automation
    automation = EAIOJiraAutomation(
        jira_url=base_url,
        email=email,
        api_token=api_token,
        project_key=project_key
    )

    # Test connection
    print("🔍 Testing connection...")
    if not automation.jira_client.test_connection():
        print("❌ Connection failed")
        sys.exit(1)

    # Test project access
    print(f"🔍 Testing access to project {project_key}...")
    if not automation.jira_client.test_project_access(project_key):
        print(f"❌ No access to project {project_key}")
        sys.exit(1)

    # Process all sprints using built-in method
    print("\n📊 Processing all sprint files...")
    asyncio.run(automation.process_all_sprints("sprints"))

    print(f"\n{'='*60}")
    print("🎉 EAIO Jira Automation Completed!")
    print(f"{'='*60}")
    print(f"📊 Check your project at: {base_url}/jira/software/projects/{project_key}")

if __name__ == "__main__":
    main()
