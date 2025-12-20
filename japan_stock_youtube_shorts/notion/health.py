from __future__ import annotations

import logging
from typing import Dict, Optional

from notion_client.errors import APIResponseError

from .notion_client import NotionClient

logger = logging.getLogger(__name__)


def healthcheck(notion: Optional[NotionClient] = None) -> Dict[str, str]:
    """
    Perform a lightweight healthcheck by fetching the current bot user.
    """
    notion = notion or NotionClient()
    try:
        user = notion.client.users.me()
        logger.info("Notion healthcheck ok for bot: %s", user.get("name", "unknown"))
        return {"status": "ok", "bot": user.get("name", "unknown")}
    except APIResponseError as exc:
        logger.error("Notion healthcheck failed: %s", exc)
        raise
