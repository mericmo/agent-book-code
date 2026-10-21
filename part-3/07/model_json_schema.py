import openai
from pydantic import BaseModel, Field
from typing import Literal, Optional

class SearchOrdersArgs(BaseModel):
    """搜索当前用户的历史订单。"""
    start_date: str = Field(description="起始日期，ISO 8601 格式，如 2026-01-01")
    end_date: str = Field(description="结束日期（含），必须晚于 start_date")
    status: Optional[Literal["pending", "shipped", "delivered", "cancelled"]] = Field(
        default=None, description="按状态过滤，不传则返回全部状态"
    )

# 一行生成工具定义（OpenAI SDK）
tools = [openai.pydantic_function_tool(SearchOrdersArgs)]

# 或直接取 schema
search_orders_args = SearchOrdersArgs.model_json_schema()
print(search_orders_args)