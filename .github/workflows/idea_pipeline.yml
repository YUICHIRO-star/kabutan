"""
Task:
1) 前回テーマをもとに次の動画アイデア案をOpenAIで生成
2) Notion Video_Artifacts データベースに新規ページとして保存
"""

from __future__ import annotations

import os
from notion_client import Client
from japan_stock_youtube_shorts.openai.client import openai_client


def generate_next_ideas(previous_topic: str) -> str:
    """
    株初心者向け Shorts の次テーマ案を3つ生成する
    """
    client = openai_client()

    messages = [
        {
            "role": "system",
            "content": "You are an editor for Japanese stock beginners YouTube Shorts.",
        },
        {
            "role": "user",
            "content": f"""
あなたは「株初心者向けYouTube Shorts」の編集者です。

条件：
- 60秒以内のShorts向け
- 日本株・指標・考え方が対象
- 難解な専門用語は避ける

直近で扱ったテーマ：
「{previous_topic}」

この次に扱うと理解が深まるテーマ案を3つ出してください。

出力形式：
1. テーマ名：
   狙い：
""",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


def insert_idea_into_notion(content: str, version: int = 1) -> None:
    """
    アイデア案を Notion に新規ページとして保存
    """
    notion = Client(auth=os.environ["NOTION_API_KEY"])
    database_id = os.environ["NOTION_DATABASE_ID"]

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [
                    {"text": {"content": f"IDEA_{version:02d}"}}
                ]
            },
            "Artifact_Type": {
                "select": {"name": "idea"}
            },
            "Content": {
                "rich_text": [
                    {"text": {"content": content}}
                ]
            },
            "Status": {
                "status": {"name": "proposed"}
            },
            "Version": {
                "number": version
            },
        },
    )

    print("Idea page created:")
    print(page["url"])


def main() -> None:
    previous_topic = "DOE（株主資本配当率）"
    version = 1

    ideas = generate_next_ideas(previous_topic)
    insert_idea_into_notion(ideas, version)


if __name__ == "__main__":
    main()
