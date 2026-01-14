# app.py
"""Simple agent using Microsoft 365 Agent SDK that responds with a test message."""
import asyncio
import uuid
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.activity import Activity, ActivityTypes
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
    # Generate unique stream ID for this interaction
    stream_id = str(uuid.uuid4())
    sequence = 1
    
    # Thinking events to stream (informative - shows in thinking box)
    thinking_events = [
        "Got it, looking into it",
        "Searching Internet",
        "Searching Knowledge base",
        "Thinking"
    ]
    
    # Stream each thinking event with 2-second delays
    for event_text in thinking_events:
        await context.send_activity(Activity(
            type=ActivityTypes.typing,
            text=event_text,
            entities=[{
                "type": "streaminfo",
                "streamId": stream_id,
                "streamType": "informative",
                "streamSequence": sequence
            }]
        ))
        sequence += 1
        await asyncio.sleep(2)  # 2-second delay between events
    
    # Final response text with citations
    full_response = (
        "Hello, this is test message from Python! [1][2] "
        "This demonstrates how citations work in Microsoft Teams and Copilot."
    )
    
    # Stream the response token by token (simulating LLM output)
    accumulated_text = ""
    words = full_response.split()
    
    for i, word in enumerate(words):
        accumulated_text += word + " "
        
        # Send streaming activity with accumulated text
        await context.send_activity(Activity(
            type=ActivityTypes.typing,
            text=accumulated_text.strip(),
            entities=[{
                "type": "streaminfo",
                "streamId": stream_id,
                "streamType": "streaming",
                "streamSequence": sequence
            }]
        ))
        sequence += 1
        
        # Small delay between words to simulate typing (0.1 seconds per word)
        await asyncio.sleep(0.1)
    
    # Send final message with citations (this ends the stream)
    final_message = Activity(
        type=ActivityTypes.message,  # Use "message" type for final
        text=full_response,
        entities=[
            {
                "type": "streaminfo",
                "streamId": stream_id,
                "streamType": "final"  # Use "final" for the last message
                # NO streamSequence on final message!
            },
            {
                "type": "https://schema.org/Message",
                "@type": "Message",
                "@context": "https://schema.org",
                "@id": "",
                "additionalType": ["AIGeneratedContent"],
                "citations": [
                    {
                        "@type": "Claim",
                        "position": "1",
                        "appearance": {
                            "name": "Microsoft 365 Agent SDK Documentation",
                            "abstract": "The Microsoft 365 Agent SDK enables building enterprise-grade "
                                       "conversational AI agents with features like citations and streaming."
                        }
                    },
                    {
                        "@type": "Claim",
                        "position": "2",
                        "appearance": {
                            "name": "Python Agent Sample",
                            "abstract": "This is a simple example demonstrating how to use the Agent SDK "
                                       "with Python to create responsive bot applications."
                        }
                    }
                ]
            }
        ]
    )
    
    await context.send_activity(final_message)


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
