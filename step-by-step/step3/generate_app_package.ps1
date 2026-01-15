# Generate Teams App Package
# This script generates the manifest.json from the template and creates the app package

param(
    [string]$AppId = $env:MICROSOFT_APP_ID
)

# Check if App ID is provided
if (-not $AppId) {
    # Try to read from .env file
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" | Where-Object { $_ -match "^CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=" }
        if ($envContent) {
            $AppId = ($envContent -split "=")[1].Trim()
        }
    }
    
    if (-not $AppId) {
        Write-Error "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID not found. Please provide it as a parameter or set it in .env file."
        exit 1
    }
}

Write-Host "Using App ID: $AppId"

# Read template and replace placeholder
$templatePath = "appPackage/manifest.template.json"
$outputPath = "appPackage/manifest.json"

$template = Get-Content $templatePath -Raw
$manifest = $template -replace '\$\{\{MICROSOFT_APP_ID\}\}', $AppId

# Write manifest.json
Set-Content -Path $outputPath -Value $manifest
Write-Host "Generated manifest.json"

# Check for icons
$colorIcon = "appPackage/color.png"
$outlineIcon = "appPackage/outline.png"

if (-not (Test-Path $colorIcon)) {
    Write-Warning "color.png not found in appPackage folder. Please add a 192x192 icon."
}

if (-not (Test-Path $outlineIcon)) {
    Write-Warning "outline.png not found in appPackage folder. Please add a 32x32 icon."
}

# Create ZIP package
$zipPath = "SimpleAgent.zip"
$filesToZip = @("appPackage/manifest.json")

if (Test-Path $colorIcon) { $filesToZip += $colorIcon }
if (Test-Path $outlineIcon) { $filesToZip += $outlineIcon }

# Remove existing zip
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

# Create zip with just filenames (not paths)
Push-Location appPackage
$files = @("manifest.json")
if (Test-Path "color.png") { $files += "color.png" }
if (Test-Path "outline.png") { $files += "outline.png" }

Compress-Archive -Path $files -DestinationPath "../$zipPath" -Force
Pop-Location

Write-Host ""
Write-Host "Created app package: $zipPath"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Add color.png (192x192) and outline.png (32x32) to appPackage folder if missing"
Write-Host "2. Upload $zipPath to Microsoft Teams"
