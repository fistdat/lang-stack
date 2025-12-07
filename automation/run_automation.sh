#!/bin/bash

# EAIO Project Automation Runner
# This script runs the complete Jira and Confluence automation

set -e  # Exit on error

echo "=========================================="
echo "EAIO PROJECT AUTOMATION RUNNER"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your Atlassian credentials:"
    echo "  - ATLASSIAN_EMAIL: Your Atlassian email"
    echo "  - ATLASSIAN_API_TOKEN: Your API token from https://id.atlassian.com/manage-profile/security/api-tokens"
    echo ""
    echo "After editing .env, run this script again."
    exit 1
fi

echo "✓ .env file found"
echo ""

# Install required packages
echo "Installing required Python packages..."
pip3 install -q requests python-dotenv 2>/dev/null || pip install -q requests python-dotenv

echo "✓ Dependencies installed"
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate credentials
if [ -z "$ATLASSIAN_EMAIL" ] || [ -z "$ATLASSIAN_API_TOKEN" ]; then
    echo "❌ ATLASSIAN_EMAIL or ATLASSIAN_API_TOKEN not set in .env"
    echo "Please edit .env and add your credentials."
    exit 1
fi

echo "✓ Credentials loaded"
echo "  Email: $ATLASSIAN_EMAIL"
echo "  Token: ${ATLASSIAN_API_TOKEN:0:10}..."
echo ""

# Confirm before running
echo "This script will create:"
echo "  - 6 Epics"
echo "  - 22 User Stories"
echo "  - 100+ Tasks"
echo "  - 9 Sprints"
echo "  - Complete Confluence documentation structure"
echo ""
echo "Target:"
echo "  - Jira Project: SMMG6 (https://fistdat.atlassian.net/jira/software/projects/SMMG6)"
echo "  - Confluence Space: S (https://fistdat.atlassian.net/wiki/spaces/S)"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Automation cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "STARTING AUTOMATION..."
echo "=========================================="
echo ""

# Run the automation script
python3 eaio_jira_confluence_automation.py

echo ""
echo "=========================================="
echo "AUTOMATION COMPLETED!"
echo "=========================================="
echo ""
echo "Check the following:"
echo "  - Jira: https://fistdat.atlassian.net/jira/software/projects/SMMG6/board"
echo "  - Confluence: https://fistdat.atlassian.net/wiki/spaces/S"
echo "  - Summary: automation_summary.json"
echo ""
