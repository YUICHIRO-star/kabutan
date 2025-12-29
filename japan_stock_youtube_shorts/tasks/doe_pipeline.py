"""
Minimal, runnable steps for:
1) Generating a 60-character DOE explanation for beginners via OpenAI.
2) Adding the generated text as a new row in the Notion Video_Artifacts database.
"""
from __future__ import annotations

import os
from notion_client import Client
from japan_stock_youtube_shorts.openai.client import openai_client


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


def insert_new_page(content: str, version: int) -> None:
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    database_id = os.environ["NOTION_DATABASE_ID"]

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [
                    {"text": {"content": f"DOE_script_v{version}"}}
                ]
            },
            "artifact_id": {
                "rich_text": [
                    {"text": {"content": f"DOE_script_v{version}"}}
                ]
            },
            "artifact_type": {
                "select": {"name": "script"}
            },
            "Content": {
                "rich_text": [
                    {"text": {"content": content}}
                ]
            },
            "Status": {
                "status": {"name": "generated"}
            },
            "Version": {
                "number": version
            },
        },
    )

    print(f"New DOE script page created: {page['url']}")


def main() -> None:
    version = 1  # ← 次は 2, 3 と手で増やす
    text = generate_doe_summary()
    insert_new_page(text, version)


if __name__ == "__main__":
    main()
