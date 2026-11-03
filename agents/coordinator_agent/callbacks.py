import logging
import os
import sys

from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)


def save_monitoring_output(callback_context: CallbackContext):
    for event in reversed(callback_context.session.events):
        if (
            event.author == callback_context.agent_name
            and event.content
            and event.content.parts
        ):
            callback_context.state["monitoring_output"] = "".join(
                part.text or "" for part in event.content.parts
            )
            logger.info("Monitoring output saved to state.")
            break


def save_knowledge_output(callback_context: CallbackContext):
    for event in reversed(callback_context.session.events):
        if (
            event.author == callback_context.agent_name
            and event.content
            and event.content.parts
        ):
            callback_context.state["knowledge_output"] = "".join(
                part.text or "" for part in event.content.parts
            )
            logger.info("Knowledge output saved to state.")
            break


def save_remediation_output(callback_context: CallbackContext):
    for event in reversed(callback_context.session.events):
        if (
            event.author == callback_context.agent_name
            and event.content
            and event.content.parts
        ):
            callback_context.state["remediation_output"] = "".join(
                part.text or "" for part in event.content.parts
            )
            logger.info("Remediation output saved to state.")
            break
