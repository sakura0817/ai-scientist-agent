import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL = os.getenv("QWEN_MODEL", "qwen-plus")


def call_qwen(messages, enable_search=False, temperature=0.4):
    extra_body = {}
    if enable_search:
        extra_body = {
            "enable_search": True,
            "search_options": {
                "search_strategy": "turbo"
            },
        }

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        extra_body=extra_body,
    )

    content = response.choices[0].message.content
    save_log(messages, content, enable_search)
    return content


def save_log(messages, content, enable_search):
    Path("logs").mkdir(exist_ok=True)
    log_item = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "model": MODEL,
        "enable_search": enable_search,
        "messages": messages,
        "response": content,
    }
    log_path = Path("logs") / "qwen_calls.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_item, ensure_ascii=False) + "\n")
