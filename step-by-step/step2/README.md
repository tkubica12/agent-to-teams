# Step 2 - Azure Bot Service Integration

In this step, we'll connect our Python agent to Azure Bot Service and test it using the Azure Portal's Web Chat feature.

## Overview

Building on Step 1, we'll now:
1. Create an Entra ID App Registration for authentication
2. Deploy an Azure Bot Service
3. Connect our local agent to Azure using a dev tunnel
4. Test using Azure Portal's Web Chat

## Prerequisites

- Completed Step 1 (Python agent working with local simulator)
- Azure CLI - [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Azure subscription with active access

## Project Structure

This step uses the same code as Step 1, but adds Azure configuration:

```
step2/
├── app.py              # Main agent application (same as step1)
├── start_server.py     # Server startup helper (same as step1)
├── pyproject.toml      # Project dependencies (same as step1)
├── .env                # Environment variables (with Azure credentials)
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Azure Setup

### Step 1: Login to Azure

```powershell
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "<your-subscription-id>"
```

### Step 2: Create Resource Group

```powershell
# Set variables
$RESOURCE_GROUP = "rg-agent-test"
$LOCATION = "westeurope"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 3: Create Entra ID App Registration

```powershell
# Create App Registration
$APP_NAME = "simple-agent-step2"
$APP_REGISTRATION = az ad app create --display-name $APP_NAME | ConvertFrom-Json

# Get the App ID
$APP_ID = $APP_REGISTRATION.appId
Write-Host "App ID: $APP_ID"

# Create a client secret
$SECRET = az ad app credential reset --id $APP_ID --append | ConvertFrom-Json
$APP_PASSWORD = $SECRET.password
Write-Host "App Password: $APP_PASSWORD"

# Get Tenant ID
$TENANT_ID = az account show --query tenantId -o tsv
Write-Host "Tenant ID: $TENANT_ID"
```

### Step 4: Create Azure Bot Service

```powershell
# Create Bot Service
$BOT_NAME = "bot-simple-agent-step2"

az bot create `
  --resource-group $RESOURCE_GROUP `
  --name $BOT_NAME `
  --app-type SingleTenant `
  --appid $APP_ID `
  --tenant-id $TENANT_ID `
  --location global

Write-Host "Bot created: $BOT_NAME"
```

### Step 5: Update .env File

Copy the values from the previous commands into your `.env` file:

```powershell
# Update your .env file with these values
@"
MICROSOFT_APP_ID=$APP_ID
MICROSOFT_APP_PASSWORD=$APP_PASSWORD
MICROSOFT_APP_TENANT_ID=$TENANT_ID
PORT=3978
"@ | Set-Content .env

Write-Host "Updated .env file with Azure credentials"
```

## Local Setup and Run

```powershell
# Navigate to step2 directory
cd step-by-step/step2

# Install dependencies and run the agent (single command)
uv run app.py
```

The agent will start on port 3978 and display:
- Your App ID
- Your Tenant ID
- Server listening status

**Important**: Keep this terminal running while testing!

## Setting Up Dev Tunnel for Azure

Azure Bot Service needs a public endpoint to reach your local agent. VS Code has built-in dev tunnel support:

1. **In VS Code**, ensure your agent is running (`uv run app.py`)
2. Open the **Ports** view (View → Terminal → Ports tab, or press `Ctrl+` ` then click "PORTS")
3. You should see port 3978 listed (if your app is running)
4. Right-click on port 3978 → **Port Visibility** → **Public**
5. Right-click on port 3978 → **Copy Local Address** 
   - It will look like: `https://abc123-3978.eus.devtunnels.ms`

**Note**: The dev tunnel URL changes each time VS Code restarts, so you'll need to update the Bot Service endpoint when that happens.

## Configure Bot Service Endpoint

Update your Bot Service with the dev tunnel URL:

```powershell
# Update bot endpoint with your dev tunnel URL
$TUNNEL_URL = "https://jqclwctd-3978.euw.devtunnels.ms"
az bot update `
  --resource-group $RESOURCE_GROUP `
  --name $BOT_NAME `
  --endpoint "$TUNNEL_URL/api/messages"
```

Or via Azure Portal:
1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your Bot Service resource (`bot-simple-agent-step2`)
3. Go to **Configuration** blade
4. Set the **Messaging endpoint** to: `https://your-devtunnel-url/api/messages`
5. Click **Apply**

## Testing via Azure Bot Service Web Chat

1. **Verify your agent is running** locally on port 3978
2. **Verify your dev tunnel is active and public** (check VS Code Ports view)
3. **Verify the Bot Service endpoint is configured** correctly
4. Go to Azure Portal: https://portal.azure.com
5. Navigate to your Bot Service resource (`bot-simple-agent-step2`)
6. Go to **Test in Web Chat** blade
7. Send a message to test the bot
8. You should see:
   - Thinking indicators
   - Streaming response
   - Final message with citations
9. Check your terminal for token information output

### What you'll see in the terminal:
```
============================================================
TOKEN INFORMATION FROM BOT SERVICE
============================================================
Is Authenticated: True
Authentication Type: ...
App ID: 7a51f989-e93d-406d-b8ad-b40c5311cace
...
```

## How It Works

```
User Message → Azure Bot Service Web Chat
                        ↓
              Azure Bot Framework
                        ↓
              Dev Tunnel (public URL)
                        ↓
              /api/messages endpoint (local)
                        ↓
                  AgentApplication
                        ↓
                  on_message handler
                        ↓
              Streaming response with citations
                        ↓
              Azure Bot Service → User
```

## Key Differences from Step 1

| Aspect | Step 1 | Step 2 |
|--------|--------|--------|
| Testing Tool | Local Teams Simulator | Azure Web Chat |
| Azure Resources | None | App Registration + Bot Service |
| Authentication | None | Entra ID (App ID + Secret) |
| Network | localhost only | Public dev tunnel |
| .env Required | Optional | Required (with Azure creds) |

## Troubleshooting

### Bot doesn't respond in Web Chat

**Check these in order:**

1. **Is the agent running?**
   ```powershell
   # You should see: "Running on http://0.0.0.0:3978"
   ```

2. **Is the dev tunnel active and public?**
   - Open VS Code Ports view
   - Port 3978 should show a globe icon (public) and a tunnel URL

3. **Is the messaging endpoint correct?**
   ```powershell
   # Should end with /api/messages
   $TUNNEL_URL = "https://your-tunnel-url.devtunnels.ms"
   az bot show --resource-group $RESOURCE_GROUP --name $BOT_NAME --query "properties.endpoint"
   ```

4. **Are credentials correct?**
   - Check your .env file has `MICROSOFT_APP_ID`, `MICROSOFT_APP_PASSWORD`, `MICROSOFT_APP_TENANT_ID`
   - Restart the agent after changing .env

5. **Check the terminal for errors**
   - Authentication errors
   - Connection failures
   - JWT validation errors

### Authentication errors
- Verify the App ID matches between Bot Service and .env
- Regenerate client secret if expired

### Dev tunnel issues
- Make sure port 3978 is forwarded
- Verify visibility is set to "Public"
- Try restarting the tunnel

## Cleanup (Optional)

If you want to clean up Azure resources:

```powershell
# Delete the resource group and all resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Next Steps

After successfully testing with Azure Web Chat, proceed to **Step 3** to connect your agent to Microsoft Teams.
