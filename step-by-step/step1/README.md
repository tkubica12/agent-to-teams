# Step 1 - Python Agent with Teams Simulator

In this step, we'll create a simple Python agent and test it locally using the Microsoft 365 Agents Playground (Teams simulator). No Azure resources required!

## Overview

This is a simple Python agent using the **Microsoft 365 Agent SDK** that responds to any message with a test response including streaming and citations. We'll test it entirely locally using the Teams simulator.

## Prerequisites

- Python 3.10 or newer
- [uv package manager](https://github.com/astral-sh/uv) - Install with: `pip install uv`
- Node.js (for the Teams simulator)

## Project Structure

```
step1/
├── app.py              # Main agent application
├── start_server.py     # Server startup helper
├── pyproject.toml      # Project dependencies (uv format)
├── .env                # Environment variables (local config)
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Local Setup and Run

```powershell
# Install dependencies and run the agent (single command)
uv run app.py
```

## Testing with Microsoft 365 Agents Playground

The Teams simulator allows you to test your agent locally without any Azure setup.

1. Install the test tool:
```powershell
npm install -g @microsoft/teams-app-test-tool
```

2. In a new terminal (keep the agent running), start the playground:
```powershell
teamsapptester
```

3. The playground will open in your browser at `http://localhost:56150`
4. It automatically connects to your agent running on port 3978
5. Send any message and observe:
   - Thinking indicators (streaming informative messages)
   - Token-by-token response streaming
   - Final response with citations

## How It Works

1. **Agent SDK**: Uses `microsoft-agents-hosting-aiohttp` (version 0.6.1+) for the latest Microsoft 365 Agent SDK
2. **Server**: aiohttp web server listening on port 3978
3. **Message Handler**: Demonstrates streaming responses with thinking indicators and citations
4. **State Management**: Uses in-memory storage (MemoryStorage) for conversation state
5. **No Azure Required**: The simulator connects directly to your local agent

## Key Files

- **app.py**: Main application with agent logic
  - Creates `AgentApplication` instance
  - Registers message handlers
  - Demonstrates streaming and citations
  
- **start_server.py**: HTTP server setup
  - Configures aiohttp routes
  - Sets up JWT authentication middleware
  - Handles incoming bot framework messages

- **pyproject.toml**: Modern Python project configuration
  - Uses uv package manager
  - Specifies Microsoft 365 Agent SDK dependencies
  - No requirements.txt needed

## Architecture (Local Testing)

```
User Message → Teams Simulator → /api/messages endpoint
                                  ↓
                          AgentApplication
                                  ↓
                          on_message handler
                                  ↓
                    Streaming response with citations
                                  ↓
                          Teams Simulator → User
```

## Next Steps

After successfully testing locally with the simulator, proceed to **Step 2** to connect your agent to Azure Bot Service.

1. **Step 2**: Add more complex message handling
2. **Step 3**: Integrate with Teams
3. **Step 4**: Add AI capabilities (Azure OpenAI)
4. **Step 5**: Deploy to Azure

## Troubleshooting

### Port Already in Use
```powershell
# Change PORT in .env file
PORT=3979
```

### Authentication Errors
- Verify App ID and Password are correct in `.env`
- Check that the App Registration has the correct permissions
- Ensure Tenant ID matches your Azure subscription

### Bot Not Responding
- Verify the bot endpoint URL is correct in Azure
- Check that dev tunnel is running and accessible
- Ensure the port visibility is set to **Public** in VS Code
- Verify the agent is running on the correct port
- Check Azure Bot Service logs in the portal

## References

- [Microsoft 365 Agent SDK Documentation](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/)
- [Quickstart Guide](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/quickstart)
- [Agent SDK Python Packages](https://pypi.org/project/microsoft-agents-hosting-aiohttp/)
- [Azure Bot Service Documentation](https://learn.microsoft.com/en-us/azure/bot-service/)