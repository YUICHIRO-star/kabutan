"""
Generate a YouTube Shorts-ready script for a given Japanese stock ticker.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from ..config import RuntimeConfig
from ..notion import updater
from ..openai.prompt_generator import PromptContext, PromptGenerator

logger = logging.getLogger(__name__)


def fetch_stock_summary(ticker: str, period: str = "1mo", *, dry_run: bool = False) -> str:
    """Download recent data and format a concise summary."""
    if dry_run:
        logger.info("[dry-run] Skipping stock data download for %s", ticker)
        return f"{ticker} ({period}) dummy summary"

    logger.info("Fetching %s price history for %s", period, ticker)
    data: pd.DataFrame = yf.download(ticker, period=period, progress=False)
    if data.empty:
        raise ValueError(f"No price data found for {ticker}")

    start_price = float(data["Close"].iloc[0])
    end_price = float(data["Close"].iloc[-1])
    pct_change = ((end_price - start_price) / start_price) * 100

    summary = (
        f"{period} closing price: {start_price:.2f} -> {end_price:.2f} "
        f"({pct_change:+.2f}%). Highest: {data['High'].max():.2f}, Lowest: {data['Low'].min():.2f}."
    )
    logger.debug("Stock summary for %s: %s", ticker, summary)
    return summary


def generate_script_for_ticker(
    ticker: str,
    company_name: str,
    *,
    period: str = "1mo",
    notion_page_id: Optional[str] = None,
    output_path: Optional[Path] = None,
    generator: Optional[PromptGenerator] = None,
    runtime_config: Optional[RuntimeConfig] = None,
) -> str:
    """
    Generate a script and optionally persist it to Notion or the filesystem.
    """
    runtime = runtime_config or RuntimeConfig.from_env()
    prompt_generator = generator or PromptGenerator(runtime=runtime)
    context = PromptContext(ticker=ticker, company_name=company_name, timeframe=period)
    stock_summary = fetch_stock_summary(ticker, period=period, dry_run=runtime.dry_run)
    script = prompt_generator.generate_script(context, stock_summary)

    artifact_path = output_path or Path("japan_stock_youtube_shorts") / "assets" / "templates" / f"{runtime.run_id}_{ticker}_script.md"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(script, encoding="utf-8")
    logger.info("Saved script to %s (run_id=%s)", artifact_path, runtime.run_id)

    if notion_page_id:
        try:
            updater.record_script(notion_page_id, script)
            updater.update_status(notion_page_id, "Script Generated")
        except Exception as exc:  # noqa: BLE001
            updater.log_exception(notion_page_id, exc)
            raise

    return script
