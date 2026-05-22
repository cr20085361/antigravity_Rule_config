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
$globalSkillTargets = @(
    @{ Label = "Antigravity"; Path = "$env:USERPROFILE\.agent\skills" },
    @{ Label = "VS Code Copilot"; Path = "$env:USERPROFILE\.agents\skills" }
)

# Copy compiled skills over
if (Test-Path "dist\antigravity\skills") {
    foreach ($target in $globalSkillTargets) {
        if (-not (Test-Path $target.Path)) {
            New-Item -ItemType Directory -Force -Path $target.Path | Out-Null
        }
        Copy-Item -Path "dist\antigravity\skills\*" -Destination $target.Path -Recurse -Force
        Write-Host " -> SUCCESS: Skills synchronized to $($target.Label): $($target.Path)"
    }
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

python scripts/pgrms.py sync-vscode

Write-Host "========================================="
Write-Host "PGRMS Deployment Completed Successfully!"
Write-Host " -> Dynamic Kanban Dashboard (dashboard.html) updated."
Write-Host "========================================="
