# AI Agent to Teams Integration

This project demonstrates how to integrate a proprietary Chatbot API (Backend) with Microsoft Teams using a "Teams Agent" middleware.

## Getting Started

**New to this project?** Start with the [empty-agent](./empty-agent/) folder - it contains a simple agent that demonstrates the Microsoft 365 Agent SDK with streaming responses, citations, and step-by-step instructions for:
1. Local testing with Teams App Test Tool
2. Azure Bot Service integration
3. Microsoft Teams deployment

## Architecture

The solution consists of three main components:

1.  **Backend** (`/backend`):
    -   **Type**: REST API (FastAPI)
    -   **Function**: Core logic, communicates with Azure OpenAI (using EntraID auth), manages chat sessions.
    -   **Storage**: In-memory (for demonstration).
    -   **Port**: 8000 (Private/Internal)

2.  **Frontend** (`/frontend`):
    -   **Type**: Web UI (Streamlit)
    -   **Function**: A simple chat interface for testing the Backend directly.
    -   **Port**: 8501

3.  **Teams Agent** (`/teams-agent`):
    -   **Type**: Bot (Microsoft 365 Agents SDK for Python)
    -   **Function**: Acts as a proxy/middleware. It receives messages from Microsoft Teams (via Azure Bot Service), forwards them to the Backend, and returns the response to Teams.
    -   **Port**: 3978 (Publicly reachable via Azure Bot Service)

4.  **Empty Agent** (`/empty-agent`):
    -   **Type**: Simple demonstration bot
    -   **Function**: A minimal agent showing streaming responses, citations, and AI labels. Great starting point for learning the SDK.
    -   **Port**: 3978

## Setup & Usage

### Prerequisites
-   Azure CLI (`az login`)
-   `uv` package manager (installed automatically by start script if missing)
-   Azure OpenAI resource (configured in environment)

### Automated Setup Scripts

The root folder contains PowerShell scripts to automate the Azure infrastructure setup:

1.  **`1_create_app_registration.ps1`**: Creates the Microsoft Entra ID App Registration for the bot identity.
2.  **`2_create_bot_service.ps1`**: Provisions the Azure Bot Service resource and links it to the App Registration.
3.  **`3_update_endpoint.ps1`**: Updates the Bot Service messaging endpoint (useful when your Dev Tunnel URL changes).

### Running the Project

Use the start script to launch all three services simultaneously:

```powershell
.\start.ps1
```

This will start:
-   Backend at http://localhost:8000
-   Frontend at http://localhost:8501
-   Teams Agent at http://localhost:3978

