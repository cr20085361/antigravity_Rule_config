# PGRMS (Personal Global Rules Management System) - One-Click Windows Deployment Script
# Run this script inside PowerShell to deploy all rule configurations globally.

$ErrorActionPreference = "Stop"

Write-Host "========================================="
Write-Host "Starting PGRMS Automation Deployment"
Write-Host "========================================="

# 1. Scan and Rebuild Metadata Index
Write-Host "[Step 1/4] Scanning rule source repository..."
python scripts/pgrms.py scan

# 2. Compile Universal Rules
Write-Host "[Step 2/4] Compiling rules for all IDE targets..."
python scripts/pgrms.py compile --target all

# 3. Deploy Antigravity Global Skills
Write-Host "[Step 3/4] Deploying global Antigravity skills..."
$globalSkillsDir = "$env:USERPROFILE\.agent\skills"

# Confirm and create global skills directory if missing
if (-not (Test-Path $globalSkillsDir)) {
    New-Item -ItemType Directory -Force -Path $globalSkillsDir | Out-Null
}

# Copy compiled skills over
if (Test-Path "dist\antigravity\skills") {
    Copy-Item -Path "dist\antigravity\skills\*" -Destination $globalSkillsDir -Recurse -Force
    Write-Host " -> SUCCESS: Skills synchronized successfully."
}

# 4. Deploy Global Configuration Files
Write-Host "[Step 4/4] Deploying global settings..."

# Deploy .gitignore_global
$globalGitIgnore = "$env:USERPROFILE\.gitignore_global"
if (Test-Path ".gitignore_global") {
    Copy-Item -Path ".gitignore_global" -Destination $globalGitIgnore -Force
    git config --global core.excludesfile "$env:USERPROFILE\.gitignore_global"
    Write-Host " -> SUCCESS: Git global ignore rule activated."
}

# Deploy GEMINI.md
$globalGeminiDir = "$env:USERPROFILE\.gemini"
$globalGeminiFile = "$globalGeminiDir\GEMINI.md"
if (-not (Test-Path $globalGeminiDir)) {
    New-Item -ItemType Directory -Force -Path $globalGeminiDir | Out-Null
}
if (Test-Path "GEMINI.md") {
    Copy-Item -Path "GEMINI.md" -Destination $globalGeminiFile -Force
    Write-Host " -> SUCCESS: Global AI constraint file (GEMINI.md) deployed."
}

Write-Host "========================================="
Write-Host "PGRMS Deployment Completed Successfully!"
Write-Host " -> Dynamic Kanban Dashboard (dashboard.html) updated."
Write-Host "========================================="
