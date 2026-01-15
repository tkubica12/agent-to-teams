# Step 3 - Connect to Microsoft Teams

In this step, we'll connect our Azure Bot Service to Microsoft Teams and test the agent directly within the Teams client.

## Overview

Building on Step 2, we'll now:
1. Enable the Microsoft Teams channel on our Bot Service
2. Create a Teams app package
3. Upload and install the app in Teams
4. Test the agent in Microsoft Teams

## Prerequisites

- Completed Step 2 (Azure Bot Service working with Web Chat)
- Microsoft Teams account
- Permission to upload custom apps to Teams (may require admin approval)

## Project Structure

This step adds Teams app package files:

```
step3/
├── app.py              # Main agent application (same as step1/step2)
├── start_server.py     # Server startup helper (same as step1/step2)
├── pyproject.toml      # Project dependencies (same as step1/step2)
├── .env                # Environment variables (with Azure credentials)
├── .env.example        # Example environment variables
├── appPackage/         # Teams app package folder
│   ├── manifest.json   # Teams app manifest
│   ├── color.png       # App icon (192x192)
│   └── outline.png     # App icon outline (32x32)
└── README.md           # This file
```

## Enable Teams Channel

### Via Azure CLI

```powershell
# Enable Microsoft Teams channel
$RESOURCE_GROUP = "rg-agent-test"
$BOT_NAME = "bot-simple-agent-step2"

az bot msteams create `
  --resource-group $RESOURCE_GROUP `
  --name $BOT_NAME
```

### Via Azure Portal

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your Bot Service resource
3. Go to **Channels** blade
4. Click **Microsoft Teams**
5. Accept the terms and click **Apply**

## Create Teams App Package

### Step 1: Create App Icons

You need two icon files in the `appPackage` folder:
- **color.png**: 192x192 pixels, full color app icon
- **outline.png**: 32x32 pixels, transparent outline icon

For testing, you can use simple placeholder icons or create them with any image editor.

### Step 2: Generate App Package

Use the provided PowerShell script to generate your Teams app package:

```powershell
.\generate_app_package.ps1
```

This script automatically:
1. Reads your App ID from `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID` in the .env file
2. Generates `manifest.json` from the template (`appPackage/manifest.template.json`)
3. Creates a ZIP file (`SimpleAgent.zip`) containing the manifest and icons
4. Validates that required icons are present

The script will output the location of the generated ZIP file and any warnings if icons are missing.

## Install App in Teams

### Option 1: Upload Custom App (Development)

1. Open Microsoft Teams
2. Click on **Apps** in the left sidebar
3. Click **Manage your apps** at the bottom
4. Click **Upload an app**
5. Select **Upload a custom app**
6. Choose your `SimpleAgent.zip` file
7. Click **Add** to install the app

### Option 2: Teams Admin Center (Organization-wide)

If you have admin access:
1. Go to Teams Admin Center: https://admin.teams.microsoft.com
2. Navigate to **Teams apps** → **Manage apps**
3. Click **Upload new app**
4. Upload your `SimpleAgent.zip` file
5. The app will be available to users in your organization

## Testing in Teams

1. Make sure your agent is running locally:
   ```powershell
   uv run app.py
   ```

2. Ensure your dev tunnel is active and the Bot Service endpoint is configured

3. Open Microsoft Teams

4. Find your app in the Apps section or search for "Simple Agent"

5. Start a chat with the bot

6. Send a message and observe:
   - Thinking indicators appearing in Teams
   - Streaming response
   - Final message with clickable citations

## How It Works

```
User Message → Microsoft Teams Client
                        ↓
              Microsoft Teams Service
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
              Microsoft Teams → User
```

## Key Differences from Step 2

| Aspect | Step 2 | Step 3 |
|--------|--------|--------|
| Testing Location | Azure Portal Web Chat | Microsoft Teams Client |
| App Package | Not required | Required (manifest + icons) |
| Teams Channel | Not configured | Enabled on Bot Service |
| Rich Features | Basic | Full Teams features (citations, streaming, etc.) |

## Features Visible in Teams

- **Thinking Indicators**: Shows "thinking" messages while processing
- **Streaming**: Token-by-token response appearing in real-time
- **Citations**: Clickable citation numbers with expandable details
- **Welcome Message**: Automatic greeting when bot is added
- **Commands**: `/help` command available

## Troubleshooting

### App doesn't appear in Teams
- Verify the manifest.json is valid (use Teams App Studio to validate)
- Check that your App ID matches in manifest.json and Bot Service
- Ensure custom apps are allowed in your Teams tenant

### Bot doesn't respond in Teams
- Verify the Teams channel is enabled on your Bot Service
- Check dev tunnel is running and public
- Verify .env credentials match the Bot Service configuration

### Citations don't appear
- Citations require specific entity format (check app.py)
- Teams may cache responses - try a new conversation

### Streaming doesn't work
- Streaming requires proper `streaminfo` entities
- Check browser/Teams app is up to date

## Production Deployment

For production, you would:
1. Deploy your agent to Azure (App Service, Container Apps, etc.)
2. Update the Bot Service messaging endpoint to your production URL
3. Submit your app package to your organization's Teams app catalog
4. (Optional) Submit to the Microsoft Teams App Store

## Cleanup

To remove the app from Teams:
1. Right-click the app in Teams
2. Select **Uninstall**

To clean up Azure resources:
```powershell
# Delete the resource group and all resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Next Steps

Congratulations! You've successfully:
1. ✅ Created a Python agent with the Microsoft 365 Agent SDK
2. ✅ Connected it to Azure Bot Service
3. ✅ Deployed it to Microsoft Teams

Next, you can:
- Add AI capabilities (Azure OpenAI, LangChain, etc.)
- Implement conversation memory
- Add adaptive cards for rich UI
- Deploy to production
