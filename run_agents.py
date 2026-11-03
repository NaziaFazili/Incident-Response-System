"""Run and test the Incident Response System's A2A agents.

Based on the Assignment 4 multi-agent runner. Run from the project root:

    uv run python run_incident_agents.py --mode start
    uv run python run_incident_agents.py --mode test
    uv run python run_incident_agents.py --mode test --agent coordinator

Start the Observability MCP server separately before testing Monitoring:

    uv run python -m mcp_server.server

Assumes agents.agent_factory.create_all_agents() returns entries like:
    {"monitoring": {"agent": <ADK agent>, "card": <AgentCard>},
     "coordinator": {"agent": <ADK agent>, "card": <AgentCard>}}

Written for the same A2A/ADK APIs as Assignment 4 (A2A SDK 0.3.x).
"""

import argparse
import asyncio
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Environment must be loaded before agent imports.
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# If your Assignment 4 project needed an A2A compatibility patch and you
# copied that module to agents/shared/a2a_compat.py, import it here BEFORE
# importing a2a.* or google.adk.*:
# from agents.shared import a2a_compat  # noqa: F401

import httpx
import uvicorn
from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.agent_factory import create_all_agents

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Fallback ports for factory entries that contain only "agent" and "card".
DEFAULT_PORTS = {"monitoring": 10020, "coordinator": 10023}


def server_port(name: str, info: dict[str, Any]) -> int:
    """Prefer the factory's port; otherwise use the AgentCard URL."""
    if "port" in info:
        return int(info["port"])
    url = getattr(info["card"], "url", None)
    if url:
        parsed = urlparse(url)
        if parsed.port:
            return parsed.port
    if name in DEFAULT_PORTS:
        return DEFAULT_PORTS[name]
    raise ValueError(f"No port configured for agent {name!r}")


def agent_url(name: str, info: dict[str, Any]) -> str:
    # Local demo: always target the address where these Uvicorn apps bind.
    return f"http://127.0.0.1:{server_port(name, info)}"


def print_agent_card(name: str, info: dict[str, Any]) -> None:
    card = info["card"]
    print("\n" + "=" * 70)
    print(f"AGENT: {card.name} ({name})")
    print(f"URL: {agent_url(name, info)}")
    print(f"Description: {card.description}")
    for skill in card.skills:
        print(f"  Skill: {skill.name} - {skill.description}")
    print("=" * 70)


