import logging

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)

from config.agents_config import (
    COORDINATOR_AGENT_PORT,
    COORDINATOR_AGENT_URL,
    KNOWLEDGE_AGENT_PORT,
    KNOWLEDGE_AGENT_URL,
    MONITORING_AGENT_PORT,
    MONITORING_AGENT_URL,
)

# from knowledge.agent import create_agent as create_knowledge_agent

logger = logging.getLogger(__name__)


def create_monitoring_agent_card() -> AgentCard:

    logger.info("Creating Monitoring Agent Card")
    try:
        card = AgentCard(
            name="Monitoring Agent",
            url=MONITORING_AGENT_URL,
            description="Investigates production incidents using logs, metrics, and deployments.",
            version="1.0",
            capabilities=AgentCapabilities(streaming=True),
            default_input_modes=["text/plain"],
            default_output_modes=["application/json"],
            preferred_transport=TransportProtocol.jsonrpc,
            skills=[
                AgentSkill(
                    id="investigate_incident",
                    name="Investigate Incident",
                    description="Uses MCP tools to analyze logs, metrics, and deployments.",
                    tags=["monitoring", "observability", "incident"],
                    examples=[
                        "Investigate incident INC-0001 for authentication-api.",
                        "Analyze logs and metrics for authentication-api.",
                    ],
                )
            ],
        )
        logger.info("Monitoring Agent Card created successfully")
        return card

    except Exception:
        logger.exception("Failed to create Monitoring Agent Card")
        raise


def create_knowledge_agent_card() -> AgentCard:

    logger.info("Creating Knowledge Agent Card")
    try:
        card = AgentCard(
            name="Knowledge Agent",
            url=KNOWLEDGE_AGENT_URL,
            description="Searches previous incidents and runbooks.",
            version="1.0",
            capabilities=AgentCapabilities(streaming=True),
            default_input_modes=["text/plain"],
            default_output_modes=["application/json"],
            preferred_transport=TransportProtocol.jsonrpc,
            skills=[
                AgentSkill(
                    id="search_incident_knowledge",
                    name="Search Incident Knowledge",
                    description="Finds similar past incidents",
                    tags=["knowledge", "incident-history"],
                    examples=[
                        "Find previous incidents involving SQL connection timeouts.",
                        "Find a runbook for database connection pool exhaustion.",
                    ],
                )
            ],
        )
        logger.info("Knowledge Agent Card created successfully")
        return card

    except Exception:
        logger.exception("Failed to create Knowledge Agent Card")
        raise


# def create_remediation_agent_card() -> AgentCard:
#     return AgentCard(
#         name="Remediation Agent",
#         url="http://127.0.0.1:10022",
#         description="Creates and ranks remediation plans using hierarchical task planning.",
#         version="1.0.0",
#         capabilities=AgentCapabilities(streaming=True),
#         default_input_modes=["text/plain"],
#         default_output_modes=["text/plain"],
#         preferred_transport=TransportProtocol.jsonrpc,
#         skills=[
#             AgentSkill(
#                 id="plan_remediation",
#                 name="Plan Remediation",
#                 description="Proposes remediation steps based on investigation findings.",
#                 tags=["remediation", "planning", "HTN"],
#                 examples=[
#                     "Create a remediation plan for database connection pool exhaustion.",
#                     "Rank recovery options for authentication-api.",
#                 ],
#             )
#         ],
#     )


def create_coordinator_agent_card() -> AgentCard:
    logger.info("Creating Coordinator Agent Card")

    try:
        card = AgentCard(
            name="Incident Coordinator Agent",
            url=COORDINATOR_AGENT_URL,
            description="Coordinates incident investigation across specialized agents.",
            version="1.0",
            capabilities=AgentCapabilities(streaming=True),
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"],
            preferred_transport=TransportProtocol.jsonrpc,
            skills=[
                AgentSkill(
                    id="coordinate_incident",
                    name="Coordinate Incident Response",
                    description="Delegates investigation tasks and combines findings.",
                    tags=["coordinator", "incident-response", "A2A"],
                    examples=[
                        "Investigate incident INC-0001.",
                        "Coordinate an investigation for authentication-api.",
                    ],
                )
            ],
        )
        logger.info("Coordinater Agent Card created successfully")
        return card

    except Exception:
        logger.exception("Failed to create Coordinater Agent Card")
        raise
