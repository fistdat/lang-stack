# EAIO Multi-Project Jira Automation Setup

## 🎯 Overview

EAIO Jira Automation hiện đã hỗ trợ tạo tasks và epics cho nhiều Jira projects khác nhau. Bạn có thể dễ dàng chuyển đổi giữa các projects và deploy sprints vào project mong muốn.

## 🏢 Available Projects

### Project 1: SCRUM
- **Project Key**: `SCRUM`
- **Project Name**: EAIO - Energy AI Optimizer
- **Description**: Main EAIO development project
- **Board URL**: https://fistdat.atlassian.net/jira/software/projects/SCRUM/boards/1
- **Board ID**: 1

### Project 2: SMMG6
- **Project Key**: `SMMG6`
- **Project Name**: EAIO - Secondary Development
- **Description**: Secondary EAIO development project  
- **Board URL**: https://fistdat.atlassian.net/jira/software/projects/SMMG6/boards/34
- **Board ID**: 34

## 🚀 Quick Start Guide

### 1. Test Multi-Project Access
```bash
cd "jira automation"
python3 multi_project_demo.py
```

Expected output:
```
🏢 EAIO Multi-Project Demo
============================================================
📌 Testing SCRUM:
✅ Access confirmed for project: Scrum Project Template

📌 Testing SMMG6:
✅ Access confirmed for project: SWM501-MAY25-MSE19-G6
```

### 2. Run Interactive Automation
```bash
python3 run_automation.py
```

### 3. Select Target Project
When prompted, choose your target project:
```
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

### 4. Deploy Sprints
Choose which sprints to deploy to the selected project:
```
🎯 Sprint Selection
Select sprints (0,1,2,3,4,5,6,7,8,9,10): 0,1,2

📊 Creation Summary
🚀 Proceed with creating 7 epics and 36 tasks? [y/n] (y): y
```

## 🔧 Configuration Details

### Environment Variables
```bash
# Required
ATLASSIAN_URL=https://fistdat.atlassian.net
ATLASSIAN_EMAIL=fistdat@gmail.com
ATLASSIAN_API_TOKEN=your_api_token_here

# Optional
JIRA_PROJECT_KEY=SCRUM  # Default project
SPRINTS_DIRECTORY=../.cursor/tasks/sprints
RATE_LIMIT_DELAY=0.5
```

### Project Configuration
Projects are configured in `eaio_jira_automation.py`:

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
    )
}
```

## 📊 Usage Examples

### Example 1: Deploy Sprint 0 to SCRUM Project
```bash
python3 run_automation.py
# Select: SCRUM project
# Select: Sprint 0
# Result: 3 epics, 24 tasks created in SCRUM
```

### Example 2: Deploy Multiple Sprints to SMMG6 Project
```bash
python3 run_automation.py
# Select: SMMG6 project  
# Select: Sprints 1,2,3
# Result: 7 epics, 38 tasks created in SMMG6
```

### Example 3: Programmatic Project Switching
```python
from eaio_jira_automation import EAIOJiraAutomation

automation = EAIOJiraAutomation(
    jira_url="https://fistdat.atlassian.net",
    email="fistdat@gmail.com",
    api_token="your_token",
    project_key="SCRUM"
)

# Switch to SMMG6
automation.switch_project("SMMG6")

# Deploy specific sprint
sprint = automation.parse_sprint_file("sprint_0_project_foundation.md")
await automation.process_single_sprint(sprint)
```

## 🎯 Deployment Strategy

### Recommended Approach

1. **SCRUM Project**: Deploy core foundation sprints (0, 1, 2)
   - Sprint 0: Project Foundation & Planning
   - Sprint 1: Database Foundation  
   - Sprint 2: Vector Database & Data Integration

2. **SMMG6 Project**: Deploy implementation sprints (3-10)
   - Sprint 3: LLM Infrastructure
   - Sprint 4: MCP Integration Layer
   - Sprint 5-7: Agent Framework & Frontend
   - Sprint 8-10: Integration & Production

### Parallel Development
Both projects can run simultaneously:
- SCRUM: Foundation and infrastructure
- SMMG6: Feature development and integration

## 🔍 Validation & Monitoring

### Project Access Validation
```bash
# Test access to all projects
python3 multi_project_demo.py

# Expected: ✅ for both SCRUM and SMMG6
```

### Creation Validation
After deployment, verify tasks were created:
- SCRUM: https://fistdat.atlassian.net/jira/software/projects/SCRUM/boards/1
- SMMG6: https://fistdat.atlassian.net/jira/software/projects/SMMG6/boards/34

## 🆕 Adding New Projects

To add a new project, update `PROJECT_CONFIGS`:

```python
"NEW_PROJECT": JiraProjectConfig(
    key="NEW_PROJECT",
    name="New Project Name",
    description="Project description",
    base_url="https://fistdat.atlassian.net", 
    board_id="new_board_id"
)
```

## 🎉 Success Metrics

With multi-project support, you can now:

✅ **Deploy to multiple Jira projects simultaneously**  
✅ **Separate concerns across different project contexts**  
✅ **Maintain consistent sprint structure across projects**  
✅ **Support parallel team development workflows**  
✅ **Enable project-specific customization and configuration**

## 🆘 Troubleshooting

### Issue: Project Access Denied
```
❌ No access to project SMMG6
```
**Solution**: Check Jira project permissions for your account

### Issue: Board ID Not Found
```
❌ Board URL returns 404
```
**Solution**: Verify board ID in project settings

### Issue: API Token Expired
```
❌ Connection failed: Unauthorized
```
**Solution**: Regenerate API token in Atlassian account settings

---

**🎯 Result**: EAIO automation system now supports flexible multi-project deployment across the entire Jira ecosystem! 🚀 