def create_agent_a2a_server(agent: Any, agent_card: AgentCard) -> Any:
    """Expose an ADK agent using its explicitly defined A2A AgentCard."""
    runner = Runner(
        app_name=agent.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    executor = A2aAgentExecutor(runner=runner, config=A2aAgentExecutorConfig())

    class LoggingRequestHandler(DefaultRequestHandler):
        async def on_message_send(self, params, context=None):
            logger.info("[%s] Received A2A request", agent_card.name)
            result = await super().on_message_send(params, context)
            logger.info("[%s] Finished A2A request", agent_card.name)
            return result

        async def on_message_send_stream(self, params, context=None):
            logger.info("[%s] Received streaming A2A request", agent_card.name)
            async for item in super().on_message_send_stream(params, context):
                yield item
            logger.info("[%s] Finished streaming A2A request", agent_card.name)

    handler = LoggingRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(agent_card=agent_card, http_handler=handler).build()


async def wait_until_ready(
    agents: dict[str, dict[str, Any]], timeout: float = 15.0
) -> None:
    async with httpx.AsyncClient(timeout=2.0) as client:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            ready = True
            for name, info in agents.items():
                try:
                    r = await client.get(
                        agent_url(name, info) + AGENT_CARD_WELL_KNOWN_PATH
                    )
                    if r.status_code != 200:
                        ready = False
                except httpx.HTTPError:
                    ready = False
            if ready:
                return
            await asyncio.sleep(0.4)
    raise RuntimeError(
        "A2A servers did not become ready. Check port conflicts and server logs."
    )


class A2AClient:
    """Minimal A2A test client adapted"""

    async def send_message(self, url: str, prompt: str) -> str:
        timeout = httpx.Timeout(240.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as http_client:
            response = await http_client.get(url + AGENT_CARD_WELL_KNOWN_PATH)
            response.raise_for_status()
            card = AgentCard(**response.json())
            client_config = ClientConfig(
                httpx_client=http_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                use_client_preference=True,
            )
            client = ClientFactory(client_config).create(card)
            message = create_text_message_object(content=prompt)
            events = [event async for event in client.send_message(message)]

            if not events:
                return "No response received"

            # A2A SDK 0.3 client yields (Task, update) or (Message, None).
            last = events[-1]
            result = last[0] if isinstance(last, tuple) else last
            if getattr(result, "artifacts", None):
                return "\n".join(
                    part.root.text
                    for artifact in result.artifacts
                    for part in artifact.parts
                    if hasattr(part.root, "text")
                )
            if getattr(result, "parts", None):
                return "\n".join(
                    part.root.text
                    for part in result.parts
                    if hasattr(part.root, "text")
                )
            status = getattr(result, "status", None)
            if status is not None:
                detail = getattr(status, "message", None)
                raise RuntimeError(
                    f"A2A task ended with status {status.state}: {detail}"
                )
            return str(result)


async def test_agents(configs: dict[str, dict[str, Any]], selected: str) -> None:
    requests = {
        "monitoring": (
            "Investigate incident INC-TEST-001 for service authentication-api. "
            "Alert: HIGH_ERROR_RATE, severity HIGH, error rate 18.5%, "
            "detected at 2026-10-27T10:10:00Z. "
            "Use get_logs, get_metrics, and get_deployments through MCP. "
            "Report findings, evidence, and possible causes; do not execute remediation."
        ),
        "coordinator": (
            "Investigate incident INC-TEST-001 for service authentication-api. "
            "Alert: HIGH_ERROR_RATE, severity HIGH, error rate 18.5%, "
            "detected at 2026-10-27T10:10:00Z. "
            "Delegate the investigation and summarize available evidence."
        ),
    }
    names = list(configs) if selected == "all" else [selected]
    client = A2AClient()
    for name in names:
        if name not in configs:
            logger.warning("Skipping %s: not returned by create_all_agents()", name)
            continue
        print(f"\n{'=' * 70}\nTESTING {name.upper()} AGENT\n{'=' * 70}")
        prompt = requests.get(name, "Describe your available capabilities.")
        try:
            answer = await client.send_message(agent_url(name, configs[name]), prompt)
            print(answer)
        except Exception as exc:
            logger.exception("Test for %s failed: %s", name, exc)


async def main_async(mode: str, selected: str) -> None:
    configs = create_all_agents()
    if not configs:
        raise RuntimeError("create_all_agents() returned no agents")

    for name, info in configs.items():
        print_agent_card(name, info)

    # Ensure the Coordinator and Monitoring Agent can find each other on the
    # AgentCard URLs configured in agents/agent_cards.py.
    servers = []
    for name, info in configs.items():
        app = create_agent_a2a_server(info["agent"], info["card"])
        port = server_port(name, info)
        server = uvicorn.Server(
            uvicorn.Config(
                app, host="127.0.0.1", port=port, log_level="warning", loop="none"
            )
        )
        servers.append((name, server))

    tasks = [
        asyncio.create_task(s.serve(), name=f"server-{name}") for name, s in servers
    ]
    try:
        await wait_until_ready(configs)
        print("\nAll configured A2A servers are running.")
        for name, info in configs.items():
            print(f"  {name}: {agent_url(name, info)}{AGENT_CARD_WELL_KNOWN_PATH}")
        if mode == "test":
            await test_agents(configs, selected)
            return
        print("\nPress Ctrl+C to stop all agent servers.")
        await asyncio.gather(*tasks)
    finally:
        for _, server in servers:
            server.should_exit = True
        await asyncio.gather(*tasks, return_exceptions=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Incident Response A2A agents")
    parser.add_argument("--mode", choices=["start", "test"], default="start")
    parser.add_argument(
        "--agent",
        choices=["monitoring", "coordinator", "all"],
        default="monitoring",
        help="Which agent to test when --mode test (default: monitoring)",
    )
    args = parser.parse_args()
    try:
        asyncio.run(main_async(args.mode, args.agent))
    except KeyboardInterrupt:
        logger.info("Stopping A2A servers")


if __name__ == "__main__":
    main()
