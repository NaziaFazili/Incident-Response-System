"""
Monitoring MCP Server
Uses the official MCP Python SDK (FastMCP) for protocol handling and tool registration.

The server exposes 3 tools for logs, metrics and deployment via the MCP protocol.
It uses SSE (Server-Sent Events) transport for communication.

Endpoints (managed by FastMCP):
  GET  /sse       - SSE stream for receiving responses
  POST /messages/ - Send JSON-RPC 2.0 requests
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from config.logging_config import configure_logging
from config.mcp_config import DATA_DIR, HOST, PORT
from models.deployment import Deployment
from models.log_entry import LogEntry
from models.metric import Metric

configure_logging()
logger = logging.getLogger(__name__)

# Create MCP server using the official SDK
mcp = FastMCP("Incident Response MCP server", host=HOST, port=PORT)


# ==================== Tools ====================
@mcp.tool()
def get_logs(service: str) -> list[dict]:
    """Retrieve application logs for the specified service."""

    logger.info("Retrieving logs for service: %s", service)

    try:
        file_path = DATA_DIR / "logs.json"

        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Expected a JSON array")

        logs = [LogEntry.model_validate(item) for item in data]

        filtered_logs = [
            log.model_dump(mode="json") for log in logs if log.service == service
        ]

        logger.info("Found %d logs for service: %s", len(filtered_logs), service)

        return filtered_logs
    except (FileNotFoundError, json.JSONDecodeError, Exception) as ex:
        logger.exception("Failed to retrieve logs for service: %s", service)
        raise RuntimeError("Unable to retrieve application logs") from ex


@mcp.tool()
def get_metrics(service: str) -> list[dict]:
    """Retrieve performance metrics for the specified service."""

    logger.info("Retrieving metrics for service: %s", service)
    try:
        file_path = DATA_DIR / "metrics.json"

        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)

        metrics = [Metric.model_validate(item) for item in data]

        filtered_metrics = [
            metric.model_dump(mode="json")
            for metric in metrics
            if metric.service == service
        ]

        logger.info("Found %d metrics for service: %s", len(filtered_metrics), service)

        return filtered_metrics

    except (OSError, json.JSONDecodeError, TypeError) as ex:
        logger.exception("Failed to retrieve metrics for service: %s", service)
        raise RuntimeError("Unable to retrieve performance metrics") from ex


@mcp.tool()
def get_deployments(service: str) -> list[dict]:
    """Retrieve deployment history for the specified service."""

    logger.info("Retrieving deployments for service: %s", service)
    try:
        file_path = DATA_DIR / "deployments.json"

        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)

        deployments = [Deployment.model_validate(item) for item in data]

        filtered_deployments = [
            deployment.model_dump(mode="json")
            for deployment in deployments
            if deployment.service == service
        ]

        logger.info(
            "Found %d deployments for service: %s", len(filtered_deployments), service
        )

        return filtered_deployments

    except (OSError, json.JSONDecodeError, TypeError) as ex:
        logger.exception("Failed to retrieve deployments for service: %s", service)
        raise RuntimeError("Unable to retrieve deployment history") from ex


if __name__ == "__main__":
    logger.info(f"Starting Incident Response MCP Server on {HOST}:{PORT}")
    logger.info(f"Transport: SSE")
    logger.info(f"Endpoints: GET /sse (stream), POST /messages/ (requests)")
    logger.info(f"Available tools: 3")
    mcp.run(transport="sse")
