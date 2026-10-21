# validation_loop.py —— 校验闭环：报错不是异常路径，是给模型的纠错信号（pydantic 即可运行）
import json
from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError, model_validator

class SearchOrdersArgs(BaseModel):
    """搜索当前用户的历史订单。"""
    start_date: str = Field(description="起始日期，ISO 8601 格式，如 2026-01-01")
    end_date: str = Field(description="结束日期（含），必须晚于 start_date")
    status: Optional[Literal["pending", "shipped", "delivered", "cancelled"]] = Field(
        default=None, description="按状态过滤，不传则返回全部状态")

    @model_validator(mode="after")     # 业务级约束：schema 的 type/enum 表达不了
    def check_range(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date 必须晚于 start_date")
        return self

def execute(args: SearchOrdersArgs) -> str:
    tail = f"、状态 {args.status}" if args.status else ""
    return f"返回 {args.start_date} 至 {args.end_date}{tail} 的订单 3 条"

def mock_llm(messages: list) -> dict:
    """桩模型：第一轮把日期填反、枚举值编造；见过报错后按 hint 自纠。
    真实系统里这一步是一次 API 调用，闭环结构与此完全相同。"""
    if any(m["role"] == "tool" for m in messages):
        return {"name": "search_orders",
                "arguments": {"start_date": "2026-01-01", "end_date": "2026-01-31",
                              "status": "shipped"}}
    return {"name": "search_orders",
            "arguments": {"start_date": "2026-03-01", "end_date": "2026-02-01",
                          "status": "Processing"}}

messages = [{"role": "user", "content": "查一下我 1 月的订单"}]
for round_no in (1, 2, 3):
    call = mock_llm(messages)
    print(f"第 {round_no} 轮 模型给参：{json.dumps(call['arguments'], ensure_ascii=False)}")
    try:
        args = SearchOrdersArgs(**call["arguments"])
        print("  校验通过 ->", execute(args))
        break
    except ValidationError as e:
        # 关键动作：把结构化报错整理成 tool 消息喂回，而不是当异常抛掉
        feedback = json.dumps({"error": "参数校验失败",
                               "detail": e.errors(include_url=False, include_context=False),
                               "hint": "请按 detail 修正参数后重新调用"},
                              ensure_ascii=False, default=str)
        print("  校验失败 -> 喂回模型：", feedback)
        messages.append({"role": "tool", "tool_call_id": "call_1", "content": feedback})

# 输出：
# 第 1 轮 模型给参：{"start_date": "2026-03-01", "end_date": "2026-02-01", "status": "Processing"}
#   校验失败 -> 喂回模型： {"error": "参数校验失败", "detail": [{"type": "literal_error",
#     "loc": ["status"], "msg": "Input should be 'pending', 'shipped', 'delivered' or 'cancelled'",
#     "input": "Processing"}], "hint": "请按 detail 修正参数后重新调用"}
# 第 2 轮 模型给参：{"start_date": "2026-01-01", "end_date": "2026-01-31", "status": "shipped"}
#   校验通过 -> 返回 2026-01-01 至 2026-01-31、状态 shipped 的订单 3 条