# app.py
"""Simple agent using Microsoft 365 Agent SDK that responds with a test message."""
import asyncio
import os
from dotenv import load_dotenv
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter, Citation
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env
from start_server import start_server

# Load environment variables from .env file
load_dotenv()

# Load SDK configuration from environment variables
# Expects: CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID, etc.
agents_sdk_config = load_configuration_from_env(dict(os.environ))

# Create connection manager for authentication with Azure Bot Service
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)

# Create the Agent Application with authenticated CloudAdapter
AGENT_APP = AgentApplication[TurnState](
    storage=MemoryStorage(), 
    adapter=CloudAdapter(connection_manager=CONNECTION_MANAGER),
    **agents_sdk_config
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
    """Respond to any message with informative thinking events and a token-by-token streamed response with citations."""
    # Print token/claims information from Bot Service
    print("\n" + "=" * 60)
    print("TOKEN INFORMATION FROM BOT SERVICE")
    print("=" * 60)
    if context.identity:
        print(f"Is Authenticated: {context.identity.is_authenticated}")
        print(f"Authentication Type: {context.identity.authentication_type}")
        print(f"App ID: {context.identity.get_app_id()}")
        print(f"Outgoing App ID: {context.identity.get_outgoing_app_id()}")
        print(f"Is Agent Claim: {context.identity.is_agent_claim()}")
        print("\nAll Claims:")
        for claim_type, claim_value in context.identity.claims.items():
            print(f"  {claim_type}: {claim_value}")
    else:
        print("No identity/claims available (local testing mode)")
    print("=" * 60 + "\n")
    
    # Use the SDK's built-in StreamingResponse helper
    # Enable AI features
    context.streaming_response.set_feedback_loop(True)
    context.streaming_response.set_generated_by_ai_label(True)
    
    # Thinking events (informative - shows in thinking indicator)
    thinking_events = [
        "Got it, looking into it",
        "Searching Internet",
        "Searching Knowledge base",
        "Thinking"
    ]
    
    # Stream each thinking event with delays
    for event_text in thinking_events:
        context.streaming_response.queue_informative_update(event_text)
        await asyncio.sleep(2)  # 2-second delay between events
    
    # Final response text with citations
    full_response = (
        "Hello, this is test message from Python! [doc1][doc2] "
        "This demonstrates how citations work in Microsoft Teams and Copilot."
    )
    
    # Stream the response token by token (simulating LLM output)
    words = full_response.split()
    
    for word in words:
        context.streaming_response.queue_text_chunk(word + " ")
        await asyncio.sleep(0.1)  # Small delay between words
    
    # Set citations for the final message
    context.streaming_response.set_citations([
        Citation(
            title="Microsoft 365 Agent SDK Documentation",
            content="The Microsoft 365 Agent SDK enables building enterprise-grade "
                   "conversational AI agents with features like citations and streaming.",
            filepath="",
            url="https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/"
        ),
        Citation(
            title="Python Agent Sample",
            content="This is a simple example demonstrating how to use the Agent SDK "
                   "with Python to create responsive bot applications.",
            filepath="",
            url="https://github.com/microsoft/Agents-for-python"
        )
    ])
    
    # End the stream (sends final message with all accumulated text and citations)
    await context.streaming_response.end_stream()


# Start the server
if __name__ == "__main__":
    try:
        # Get the default auth config from connection manager
        auth_config = CONNECTION_MANAGER.get_default_connection_configuration()
        
        print("=" * 60)
        print("Simple Test Agent - Step 2 (Azure Bot Service)")
        print("=" * 60)
        print(f"App ID: {auth_config.CLIENT_ID}")
        print(f"Tenant ID: {auth_config.TENANT_ID}")
        print("=" * 60)
        
        # Start server with authentication configuration
        start_server(AGENT_APP, auth_config)
        
    except Exception as error:
        print(f"Error starting server: {error}")
        raise error
