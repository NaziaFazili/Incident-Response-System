import logging
import os

from google.adk.agents import Agent

from agents.remediation_agent.prompts import REMEDIATION_INSTRUCTION
from config.agents_config import GEMINI_MODEL
from config.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """Create the Remediation Agent using HTN planning."""

    logger.info("[REMEDIATION] Creating Remediation Agent")

    agent = Agent(
        name="remediation_agent",
        model=GEMINI_MODEL,
        description=(
            "Creates hierarchical remediation plans based on incident investigation findings."
        ),
        instruction=REMEDIATION_INSTRUCTION,
    )

    logger.info("[REMEDIATION] Remediation Agent created successfully")

    return agent
