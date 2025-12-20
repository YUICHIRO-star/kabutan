from __future__ import annotations

import logging
from typing import Dict

from openai import APIConnectionError, AuthenticationError

from .client import openai_client

logger = logging.getLogger(__name__)


def healthcheck() -> Dict[str, str]:
    """
    Perform a simple list-models call to verify OpenAI connectivity.
    """
    client = openai_client()
    try:
        models = client.models.list()
        logger.info("OpenAI healthcheck ok: %d models available", len(models.data))
        return {"status": "ok", "models": len(models.data)}
    except (AuthenticationError, APIConnectionError) as exc:
        logger.error("OpenAI healthcheck failed: %s", exc)
        raise
