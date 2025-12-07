# EAIO Jira Automation Guide

**Interactive automation tool for creating EAIO project tasks and epics in Jira**
**✨ Now supports multiple Jira projects!**

## 📋 Overview

The EAIO Jira Automation system provides an interactive command-line interface to create and manage project tasks across 10 sprints. It supports full customization of epics, tasks, and project metadata before creation, with the ability to deploy to multiple Jira projects.

### ✨ Key Features

- **Interactive Sprint Selection**: Choose which sprints to process
- **Multi-Project Support**: Deploy to SCRUM, SMMG6, or other configured projects
- **Full Customization**: Modify epics, tasks, assignees, and story points
- **Validation & Preview**: Review what will be created before execution
- **Rich UI**: Beautiful command-line interface with tables and progress bars
- **Error Handling**: Comprehensive validation and error reporting
- **MCP Integration**: Direct integration with Jira REST API

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Navigate to automation directory
cd "jira automation"

# Install dependencies
pip3 install -r requirements.txt

# Set up environment variables (if not using .env file)
export ATLASSIAN_URL="https://fistdat.atlassian.net"
export ATLASSIAN_EMAIL="fistdat@gmail.com"
export ATLASSIAN_API_TOKEN="your_api_token_here"
```

### 2. Test Multi-Project Access
```bash
# Run multi-project demo to verify access
python3 multi_project_demo.py
```

### 3. Run Interactive Automation
```bash
# Start the interactive automation
python3 run_automation.py
```

---

## 🏢 Multi-Project Configuration

### Available Projects

The automation supports multiple Jira projects with predefined configurations:

| Project Key | Project Name | Description | Board ID |
|-------------|--------------|-------------|----------|
| **SCRUM** | EAIO - Energy AI Optimizer | Main EAIO development project | 1 |
| **SMMG6** | EAIO - Secondary Development | Secondary EAIO development project | 34 |

### Project URLs
- **SCRUM**: https://fistdat.atlassian.net/jira/software/projects/SCRUM/boards/1
- **SMMG6**: https://fistdat.atlassian.net/jira/software/projects/SMMG6/boards/34

### Adding New Projects

To add a new project, update the `PROJECT_CONFIGS` in `eaio_jira_automation.py`:

```python
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
    ),
    "YOUR_PROJECT": JiraProjectConfig(
        key="YOUR_PROJECT",
        name="Your Project Name",
        description="Your project description",
        base_url="https://fistdat.atlassian.net",
        board_id="your_board_id"
    )
}
```

---

## 🎯 Interactive Workflow

### Step 1: Connection & Project Selection
```
🎯 EAIO Interactive Jira Automation
============================================================
🔧 Configuration:
   Jira URL: https://fistdat.atlassian.net
   Email: fistdat@gmail.com
   Project: SCRUM

🔍 Testing Jira connection...
✅ Connected as: fistdat
✅ Jira connection successful

🏢 Project Selection
📋 Available Jira Projects
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Key   ┃ Project Name                 ┃ Description                     ┃ Board ID ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ SCRUM │ EAIO - Energy AI Optimizer   │ Main EAIO development project   │ 1        │
│ SMMG6 │ EAIO - Secondary Development │ Secondary EAIO development      │ 34       │
└───────┴──────────────────────────────┴─────────────────────────────────┴──────────┘

📌 Current project: SCRUM
Change project? [y/n] (n): y
Select project [SCRUM/SMMG6] (SCRUM): SMMG6

🔍 Testing access to project SMMG6...
✅ Access confirmed for project: SWM501-MAY25-MSE19-G6
🔄 Switched to project: EAIO - Secondary Development (SMMG6)
✅ Successfully switched to project: SMMG6
```

### Step 2: Sprint Selection & Customization
```
📋 Parsing sprint files...
  ✅ Parsed: sprint_0_project_foundation.md (3 epics)
  ✅ Parsed: sprint_1_database_foundation.md (2 epics)
  ...

🎯 Sprint Selection
                        📋 Available Sprints                         
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Number ┃ Sprint Name                              ┃ Epics ┃ Tasks ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ 0      │ Project Foundation & Planning            │   3   │  24   │
│ 1      │ Database Foundation                      │   2   │   6   │
│ 2      │ Vector Database & Data Integration       │   2   │   6   │
└────────┴──────────────────────────────────────────┴───────┴───────┘

Process all sprints? [y/n] (y): n
💡 Enter sprint numbers separated by commas (e.g., 1,3,5)
Select sprints (0,1,2,3,4,5,6,7,8,9,10): 0

🎨 Customize sprints before creation? [y/n] (n): n
```

### Step 3: Creation Summary & Execution
```
📊 Creation Summary
      📋 Items to be Created in Jira       
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Sprint   ┃ Epics ┃ Tasks ┃ Story Points ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ Sprint 0 │   3   │  24   │     218      │
│ TOTAL    │   3   │  24   │     218      │
└──────────┴───────┴───────┴──────────────┘

🚀 Proceed with creating 3 epics and 24 tasks? [y/n] (y): y

🚀 Starting automation...
📋 Processing: Sprint 0
📝 Sprint 0: Project Foundation & Planning (create manually in Jira)

  📁 Creating Epic: Project Overview & Charter
  ✅ Created Epic: SMMG6-001 - Project Overview & Charter
    ✅ Created Task: SMMG6-002 - Create EAIO Project Charter
    ✅ Created Task: SMMG6-003 - Develop Stakeholder Registry & Analysis
    ...
