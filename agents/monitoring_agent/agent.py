import logging
import os

from google.adk.agents import Agent

from agents.monitoring_agent.prompts import MONITORING_INSTRUCTION
from agents.shared.mcp_toolset import create_monitoring_toolset
from config.agents_config import GEMINI_MODEL
from config.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    logger.info("Creating Monitoring Agent")

    try:
        logger.info("Initializing Monitoring MCP toolset")

        if not GEMINI_MODEL:
            logger.error(
                "Initialization Failed: The shared variable GEMINI_MODEL is empty or invalid."
            )
            raise ValueError(
                "GEMINI MODEL environment variable must contain a valid model name string."
            )

        if not MONITORING_INSTRUCTION:
            logger.error(
                "Initialization Failed: MONITORING_INSTRUCTION is empty or invalid."
            )
            raise ValueError("MONITORING_INSTRUCTION must contain a valid prompt.")

        toolset = create_monitoring_toolset()

        agent = Agent(
            model=GEMINI_MODEL,
            name="monitor_agent",
            description="Investigates logs, metrics, and deployments for any service",
            instruction=MONITORING_INSTRUCTION,
            tools=[toolset],
        )
        logger.info("Monitoring created successfully")

        return agent
    except Exception:
        logger.exception("Failed to create Monitoring Agent")
        raise
