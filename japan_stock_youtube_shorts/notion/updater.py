"""
Utilities to keep Notion pages in sync with pipeline progress.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..config import RuntimeConfig
from .notion_client import NotionClient

logger = logging.getLogger(__name__)


def update_status(page_id: str, status_name: str, client: Optional[NotionClient] = None) -> Dict[str, Any]:
    """Update the Status property on a Notion page."""
    notion = client or NotionClient()
    logger.info("Status update for %s -> %s", page_id, status_name)
    return notion.set_status(page_id, status_name)


def update_property(page_id: str, property_name: str, value: Any, client: Optional[NotionClient] = None) -> Dict[str, Any]:
    """
    Update a single property value.

    The value should follow Notion's property schema (e.g. {"rich_text": [{"text": {"content": "hello"}}]}).
    """
    notion = client or NotionClient()
    logger.info("Updating property %s for %s", property_name, page_id)
    return notion.update_page_properties(page_id, {property_name: value})


def record_script(page_id: str, script_text: str, client: Optional[NotionClient] = None) -> Dict[str, Any]:
    """Persist a generated script back to the Notion page."""
    logger.info("Recording generated script for page %s", page_id)
    return update_property(
        page_id,
        "Script",
        {"rich_text": [{"text": {"content": script_text}}]},
        client=client,
    )


def log_exception(page_id: str, exc: Exception, client: Optional[NotionClient] = None) -> None:
    runtime = (client.runtime if client else None) or RuntimeConfig.from_env()
    notion = client or NotionClient(runtime=runtime)
    logger.error("Logging exception to Notion for %s", page_id, exc_info=exc)
    notion.log_exception(page_id, exc)
