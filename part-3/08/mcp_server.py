# mcp_server.py
# pip install "mcp[cli]"
from mcp.server.fastmcp import FastMCP

# api_client = None  # 实际项目里换成你自己的客户端实例
class FakeApiClient:
    def query_orders(self, start_date, end_date, status):
        return f"我是查询到的订单: {start_date}~{end_date} status={status}"

    def get_schema(self):
        return "我是schema"

api_client = FakeApiClient()

mcp = FastMCP("orders-server")  # 服务器名，握手时上报

@mcp.tool()
def search_orders(start_date: str, end_date: str,
                  status: str = "all") -> str:
    """搜索当前用户的历史订单。

    Args:
        start_date: 起始日期，ISO 8601，如 2026-01-01
        end_date: 结束日期（含），必须晚于 start_date
        status: pending / shipped / delivered / cancelled / all
    """
    # 这里调你已有的内部 API —— 业务逻辑一行不用改
    return api_client.query_orders(start_date, end_date, status)

@mcp.resource("orders://schema")
def orders_schema() -> str:
    """订单库表结构（只读，供宿主按需挂载）"""
    return api_client.get_schema()

if __name__ == "__main__":
    mcp.run(transport="stdio")  # 本地运行；远程部署改为 streamable-http