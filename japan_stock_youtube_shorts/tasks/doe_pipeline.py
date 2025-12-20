"""
Minimal, runnable steps for:
1) Generating a 60-character DOE explanation for beginners via OpenAI.
2) Adding the generated text as a new row in the Notion Video_Artifacts database.
"""

from __future__ import annotations

import os

from notion_client import Client
from openai import OpenAI


def generate_doe_summary() -> str:
    """
    Task 1: Call OpenAI (gpt-4o-mini) to produce a 60-character beginner-friendly DOE blurb.
    Prints the result and returns it.
    """
    api_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": "You are a concise Japanese tutor for finance beginners.",
        },
        {
            "role": "user",
            "content": "DOEを株初心者向けに60字で説明してください。必ず60字以内の日本語で。",
        },
    ]
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.4)
    text = response.choices[0].message.content.strip()
    print("=== Task1: OpenAI生成結果 ===")
    print(text)
    return text


def insert_into_notion_video_artifacts(content: str) -> None:
    """
    Task 2: Add a new row to the Video_Artifacts DB with the generated content.
    Prints the created Notion URL on success.
    """
    notion_token = os.environ["NOTION_API_KEY"]
    database_id = os.environ["NOTION_DATABASE_ID"]
    notion = Client(auth=notion_token)

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            # Title property (Notion requires at least one title field)
            "Name": {"title": [{"text": {"content": "DOE_script_2025-09-01"}}]},
            "artifact_id": {"rich_text": [{"text": {"content": "VID2025-09-001_script_v1"}}]},
            "artifact_type": {"select": {"name": "script"}},
            "content": {"rich_text": [{"text": {"content": content}}]},
            "status": {"status": {"name": "generated"}},
            "version": {"number": 1},
            "video_id": {"rich_text": [{"text": {"content": "VID2025-09-001"}}]},
        },
    )

    print("=== Task2: Notion登録完了 ===")
    print(f"Notion URL: {page['url']}")


if __name__ == "__main__":
    """
    Run the two tasks sequentially.
    - Requires OPENAI_API_KEY, NOTION_API_KEY, NOTION_DATABASE_ID to be set.
    """
    generated = generate_doe_summary()
    insert_into_notion_video_artifacts(generated)
