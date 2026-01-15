# app.py
"""Simple agent using Microsoft 365 Agent SDK that responds with a test message."""
import asyncio
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter, Citation
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
    """Respond to any message with informative thinking events and a token-by-token streamed response with citations."""
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
