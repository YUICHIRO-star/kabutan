"""
Minimal, runnable steps for:
1) Generating a 60-character DOE explanation for beginners via OpenAI.
2) Adding the generated text as a new row in the Notion Video_Artifacts database.
"""
from __future__ import annotations
import os

from japan_stock_youtube_shorts.openai.client import openai_client
from japan_stock_youtube_shorts.notion.updater import update_property, update_status


def generate_doe_summary() -> str:
    client = openai_client()

    messages = [
        {
            "role": "system",
            "content": "You are a concise Japanese tutor for finance beginners.",
        },
        {
            "role": "user",
            "content": "DOEを株初心者向けに60字以内の日本語で説明してください。",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
    )

    text = response.choices[0].message.content.strip()
    print("=== Task1: OpenAI生成結果 ===")
    print(text)
    return text


def record_doe_script(page_id: str, content: str) -> None:
    update_property(
        page_id,
        "Content",
        {"rich_text": [{"text": {"content": content}}]},
    )
    update_status(page_id, "generated")


def main() -> None:
    page_id = os.environ["NOTION_PAGE_ID"]
    generated = generate_doe_summary()
    record_doe_script(page_id, generated)


if __name__ == "__main__":
    main()
