# app.py
# Teams Agent using Microsoft 365 Agents SDK
import os
import sys
import traceback
from dotenv import load_dotenv

from microsoft_agents.hosting.core import (
   AgentApplication,
   TurnState,
   TurnContext,
   MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env
from start_server import start_server
from backend_client import BackendClient

# Load environment variables
load_dotenv()

# Load SDK configuration from environment variables
# This parses CONNECTIONS__*, CONNECTIONSMAP_* etc.
agents_sdk_config = load_configuration_from_env(dict(os.environ))

# Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Create backend client
backend_client = BackendClient(BACKEND_API_URL)

# Create connection manager and adapter using SDK config pattern
STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)

# Create the Agent Application with connection manager
AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, 
    adapter=ADAPTER,
    **agents_sdk_config
)


async def _help(context: TurnContext, _: TurnState):
    """Handle help command and welcome messages."""
    await context.send_activity(
        "Welcome! I'm connected to the Azure OpenAI backend. "
        "Just send me a message and I'll respond using AI. "
        "Type /help for this message."
    )


# Simple in-memory session tracking (conversation_id -> session_id)
conversation_sessions: dict[str, str] = {}


async def on_message(context: TurnContext, state: TurnState):
    """Handle incoming messages by forwarding to backend API."""
    user_message = context.activity.text
    conversation_id = context.activity.conversation.id
    
    # Skip if no message or it's a command
    if not user_message or user_message.startswith("/"):
        return
    
    # Get or create backend session for this conversation
    session_id = conversation_sessions.get(conversation_id)
    
    try:
        if not session_id:
            # Create a new backend session
            session_id = await backend_client.create_session()
            conversation_sessions[conversation_id] = session_id
            print(f"Created backend session: {session_id} for Teams conversation: {conversation_id}")
        
        # Send message to backend and get response
        response = await backend_client.send_message(session_id, user_message)
        
        # Send response back to Teams
        await context.send_activity(response)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error communicating with backend: {error_msg}")
        
        # If session expired or not found, create a new one and retry
        if "404" in error_msg or "session" in error_msg.lower():
            try:
                session_id = await backend_client.create_session()
                conversation_sessions[conversation_id] = session_id
                print(f"Recreated backend session: {session_id}")
                
                response = await backend_client.send_message(session_id, user_message)
                await context.send_activity(response)
            except Exception as retry_error:
                await context.send_activity(
                    f"Sorry, I'm having trouble connecting to the AI service. Please try again later."
                )
        else:
            await context.send_activity(
                f"Sorry, something went wrong. Please try again."
            )


# Register handlers
AGENT_APP.conversation_update("membersAdded")(_help)
AGENT_APP.message("/help")(_help)

@AGENT_APP.activity("message")
async def message_handler(context: TurnContext, state: TurnState):
    await on_message(context, state)


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    """Handle errors."""
    print(f"\n[on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The agent encountered an error or bug.")


if __name__ == "__main__":
    try:
        print(f"Starting Teams Agent...")
        print(f"SDK config loaded: {list(agents_sdk_config.keys())}")
        # Use connection manager's default config for auth
        start_server(AGENT_APP, CONNECTION_MANAGER.get_default_connection_configuration())
    except Exception as error:
        raise error
