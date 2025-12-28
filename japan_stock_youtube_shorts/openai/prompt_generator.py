"""
Helpers to generate prompts and retrieve ChatGPT completions.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from openai import APIError

from ..config import RuntimeConfig
from ..utils import retry_with_backoff
from .client import openai_client

logger = logging.getLogger(__name__)


@dataclass
class PromptContext:
    """Metadata used to build consistent prompts."""

    ticker: str
    company_name: str
    timeframe: str = "past month"
    style: str = "concise, upbeat Japanese narration suitable for YouTube Shorts"
    call_to_action: str = "チャンネル登録と高評価もよろしくお願いします！"


class PromptGenerator:
    """Compose prompts and fetch completions from OpenAI."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, runtime: Optional[RuntimeConfig] = None) -> None:
        self.runtime = runtime or RuntimeConfig.from_env()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if self.runtime.dry_run:
            self.client = None
        else:
            self.client = openai_client(api_key)

    def build_script_prompt(self, context: PromptContext, stock_summary: str) -> str:
        """Construct a prompt instructing the model to create a narration."""
        prompt = (
            f"あなたは『株鍛（かぶたん）』というコンセプトで、"
            f"視聴者の投資思考を鍛える短編解説動画の台本を作成します。\n\n"
            
            f"【対象銘柄】\n"
            f"{context.ticker}（{context.company_name}）\n\n"
            
            f"【対象期間】\n"
            f"{context.timeframe}\n\n"
            
            f"【事実（価格データの要約）】\n"
            f"{stock_summary}\n\n"
            
            "【解説方針】\n"
            "- 起きた事実と、それに対する解釈を分けて説明してください\n"
            "- 値動きを『良い・悪い』で断定しないでください\n"
            "- この動きが投資家心理や市場参加者の行動として"
            "どう読めるかを説明してください\n"
            "- 短期的な値動きの限界にも必ず触れてください\n\n"
            
            "【出力要件】\n"
            "- 60〜90秒のYouTube Shorts向け台本\n"
            "- 冒頭は『問い』や『違和感』から始める\n"
            "- 最後に次のCTAを自然に含める\n\n"
            
            f"CTA:\n{context.call_to_action}\n"
        )
        
        logger.debug("Built script prompt (kabutan style): %s", prompt)
        return prompt



    @retry_with_backoff(attempts=4)
    def complete(self, system: str, messages: List[Dict[str, str]]) -> str:
        """Execute a chat completion call."""
        if self.runtime.dry_run:
            logger.info("[dry-run] Skipping OpenAI request; returning placeholder content.")
            return "これはドライラン用のサンプル台本です。"
        if not self.client:
            raise RuntimeError("OpenAI client unavailable.")
        logger.info("Requesting completion on model=%s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=0.6,
        )
        return response.choices[0].message.content or ""

    def generate_script(self, context: PromptContext, stock_summary: str) -> str:
    """End-to-end helper to create a script from context + summary."""
    prompt = self.build_script_prompt(context, stock_summary)

    system = (
        "You are a Japanese equity analyst focused on long-term thinking. "
        "You do not exaggerate or hype stock movements. "
        "You clearly distinguish between factual price movements and interpretation. "
        "Your goal is to help viewers think better about stocks, not to give buy/sell advice."
    )

    return self.complete(system, [{"role": "user", "content": prompt}])

