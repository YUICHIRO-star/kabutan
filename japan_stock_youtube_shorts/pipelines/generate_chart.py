"""
Generate a simple line chart image for a stock ticker.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from ..config import RuntimeConfig

logger = logging.getLogger(__name__)
plt.switch_backend("Agg")


def _default_output(ticker: str, run_id: str) -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "japan_stock_youtube_shorts" / "assets" / "templates" / "charts" / f"{run_id}_{ticker}_chart.png"


def download_history(ticker: str, period: str = "1mo", *, dry_run: bool = False) -> pd.DataFrame:
    logger.info("Downloading price history for %s (%s)", ticker, period)
    if dry_run:
        logger.info("[dry-run] Returning dummy price history for %s", ticker)
        dates = pd.date_range(end=pd.Timestamp.today(), periods=5)
        return pd.DataFrame({"Close": [1, 2, 3, 4, 5], "High": [1, 2, 3, 4, 5], "Low": [1, 2, 3, 4, 5]}, index=dates)
    data = yf.download(ticker, period=period, progress=False)
    if data.empty:
        raise ValueError(f"No data for ticker {ticker}")
    return data


def create_price_chart(ticker: str, *, period: str = "1mo", output_path: Optional[Path] = None, runtime_config: Optional[RuntimeConfig] = None) -> Path:
    """
    Generate a closing-price line chart and return the output path.
    """
    runtime = runtime_config or RuntimeConfig.from_env()
    history = download_history(ticker, period=period, dry_run=runtime.dry_run)
    output = output_path or _default_output(ticker, runtime.run_id)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))
    history["Close"].plot(ax=ax, color="#d81b60", linewidth=2)
    ax.set_title(f"{ticker} closing price ({period})")
    ax.set_ylabel("Price (JPY)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)

    logger.info("Chart saved to %s (run_id=%s)", output, runtime.run_id)
    return output
