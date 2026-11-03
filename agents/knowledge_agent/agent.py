import logging

from google.adk.agents import Agent

from agents.knowledge_agent.prompts import KNOWLEDGE_INSTRUCTION
from agents.shared.rag_tools import search_knowledge
from config.agents_config import GEMINI_MODEL
from config.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def create_agent() -> Agent:
    """Create the Knowledge Agent with RAG search capability."""

    logger.info("Creating Knowledge Agent")
    if not GEMINI_MODEL:
        logger.error(
            "Initialization Failed: The shared variable GEMINI_MODEL is empty or invalid."
        )
        raise ValueError(
            "GEMINI MODEL environment variable must contain a valid model name string."
        )

    if not KNOWLEDGE_INSTRUCTION:
        logger.error(
            "Initialization Failed: MONITORING_INSTRUCTION is empty or invalid."
        )
        raise ValueError("MONITORING_INSTRUCTION must contain a valid prompt.")

    agent = Agent(
        name="knowledge_agent",
        model=GEMINI_MODEL,
        description=(
            "Searches historical incidents and operational runbooks "
            "using RAG to identify similar problems and resolutions."
        ),
        instruction=KNOWLEDGE_INSTRUCTION,
        tools=[search_knowledge],
    )

    logger.info("[KNOWLEDGE] Knowledge Agent created successfully")

    return agent
