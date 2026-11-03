import logging

from agents.agent_cards import (
    create_coordinator_agent_card,
    create_knowledge_agent_card,
    create_monitoring_agent_card,
    create_remediation_agent_card,
)
from agents.coordinator_agent.agent import create_agent as create_coordinator_agent
from agents.knowledge_agent.agent import create_agent as create_knowledge_agent
from agents.monitoring_agent.agent import create_agent as create_monitor_agent
from agents.remediation_agent.agent import create_agent as create_remediation_agent

logger = logging.getLogger(__name__)


def create_all_agents() -> dict:
    logger.info("Creating all Incident Response System Agents")

    try:
        agents = {
            "monitoring": {
                "agent": create_monitor_agent(),
                "card": create_monitoring_agent_card(),
            },
            "knowledge": {
                "agent": create_knowledge_agent(),
                "card": create_knowledge_agent_card(),
            },
            "coordinator": {
                "agent": create_coordinator_agent(),
                "card": create_coordinator_agent_card(),
            },
            "remediation": {
                "agent": create_remediation_agent(),
                "card": create_remediation_agent_card(),
            },
        }
        logger.info("All Incident Response System Agents created successfully")
        return agents

    except Exception:
        logger.exception("Failed to create Incident Response System Agents")
        raise
