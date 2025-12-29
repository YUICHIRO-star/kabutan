"""
Minimal, runnable steps for:
1) Generating a 60-character DOE explanation for beginners via OpenAI.
2) Adding the generated text as a new row in the Notion Video_Artifacts database.
"""
from __future__ import annotations

import os
from japan_stock_youtube_shorts.openai.client import openai_client
from japan_stock_youtube_shorts.notion.updater import update_property


def generate_doe_summary() -> str:
    client = openai_client()

    messages = [
        {"role": "system", "content": "You are a concise Japanese tutor for finance beginners."},
        {"role": "user", "content": "DOEを株初心者向けに60字以内の日本語で説明してください。"},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


def main() -> None:
    page_id = os.environ["NOTION_PAGE_ID"]
    text = generate_doe_summary()

    update_property(
        page_id=page_id,
        property_name="Content",
        value={"rich_text": [{"text": {"content": text}}]},
    )

    print("DOE summary written to Notion.")


if __name__ == "__main__":
    main()
