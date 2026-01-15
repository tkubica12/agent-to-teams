# app.py
"""Simple agent using Microsoft 365 Agent SDK that responds with a test message."""
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from start_server import start_server

# Create the Agent Application
# For local testing (anonymous mode), we use CloudAdapter() without authentication
AGENT_APP = AgentApplication[TurnState](
    storage=MemoryStorage(), 
    adapter=CloudAdapter()
)


async def _help(context: TurnContext, _: TurnState):
    """Handle help command and welcome messages."""
    await context.send_activity(
        "Welcome to the Simple Test Agent! 🚀\n"
        "Send me any message to receive a test response."
    )


# Register handlers for different events

# Handle when bot is added to conversation (welcome message)
AGENT_APP.conversation_update("membersAdded")(_help)

# Handle /help command
AGENT_APP.message("/help")(_help)


# Handle all other messages
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _: TurnState):
    """Respond to any message with a simple response.
    
    Note: Step 1 uses simple responses for local simulator compatibility.
    For streaming responses, see Step 2 and Step 3 which work with Azure Bot Service and Teams.
    """
    # For local simulator testing, use simple response
    # The Teams App Test Tool doesn't fully support streaming protocol
    await context.send_activity(
        "Hello, this is test message from Python! "
        "This demonstrates a simple response. "
        "For streaming with citations, see Step 2 and Step 3."
    )


# Start the server
if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Simple Test Agent - Step 1 (Local Simulator)")
        print("=" * 60)
        print("No authentication required for local testing")
        print("Ready for Teams Simulator (teamsapptester)")
        print("=" * 60)
        
        # Start server with None auth configuration (anonymous mode)
        start_server(AGENT_APP, None)
        
    except Exception as error:
        print(f"Error starting server: {error}")
        raise error
