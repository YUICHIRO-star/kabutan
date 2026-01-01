# Japan Stock YouTube Shorts Toolkit

Utilities for generating YouTube Shorts assets (scripts, charts, and videos) focused on Japanese equities.

## Project layout

```
japan-stock-youtube-shorts/    # symlink to the Python package for convenience
├── notion/                    # Notion API helpers
├── openai/                    # Prompt + code generation utilities
├── pipelines/                 # High-level orchestration
├── assets/
│   ├── templates/             # Chart exports and thumbnails
│   └── audio/                 # Voiceovers or TTS output
├── .env.example               # Environment variables (sample)
├── requirements.txt
└── main.py                    # CLI entrypoint
```

## Getting started

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` and fill in your API keys (or use GitHub Actions secrets):
   ```bash
   cp .env.example .env
   ```
3. Run a pipeline command, for example generate a script:
   ```bash
   python main.py script --ticker 7203.T --company トヨタ自動車
   ```

Other commands:
- `python main.py chart --ticker 7203.T` to export a PNG chart.
- `python main.py video --image path/to/chart.png --audio path/to/audio.mp3` to assemble a clip.
- `python main.py healthcheck` to verify OpenAI/Notion connectivity.

Common flags:
- `--dry-run` to avoid external API calls and writes (returns placeholders).
- `--run-id <id>` to pin artifact names to a specific identifier.
- `--log-level DEBUG` for verbose logging.

### Automation
- CI (`.github/workflows/ci.yml`): runs compile checks on push/PR and nightly.
- DOE sample pipeline (`.github/workflows/run-doe-pipeline.yml`): can be run manually or nightly to generate a short DOE explanation via OpenAI and add it to the Notion Video_Artifacts database  
  (requires `OPENAI_API_KEY`, `NOTION_API_KEY`, `NOTION_DATABASE_ID` secrets).
