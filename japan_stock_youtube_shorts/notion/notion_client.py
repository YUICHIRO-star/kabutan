"""
Wrapper around the official Notion client to simplify property updates.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from notion_client import Client
from notion_client.errors import APIResponseError

from ..config import RuntimeConfig
from ..utils import retry_with_backoff

logger = logging.getLogger(__name__)


class NotionClient:
    """Simple wrapper that centralizes authentication and common helpers."""

    def __init__(self, token: Optional[str] = None, runtime: Optional[RuntimeConfig] = None) -> None:
        self.runtime = runtime or RuntimeConfig.from_env()
        self.token = token or os.getenv("NOTION_API_KEY")
        if not self.token:
            raise ValueError(
                "NOTION_API_KEY is required. Configure via GitHub secrets or environment variables; avoid printing the token."
            )
        self.client = Client(auth=self.token)

    @retry_with_backoff()
    def query_database(self, database_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Query a database with optional filter/sort parameters."""
        logger.debug("Querying Notion database %s with params %s", database_id, kwargs)
        return self.client.databases.query(database_id=database_id, **kwargs)

    @retry_with_backoff()
    def retrieve_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve a single page."""
        logger.debug("Retrieving Notion page %s", page_id)
        return self.client.pages.retrieve(page_id=page_id)

    @retry_with_backoff()
    def update_page_properties(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update one or more properties on a page."""
        if self.runtime.dry_run:
            logger.info("[dry-run] Skipping Notion property update for %s", page_id)
            return {"dry_run": True, "page_id": page_id, "properties": properties}
        logger.info("Updating properties on Notion page %s", page_id)
        logger.debug("Properties payload keys: %s", list(properties.keys()))
        return self.client.pages.update(page_id=page_id, properties=properties)

    @retry_with_backoff()
    def set_status(self, page_id: str, status_name: str) -> Dict[str, Any]:
        """Update a status property with the provided name."""
        return self.update_page_properties(
            page_id,
            properties={"Status": {"status": {"name": status_name}}},
        )

    @retry_with_backoff(attempts=2)
    def append_comment(self, page_id: str, content: str) -> Dict[str, Any]:
        """Append a comment block to a page."""
        if self.runtime.dry_run:
            logger.info("[dry-run] Skipping Notion comment append for %s", page_id)
            return {"dry_run": True, "page_id": page_id, "content": content}
        logger.info("Appending comment to page %s", page_id)
        return self.client.comments.create(
            parent={"page_id": page_id},
            rich_text=[{"type": "text", "text": {"content": content}}],
        )

    def log_exception(self, page_id: str, exc: Exception) -> None:
        """Record an exception detail to Notion without exposing secrets."""
        message = f"run_id={self.runtime.run_id}: {exc}"
        try:
            self.append_comment(page_id, message)
        except APIResponseError:
            logger.error("Failed to log exception to Notion for %s", page_id, exc_info=True)
