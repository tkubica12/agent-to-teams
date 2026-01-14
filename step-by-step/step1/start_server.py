# start_server.py
"""Server startup helper for the agent application."""
from os import environ
from microsoft_agents.hosting.core import AgentApplication, AgentAuthConfiguration
from microsoft_agents.hosting.aiohttp import (
    start_agent_process,
    jwt_authorization_middleware,
    CloudAdapter,
)
from aiohttp.web import Request, Response, Application, run_app


def start_server(
    agent_application: AgentApplication, auth_configuration: AgentAuthConfiguration
):
    """Start the aiohttp server for the agent application.
    
    Args:
        agent_application: The configured AgentApplication instance
        auth_configuration: Authentication config (can be None for anonymous/local testing)
    """
    async def entry_point(req: Request) -> Response:
        agent: AgentApplication = req.app["agent_app"]
        adapter: CloudAdapter = req.app["adapter"]
        return await start_agent_process(
            req,
            agent,
            adapter,
        )

    # Use jwt_authorization_middleware for production, but it handles None auth config
    APP = Application(middlewares=[jwt_authorization_middleware])
    APP.router.add_post("/api/messages", entry_point)
    APP.router.add_get("/api/messages", lambda _: Response(status=200))
    APP["agent_configuration"] = auth_configuration
    APP["agent_app"] = agent_application
    APP["adapter"] = agent_application.adapter

    try:
        port = int(environ.get("PORT", 3978))
        print(f"Starting server on http://localhost:{port}")
        print("Listening for messages on /api/messages")
        run_app(APP, host="localhost", port=port)
    except Exception as error:
        raise error
