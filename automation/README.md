# EAIO Project Automation

Automated creation of the complete EAIO project structure in Jira and Confluence.

## Features

This automation script will create:

### Jira
- ✅ 6 Epics (Epic 1-6)
- ✅ 14 Features
- ✅ 22 User Stories with story points
- ✅ 100+ Tasks
- ✅ 9 Sprints (Sprint 0-8) with proper scheduling
- ✅ Automatic sprint assignment
- ✅ Epic linking

### Confluence
- ✅ Complete documentation structure
- ✅ Project hierarchy (00-90 folders)
- ✅ Document placeholders mapped to user stories
- ✅ Proper page relationships

### Mappings
- ✅ Jira tasks linked to Confluence documentation
- ✅ Cross-references between issues
- ✅ Traceability matrix

## Project Structure

```
EAIO Project (337 Story Points, 8 Sprints)
├── Epic 1: Project Foundation & Infrastructure (60 pts, Sprint 0-1)
│   ├── Feature 1.1: Project Initiation (26 pts)
│   │   ├── US-001: Setup Development Environment (5 pts)
│   │   ├── US-002: Stakeholder Requirements Analysis (8 pts)
│   │   └── US-003: Initial Architecture Design (13 pts)
│   └── Feature 1.2: Docker Infrastructure Deployment (34 pts)
│       ├── US-004: Docker Compose Infrastructure (13 pts)
│       ├── US-005: Database Schema Implementation (13 pts)
│       └── US-006: Langfuse Integration Testing (8 pts)
│
├── Epic 2: Data Management & Integration (34 pts, Sprint 2)
│   └── Feature 2.1: BDG2 Dataset Integration
│       ├── US-007: BDG2 Dataset ETL Pipeline (21 pts)
│       └── US-008: Data Preprocessing & Analytics Setup (13 pts)
│
├── Epic 3: Multi-Agent System Development (115 pts, Sprint 3-5)
│   ├── Feature 3.1: Energy Intelligence Agents (Sprint 3, 34 pts)
│   │   ├── US-009: Energy Data Intelligence Agent (21 pts)
│   │   └── US-010: Weather Intelligence Agent (13 pts)
│   ├── Feature 3.2: Optimization & Forecasting Agents (Sprint 4, 42 pts)
│   │   ├── US-011: Optimization Strategy Agent (21 pts)
│   │   └── US-012: Forecast Intelligence Agent (21 pts)
│   └── Feature 3.3: Control & Validation System (Sprint 5, 39 pts)
│       ├── US-013: System Control Agent (13 pts)
│       ├── US-014: Validator Agent (13 pts)
│       └── US-015: Multi-Agent Orchestration (13 pts)
│
├── Epic 4: User Interface & Experience (42 pts, Sprint 6)
│   ├── Feature 4.1: Conversational AI Interface (21 pts)
│   │   └── US-016: Natural Language Interface (21 pts)
│   └── Feature 4.2: Web Application (21 pts)
│       └── US-017: Responsive Web Application (21 pts)
│
├── Epic 5: Observability & Quality Assurance (39 pts, Sprint 7)
│   ├── Feature 5.1: Langfuse Observability (13 pts)
│   │   └── US-018: Comprehensive Tracing & Monitoring (13 pts)
│   ├── Feature 5.2: LLM-as-a-Judge Evaluation (13 pts)
│   │   └── US-019: Automated Quality Evaluation (13 pts)
│   └── Feature 5.3: Performance Optimization (13 pts)
│       └── US-020: System Performance Optimization (13 pts)
│
└── Epic 6: Testing & Production Deployment (47 pts, Sprint 8)
    ├── Feature 6.1: Comprehensive Testing (21 pts)
    │   └── US-021: Testing Suite (21 pts)
    ├── Feature 6.2: Documentation & Training (13 pts)
    │   └── US-022: Complete Documentation (13 pts)
    └── Feature 6.3: Production Deployment (13 pts)
        └── US-023: Go-Live (13 pts)
```

## Prerequisites

