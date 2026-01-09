# Step 1: Create Microsoft Entra ID App Registration
# ====================================================
# This script creates the identity for the Teams bot.
# Run this ONCE only - it is NOT idempotent.
# Save the output credentials to teams-agent/.env file.

# Configuration
# ==============================================================================
# EDIT THESE VALUES
$APP_NAME = "agent-teams-bot-" + (Get-Random -Minimum 1000 -Maximum 9999)
$DISPLAY_NAME = $APP_NAME  # You can customize the display name

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Create Entra ID App Registration" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Azure CLI login
Write-Host "Checking Azure CLI login..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        Write-Host "✓ Logged in as: $($account.user.name)" -ForegroundColor Green
        Write-Host "  Tenant: $($account.tenantId)" -ForegroundColor Gray
        Write-Host "  Subscription: $($account.name)" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "ERROR: Not logged in to Azure CLI" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}

# Confirm before proceeding
Write-Host "This will create a new App Registration with name:" -ForegroundColor Yellow
Write-Host "  $DISPLAY_NAME" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Create App Registration
# ==============================================================================
Write-Host ""
Write-Host "Creating App Registration..." -ForegroundColor Yellow

try {
    $appReg = az ad app create `
        --display-name "$DISPLAY_NAME" `
        --sign-in-audience "AzureADMyOrg" `
        2>&1 | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create app registration"
    }
    
    $appId = $appReg.appId
    Write-Host "✓ App Registration created" -ForegroundColor Green
    Write-Host "  App ID: $appId" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Failed to create App Registration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Create Service Principal (Enterprise Application)
# ==============================================================================
# This is required for single-tenant apps to use client credentials flow
Write-Host ""
Write-Host "Creating Service Principal..." -ForegroundColor Yellow

try {
    $sp = az ad sp create --id $appId 2>&1 | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create service principal"
    }
    
    Write-Host "✓ Service Principal created" -ForegroundColor Green
    Write-Host "  Object ID: $($sp.id)" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Failed to create Service Principal" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Create Client Secret
# ==============================================================================
Write-Host ""
Write-Host "Creating Client Secret..." -ForegroundColor Yellow

try {
    $secretParams = az ad app credential reset `
        --id $appId `
        --append `
        --display-name "BotLoginSecret" `
        --years 2 `
        2>&1 | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create client secret"
    }
    
    $appSecret = $secretParams.password
    $tenantId = $secretParams.tenant
    Write-Host "✓ Client Secret created (expires in 2 years)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create Client Secret" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Display Results
# ==============================================================================
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✓ App Registration Complete" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Save these credentials!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Copy these values to teams-agent/.env file:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Microsoft 365 Agents SDK Configuration" -ForegroundColor Gray
Write-Host "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=$appId" -ForegroundColor White
Write-Host "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=$appSecret" -ForegroundColor White
Write-Host "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=$tenantId" -ForegroundColor White
Write-Host "CONNECTIONSMAP_0_SERVICEURL=*" -ForegroundColor White
Write-Host "CONNECTIONSMAP_0_CONNECTION=SERVICE_CONNECTION" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Copy the values above to teams-agent/.env" -ForegroundColor Gray
Write-Host "  2. Run: .\2_create_bot_service.ps1" -ForegroundColor Gray
Write-Host ""

# Save to file for reference
$outputFile = "app_registration_output.txt"
$output = @"
App Registration Created: $(Get-Date)
=====================================

App Name: $DISPLAY_NAME
App ID: $appId
Tenant ID: $tenantId
Password: $appSecret

Copy to teams-agent/.env:
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=$appId
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=$appSecret
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=$tenantId
CONNECTIONSMAP_0_SERVICEURL=*
CONNECTIONSMAP_0_CONNECTION=SERVICE_CONNECTION
"@

$output | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "✓ Credentials also saved to: $outputFile" -ForegroundColor Green
Write-Host "  (Keep this file secure and delete after copying to .env)" -ForegroundColor Gray
Write-Host ""
