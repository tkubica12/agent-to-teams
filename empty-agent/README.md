# Empty Agent - Microsoft 365 Agent SDK Demo

This is a simple "empty" agent that demonstrates the Microsoft 365 Agent SDK with streaming responses and citations. The same code works across all testing environments - you just need to configure the credentials appropriately.

## What This Agent Does

- Responds to messages with **streaming responses** (token-by-token output)
- Shows **informative thinking indicators** ("Got it, looking into it", "Searching...", etc.)
- Includes **citations** in the response
- Displays **AI-generated content** labels and feedback buttons

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [Node.js](https://nodejs.org/) (for Teams App Test Tool)
- Azure CLI (`az login`)
- Azure subscription (for Steps 2-3)
- Microsoft 365 tenant with Teams (for Step 3)

## Project Structure

```
empty-agent/
├── app.py                  # Main agent application
├── start_server.py         # Server startup module
├── pyproject.toml          # Python dependencies
├── .env                    # Environment variables (local config)
├── .env.example            # Example environment variables
├── README.md               # This file
├── generate_app_package.ps1 # Script to generate Teams app package
└── appPackage/
    ├── manifest.template.json  # Teams manifest template
    ├── manifest.json           # Generated manifest (after running script)
    ├── color.png               # App icon (192x192)
    └── outline.png             # App outline icon (32x32)
```

---

## Step 1: Local Testing with Teams App Test Tool

This step lets you quickly verify the agent works locally. **Note:** The Teams App Test Tool doesn't fully support streaming, so you'll see errors, but it confirms basic message flow works.

### 1.1 Install the Teams App Test Tool

```bash
npm install -g @nicksreed/teamsapptester
```

### 1.2 Create a minimal .env file

Create a `.env` file with placeholder values (they won't be used for local testing, but the SDK requires them):

```env
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=00000000-0000-0000-0000-000000000000
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=placeholder
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=00000000-0000-0000-0000-000000000000
```

### 1.3 Run the agent

```powershell
uv run app.py
```

### 1.4 Start the Teams App Test Tool

In another terminal:

```bash
teamsapptester --endpoint http://localhost:3978/api/messages
```

### 1.5 Test it

Send a message in the test tool. You'll see **errors in the console** because the local simulator doesn't support streaming protocol, but you should see the agent attempting to respond. This confirms basic connectivity works.

---

## Step 2: Azure Bot Service Integration

Now let's connect to Azure Bot Service for proper testing with full streaming support.

### 2.1 Login to Azure

```bash
az login
```

### 2.2 Set variables and create resource group

```powershell
$appName = "empty-agent"
$resourceGroup = "rg-empty-agent"  # Change to your resource group

az group create --name $resourceGroup --location "westeurope"
```

### 2.3 Create Microsoft Entra ID App Registration

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

### 2.4 Create Azure Bot Service with Streaming Enabled

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
# Note: az bot create doesn't have a streaming flag, so we update via REST API
az rest `
    --method PATCH `
    --uri "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$resourceGroup/providers/Microsoft.BotService/botServices/${appName}?api-version=2023-09-15-preview" `
    --body '{\"properties\":{\"isStreamingSupported\":true}}'
```

> **Note:** The `isStreamingSupported: true` property is required for streaming responses to work in Teams. The Azure CLI doesn't have a direct flag for this, so we use the REST API to enable it.

### 2.5 Configure your .env file

```powershell
@"
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=$appId
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=$clientSecret
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=$tenantId
"@ | Out-File -FilePath .env -Encoding UTF8
```

### 2.6 Expose your local server using VS Code Port Forwarding

VS Code has built-in port forwarding via Microsoft Dev Tunnels:

1. Open VS Code and make sure your agent is running on port 3978
2. Open the **Ports** view in the Panel (View → Open View → Ports, or `Ctrl+Shift+P` → "Ports: Focus on Ports View")
3. Click **Forward a Port** and enter `3978`
4. Right-click on the forwarded port → **Port Visibility** → **Public**
5. Copy the **Forwarded Address** (e.g., `https://abc123-3978.euw.devtunnels.ms`)

> **Note:** You'll need to sign in with your GitHub or Microsoft account the first time.

### 2.7 Update the Bot messaging endpoint

```powershell
az bot update `
    --resource-group $resourceGroup `
    --name $appName `
    --endpoint "https://jqclwctd-3978.euw.devtunnels.ms/api/messages"
```

### 2.8 Run and test

```powershell
uv run app.py
```

Go to [Azure Portal](https://portal.azure.com) → your Bot resource → **Test in Web Chat**.

You should see:
- ✅ Streaming responses working
- ✅ Thinking indicators
- ✅ Citations appearing
- ✅ AI labels and feedback buttons

---

## Step 3: Microsoft Teams Integration

Finally, let's deploy to Microsoft Teams.

### 3.1 Enable Teams Channel

```powershell
az bot msteams create `
    --resource-group $resourceGroup `
    --name $appName
```

Or via Azure Portal:
1. Go to Azure Portal → your Bot resource
2. Navigate to **Channels**
3. Click **Microsoft Teams** → **Apply**
4. Accept the terms of service

### 3.2 Generate the Teams App Package

```powershell
.\generate_app_package.ps1
```

This creates `appPackage/app-package.zip` containing:
- `manifest.json` (with your App ID)
- `color.png` (192x192 icon)
- `outline.png` (32x32 icon)

### 3.3 Upload to Teams

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

### 3.4 Test in Teams

1. Open Microsoft Teams
2. Search for "Empty Agent" in the Apps section
3. Start a chat with the agent
4. Send a message

You should see the full experience:
- 🤔 Thinking indicators in the chat
- ⚡ Token-by-token streaming response
- 📚 Citations with source links
- 🤖 "Generated by AI" label
- 👍👎 Feedback buttons
