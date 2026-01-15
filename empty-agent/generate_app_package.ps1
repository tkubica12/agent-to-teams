# Read App ID from environment variable used by the SDK
$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=(.+)$") {
            $env:APP_ID = $matches[1]
        }
    }
}

if (-not $env:APP_ID) {
    Write-Error "APP_ID not found. Make sure CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID is set in .env file"
    exit 1
}

Write-Host "Using App ID: $env:APP_ID"

# Read the template and replace placeholder
$template = Get-Content "appPackage/manifest.template.json" -Raw
$manifest = $template -replace '\$\{\{APP_ID\}\}', $env:APP_ID

# Write the manifest.json
$manifest | Out-File -FilePath "appPackage/manifest.json" -Encoding UTF8

Write-Host "Generated appPackage/manifest.json"

# Create the app package ZIP
$zipPath = "appPackage/app-package.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

Compress-Archive -Path "appPackage/manifest.json", "appPackage/color.png", "appPackage/outline.png" -DestinationPath $zipPath

Write-Host "Created $zipPath"
Write-Host ""
Write-Host "Upload this ZIP file to Teams Admin Center or use it for sideloading."
