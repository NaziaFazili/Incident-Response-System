import logging
import os

from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

from config.agents_config import MCP_SERVER_URL

# Setup logging
logger = logging.getLogger(__name__)

# SSE endpoint URL for the MCP server
MCP_SSE_URL = f"{MCP_SERVER_URL}/sse"

logger.info(f"[MCP_TOOLSET] MCP SSE URL: {MCP_SSE_URL}")

# def create_full_toolset() -> McpToolset:
#     """Create an McpToolset with ALL MCP server tools (no filter).

#     Returns:
#         McpToolset: Toolset connected to MCP server with all tools
#     """
#     logger.info("[MCP_TOOLSET] Creating full toolset (no filter)")
#     return McpToolset(
#         connection_params=SseConnectionParams(url=MCP_SSE_URL),
#     )


def create_monitoring_toolset() -> McpToolset:
    """Create an McpToolset for the Monitoring Agent.

    Includes monitoring tools for a service.

    Returns:
        McpToolset: Toolset with log tools
    """
    log_tool_names = ["get_logs", "get_metrics", "get_deployments"]

    logger.info("[MCP_TOOLSET] Creating monitoring toolset")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
        tool_filter=log_tool_names,
    )
