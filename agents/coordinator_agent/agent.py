import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from agents.coordinator_agent.callbacks import (
    save_knowledge_output,
    save_monitoring_output,
)
from agents.coordinator_agent.prompts import SUMMARY_INSTRUCTION
from agents.shared import a2a_compat  # noqa: F401
from config.agents_config import GEMINI_MODEL, KNOWLEDGE_AGENT_URL, MONITORING_AGENT_URL

logger = logging.getLogger(__name__)


def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """ """

    logger.info("create summary instruction: ")
    monitoring_output = readonly_context.state.get(
        "monitoring_output", "Monitoring results unavailable."
    )

    knowledge_output = readonly_context.state.get(
        "knowledge_output", "Knowledge results unavailable."
    )

    final_prompt = SUMMARY_INSTRUCTION.replace(
        "[monitoring_output]", monitoring_output
    ).replace("[knowledge_output]", knowledge_output)

    return final_prompt


def create_agent() -> SequentialAgent:
    logger.info("Creating Parallel Router Agent")

    try:
        remote_monitor_agent = RemoteA2aAgent(
            name="monitor_agent",
            agent_card=f"{MONITORING_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
            after_agent_callback=save_monitoring_output,
        )

        remote_knowledge_agent = RemoteA2aAgent(
            name="knowledge_agent",
            agent_card=f"{KNOWLEDGE_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
            after_agent_callback=save_knowledge_output,
        )

        parallel_worker_agent = ParallelAgent(
            name="parallel_worker",
            sub_agents=[remote_monitor_agent, remote_knowledge_agent],
        )

        summary_agent = Agent(
            name="summary_agent",
            model=GEMINI_MODEL,
            description="Combines monitor results and knowledge findings.",
            instruction=create_summary_instruction,
            output_key="investigation_summary",
            # include_contents="none",
        )

        coordinator = SequentialAgent(
            name="coordinator_agent",
            sub_agents=[parallel_worker_agent, summary_agent],
        )

        logger.info("Incident Response Router Agent created successfully")
        return coordinator
    except Exception:
        logger.exception("Failed to create Incident Response Router Agent")
        raise
