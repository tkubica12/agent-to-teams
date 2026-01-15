# Empty Agent - Microsoft 365 Agent SDK Demo

This is a simple "empty" agent that demonstrates the Microsoft 365 Agent SDK with streaming responses and citations.

## What This Agent Does

- Responds to messages with **streaming responses** (token-by-token output)
- Shows **informative thinking indicators** ("Got it, looking into it", "Searching...", etc.)
- Includes **citations** in the response
- Displays **AI-generated content** labels and feedback buttons

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Azure CLI (`az login`)
- Azure subscription
- Microsoft 365 tenant with Teams

## Project Structure

```
empty-agent/
├── app.py                  # Main agent application
├── start_server.py         # Server startup module
├── pyproject.toml          # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── generate_app_package.ps1 # Script to generate Teams app package
└── appPackage/
    ├── manifest.template.json  # Teams manifest template
    ├── color.png               # App icon (192x192)
    └── outline.png             # App outline icon (32x32)
```

---

## Step-by-Step Guide

### 1. Login to Azure

```bash
az login
```

### 2. Set variables and create resource group

```powershell
$appName = "empty-agent"
$resourceGroup = "rg-empty-agent"  # Change to your resource group

az group create --name $resourceGroup --location "westeurope"
```

### 3. Create Microsoft Entra ID App Registration

```powershell
# Create the app registration
$app = az ad app create --display-name $appName | ConvertFrom-Json
$appId = $app.appId

# Create a service principal for the app (required for authentication)
az ad sp create --id $appId

# Create a client secret (valid for 1 year)
$secret = az ad app credential reset --id $appId --years 1 | ConvertFrom-Json
$clientSecret = $secret.password

# Get tenant ID
$tenantId = (az account show | ConvertFrom-Json).tenantId

# Display the values - SAVE THESE!
Write-Host "App ID: $appId"
Write-Host "Client Secret: $clientSecret"
Write-Host "Tenant ID: $tenantId"
```

### 4. Create Azure Bot Service with Streaming Enabled

```powershell
# Create the Azure Bot resource
az bot create `
    --resource-group $resourceGroup `
    --name $appName `
    --app-type SingleTenant `
    --appid $appId `
    --tenant-id $tenantId `
    --location "global"

# Enable streaming endpoint feature (required for streaming responses)
az rest `
    --method PATCH `
    --uri "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$resourceGroup/providers/Microsoft.BotService/botServices/${appName}?api-version=2023-09-15-preview" `
    --body '{\"properties\":{\"isStreamingSupported\":true}}'

# Enable Teams channel
az bot msteams create `
    --resource-group $resourceGroup `
    --name $appName
```

### 5. Configure your .env file

```powershell
@"
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=$appId
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=$clientSecret
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=$tenantId
"@ | Out-File -FilePath .env -Encoding UTF8
```

### 6. Run the agent

```powershell
uv run app.py
```

### 7. Expose your local server using VS Code Port Forwarding

VS Code has built-in port forwarding via Microsoft Dev Tunnels:

1. Make sure your agent is running on port 3978
2. Open the **Ports** view in the Panel (View → Open View → Ports, or `Ctrl+Shift+P` → "Ports: Focus on Ports View")
3. Click **Forward a Port** and enter `3978`
4. Right-click on the forwarded port → **Port Visibility** → **Public**
5. Copy the **Forwarded Address** (e.g., `https://abc123-3978.euw.devtunnels.ms`)

> **Note:** You'll need to sign in with your GitHub or Microsoft account the first time.

### 8. Update the Bot messaging endpoint

```powershell
az bot update `
    --resource-group $resourceGroup `
    --name $appName `
    --endpoint "https://YOUR-TUNNEL-URL/api/messages"
```

Replace `YOUR-TUNNEL-URL` with the forwarded address from the previous step.

### 9. Generate the Teams App Package

```powershell
.\generate_app_package.ps1
```

This creates `appPackage/app-package.zip` containing your manifest and icons.

### 10. Upload to Teams

**Option A: Sideload for testing (if enabled)**

1. Open Microsoft Teams
2. Go to **Apps** → **Manage your apps** → **Upload an app**
3. Select **Upload a custom app**
4. Choose `appPackage/app-package.zip`

**Option B: Teams Admin Center**

1. Go to [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Click **Upload new app**
4. Upload `appPackage/app-package.zip`
5. Approve the app for your organization

### 11. Test in Teams

1. Open Microsoft Teams
2. Search for "Empty Agent" in the Apps section
3. Start a chat with the agent
4. Send a message