1. **Python 3.7+**
2. **Atlassian Account** with access to:
   - Jira Project: `SMMG6` (https://fistdat.atlassian.net/jira/software/projects/SMMG6)
   - Confluence Space: `S` (https://fistdat.atlassian.net/wiki/spaces/S)
3. **API Token**: Generate from https://id.atlassian.com/manage-profile/security/api-tokens

## Installation

1. Install required Python packages:
```bash
pip install requests python-dotenv
```

2. Set up environment variables:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Add to `.env`:
```
ATLASSIAN_EMAIL=your-email@example.com
ATLASSIAN_API_TOKEN=your-api-token
```

## Usage

### Option 1: Using Environment Variables

```bash
# Export environment variables
export ATLASSIAN_EMAIL="your-email@example.com"
export ATLASSIAN_API_TOKEN="your-api-token"

# Run the automation
python eaio_jira_confluence_automation.py
```

### Option 2: Using .env File

```bash
# Load from .env file
python -c "from dotenv import load_dotenv; load_dotenv()" && python eaio_jira_confluence_automation.py
```

### Option 3: Run with dotenv

```bash
pip install python-dotenv

# Modify the script to load .env at the top
python eaio_jira_confluence_automation.py
```

## What the Script Does

### Phase 1: Create Sprints (5-10 minutes)
- Creates 9 sprints (Sprint 0-8)
- Each sprint is 2 weeks
- Starts from current date
- Assigns story point targets

### Phase 2: Create Epics (10-15 minutes)
- Creates 6 epics with descriptions
- Sets epic names and metadata
- Configures business value and success criteria

### Phase 3: Create User Stories and Tasks (30-60 minutes)
- Creates 22 user stories
- Assigns story points
- Links to parent epics
- Creates 100+ subtasks
- Assigns to appropriate sprints

### Phase 4: Create Confluence Pages (20-30 minutes)
- Creates root documentation page
- Creates main sections (00-90)
- Creates subsections and document placeholders
- Establishes page hierarchy

### Phase 5: Create Mappings (10-15 minutes)
- Links Jira issues to Confluence pages
- Creates cross-references
- Establishes traceability

**Total Time**: Approximately 75-130 minutes

## Monitoring Progress

The script provides real-time output:
```
================================================================================
EAIO PROJECT AUTOMATION - STARTING
================================================================================

--- CREATING SPRINTS ---

✓ Created Sprint: Sprint 0: EAIO (26pts) (ID: 123)
✓ Created Sprint: Sprint 1: EAIO (34pts) (ID: 124)
...

--- EPIC 1: PROJECT FOUNDATION & INFRASTRUCTURE ---

✓ Created: EPIC 1: Project Foundation & Infrastructure (SMMG6-1)
✓ Created: US-001: Setup Development Environment (SMMG6-2)
  ✓ Added SMMG6-2 to sprint 123
✓ Created: Task 1.1: Cài đặt Docker Desktop và configure daemon (SMMG6-3)
...
```

## Output

After completion, you'll find:

1. **automation_summary.json** - Complete record of all created items with IDs and keys
2. **Jira Project** - Fully populated with epics, stories, tasks, and sprints
3. **Confluence Space** - Complete documentation structure

## Error Handling

The script includes:
- ✅ Rate limiting (0.2-0.5s delays)
- ✅ Error messages with details
- ✅ Continuation on individual failures
- ✅ Summary of created items

If errors occur:
1. Check the console output for specific error messages
2. Verify your API token is valid
3. Ensure you have permissions on the project/space
4. Check the `automation_summary.json` to see what was created

## Customization

### Modify Issue Types
If your Jira uses different issue types, update lines:
- Epic: Line 176 `"issuetype": {"name": "Epic"}`
- Story: Line 520 `"issuetype": {"name": "Story"}`
- Task: Line 541 `"issuetype": {"name": "Task"}`

### Custom Fields
Update custom field IDs:
- Epic Name: Line 177 `"customfield_10011"`
- Story Points: Line 529 `"customfield_10016"`

Find your custom field IDs:
```bash
curl -u your-email@example.com:your-api-token \
  https://fistdat.atlassian.net/rest/api/3/field | jq
```

### Sprint Duration
Modify line 89 to change sprint length:
```python
sprint_end = sprint_start + timedelta(weeks=2, days=-1)  # Change weeks=2
```

## Verification

After running, verify in:

### Jira
1. Go to https://fistdat.atlassian.net/jira/software/projects/SMMG6/board
2. Check backlog for all epics
3. Verify sprint assignments
4. Check epic relationships

### Confluence
1. Go to https://fistdat.atlassian.net/wiki/spaces/S
2. Verify page hierarchy
3. Check document structure

## Rollback

If you need to delete everything:

```bash
# Create a cleanup script
python cleanup_jira.py --project SMMG6 --dry-run

# After verifying, run for real
python cleanup_jira.py --project SMMG6
```

## Support

For issues:
1. Check console output for errors
2. Verify API credentials
3. Check Jira/Confluence permissions
4. Review `automation_summary.json`

## License

Internal use only - EAIO Project 2025

## Version

Version: 1.0
Last Updated: January 2025
Author: EAIO Project Team