```

### Step 4: Validation & Results
```
🔍 Validating creation results...
============================================================
📊 EAIO Jira Automation Validation Report
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ Metric            ┃ Value   ┃ Status  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ Sprints Processed │ 1       │   ✅    │
│ Epics Created     │ 3/3     │ 100.0%  │
│ Tasks Created     │ 24/24   │ 100.0%  │
│ Tasks Failed      │ 0       │   ✅    │
│ Overall Status    │ SUCCESS │ SUCCESS │
└───────────────────┴─────────┴─────────┘

🎉 All tasks and epics created successfully!
✅ Ready to proceed with development work
```

---

## 🛠️ Advanced Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Jira Configuration
ATLASSIAN_URL=https://fistdat.atlassian.net
ATLASSIAN_EMAIL=fistdat@gmail.com
ATLASSIAN_API_TOKEN=your_api_token_here

# Project Configuration
JIRA_PROJECT_KEY=SCRUM
SPRINTS_DIRECTORY=../.cursor/tasks/sprints

# Performance Configuration
RATE_LIMIT_DELAY=0.5
```

### Project Switching via Code

```python
from eaio_jira_automation import EAIOJiraAutomation

# Initialize with default project
automation = EAIOJiraAutomation(
    jira_url="https://fistdat.atlassian.net",
    email="fistdat@gmail.com", 
    api_token="your_token",
    project_key="SCRUM"
)

# Switch to different project
automation.switch_project("SMMG6")

# Test access to project
automation.test_project_access("SMMG6")

# Get available projects
projects = automation.get_available_projects()
for key, config in projects.items():
    print(f"{key}: {config.name}")
```

---

## 📊 Sprint Structure Support

The automation supports all EAIO sprints with proper epic/task parsing:

### Sprint 0: Project Foundation & Planning (24 tasks)
- **Project**: Foundation setup, stakeholder alignment
- **Epics**: 3 epics covering project overview, initiation, and planning
- **Target Project**: SCRUM or SMMG6

### Sprint 1-10: Implementation Sprints (126+ tasks)
- **Project**: Full EAIO system implementation
- **Epics**: 36 total epics across all sprints
- **Architecture**: 6-layer architecture implementation

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Project Access Denied
```
❌ No access to project SMMG6: {"errorMessages":["You do not have permission to see this project."]}
```
**Solution**: Verify project permissions in Jira admin settings

#### 2. API Token Issues
```
❌ Connection failed: {"errorMessages":["You do not have permission to access this resource"]}
```
**Solution**: Regenerate API token in Atlassian account settings

#### 3. Sprint File Parsing Errors
```
❌ Failed to parse sprint_0_project_foundation.md: Epic not found
```
**Solution**: Verify sprint file format matches expected structure

### Multi-Project Validation

Test access to all configured projects:

```bash
# Run project access test
python3 multi_project_demo.py

# Expected output:
📌 Testing SCRUM:
✅ Access confirmed for project: Scrum Project Template

📌 Testing SMMG6: 
✅ Access confirmed for project: SWM501-MAY25-MSE19-G6
```

---

## 🚀 Production Deployment

### Batch Processing Multiple Projects

Create scripts for automated deployment across projects:

```bash
#!/bin/bash
# deploy_all_projects.sh

echo "🚀 Deploying EAIO Sprint 0 to all projects..."

# Deploy to SCRUM project
export JIRA_PROJECT_KEY=SCRUM
python3 run_automation.py --batch --sprint=0

# Deploy to SMMG6 project  
export JIRA_PROJECT_KEY=SMMG6
python3 run_automation.py --batch --sprint=0

echo "✅ Deployment completed to all projects"
```

### CI/CD Integration

```yaml
# .github/workflows/jira-automation.yml
name: EAIO Jira Automation

on:
  workflow_dispatch:
    inputs:
      project_key:
        description: 'Target Jira Project'
        required: true
        default: 'SCRUM'
        type: choice
        options:
        - SCRUM
        - SMMG6
      sprint_number:
        description: 'Sprint Number'
        required: true
        default: '0'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r jira automation/requirements.txt
    - name: Deploy to Jira
      env:
        ATLASSIAN_URL: ${{ secrets.ATLASSIAN_URL }}
        ATLASSIAN_EMAIL: ${{ secrets.ATLASSIAN_EMAIL }}
        ATLASSIAN_API_TOKEN: ${{ secrets.ATLASSIAN_API_TOKEN }}
        JIRA_PROJECT_KEY: ${{ inputs.project_key }}
      run: |
        cd "jira automation"
        python3 run_automation.py --batch --sprint=${{ inputs.sprint_number }}
```

---

## 📈 Next Steps

1. **Test Multi-Project Access**: Run `multi_project_demo.py`
2. **Deploy Sprint 0**: Use `run_automation.py` to create foundation tasks
3. **Deploy Additional Sprints**: Select and deploy sprints 1-10 as needed
4. **Monitor Progress**: Use Jira boards to track task completion
5. **Scale to Additional Projects**: Add new project configurations as needed

The automation system is now fully configured for multi-project deployment across the EAIO ecosystem! 🎉
