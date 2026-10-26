# tools_demo.py
# DeepSeek 调用示例（OpenAI SDK 兼容）
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从当前目录向上查找 .env
client = OpenAI(api_key=os.getenv('MODEL_API_KEY'), base_url=os.getenv('MODEL_BASE_URL'))
def get_weather(location):
  # 模拟天气数据
  return f"查询到{location}今天的天气情况是：晴朗，温度24℃"
# 工具注册表：名字 -> 函数
TOOL_REGISTRY = {
    "get_weather": get_weather,
    # ...
}
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather of a location, the user should supply a location first.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"]
        }
    }
}]
# 第一轮：模型返回工具调用意图
messages = [{"role": "user", "content": "How's the weather in Hangzhou?"}]

response = client.chat.completions.create(model=os.getenv('MODEL_NAME'), messages=messages, tools=tools)

message = response.choices[0].message

tool = message.tool_calls[0] # 这里只考虑返回一个工具调用的情况
messages.append(message) # 关键：把 assistant 消息（含 tool_calls）追加进历史

# Harness 执行函数
fn = TOOL_REGISTRY[tool.function.name]        # 按名字取函数
args = json.loads(tool.function.arguments)    # 解析参数
result = fn(**args)                           # 执行

# 结果以 tool 消息回传
messages.append({"role": "tool", "tool_call_id": tool.id, "content": result})

# 第二轮
response = client.chat.completions.create(model=os.getenv('MODEL_NAME'), messages=messages, tools=tools)
print(response.choices[0].message.content)