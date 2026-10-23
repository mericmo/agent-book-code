# agent_loop.py —— 第 1 章 1.3「5 行代码看懂 Agent 的灵魂」可运行版
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 自动从当前目录向上查找 .env

client = OpenAI(api_key=os.getenv("MODEL_API_KEY"), base_url=os.getenv("MODEL_BASE_URL"))
MODEL = os.getenv("MODEL_NAME")


def get_weather(city: str) -> str:
    return f"{city}：晴，24℃"


TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询城市天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]


def execute(tool_calls) -> list[dict]:
    """执行工具调用，返回可回填的 tool 消息。"""
    return [
        {"role": "tool", "tool_call_id": c.id,
         "content": get_weather(**json.loads(c.function.arguments))}
        for c in tool_calls
    ]


def run(task: str) -> str:
    messages = [{"role": "user", "content": task}]         # ① 任务与目标
    while True:                                            # ② 核心：循环
        resp = client.chat.completions.create(             # ③ 模型决策（控制权在此）
            model=MODEL, messages=messages, tools=TOOLS
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:                             # ④ 停止标准
            return msg.content
        messages.append(msg)                               # ⑤ 决策回填
        messages += execute(msg.tool_calls)                # ⑤ 行动 + 观察回填


if __name__ == "__main__":
    print(run("杭州和北京今天天气怎么样？"))
