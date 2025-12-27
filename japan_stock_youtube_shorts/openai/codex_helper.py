"""
Lightweight helper around the OpenAI API for code-generation tasks.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from ..config import RuntimeConfig
from ..utils import retry_with_backoff
from .client import openai_client

logger = logging.getLogger(__name__)


class CodexHelper:
    """
    Uses a coding-capable OpenAI model to generate snippets such as matplotlib
    chart builders or ffmpeg command templates.
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, runtime: Optional[RuntimeConfig] = None) -> None:
        self.runtime = runtime or RuntimeConfig.from_env()
        self.model = model or os.getenv("OPENAI_CODING_MODEL", "gpt-4.1")
        self.client = None if self.runtime.dry_run else openai_client(api_key)

    @retry_with_backoff(attempts=4)
    def request_snippet(self, instruction: str) -> str:
        """
        Ask the model for a code snippet based on the given instruction.
        The response is returned verbatim so that callers can save or execute it.
        """
        if self.runtime.dry_run:
            logger.info("[dry-run] Skipping OpenAI snippet generation.")
            return "# dry-run placeholder"
        if not self.client:
            raise RuntimeError("OpenAI client unavailable.")
        logger.info("Generating code snippet with model=%s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You generate minimal, runnable Python scripts without explanations.",
                },
                {"role": "user", "content": instruction},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
