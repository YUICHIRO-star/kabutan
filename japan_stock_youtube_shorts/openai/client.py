from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


def openai_client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is required. Configure via GitHub secrets or environment.")
    return OpenAI(api_key=key)
