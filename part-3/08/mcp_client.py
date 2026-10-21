# mcp_client.py
# pip install "mcp[cli]"
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],
)

async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. 看服务端能力
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            resources = await session.list_resources()
            print("resources:", [str(r.uri) for r in resources.resources])

            # 2. 调用工具
            result = await session.call_tool(
                "search_orders",
                {
                    "start_date": "2026-01-01",
                    "end_date": "2026-03-31",
                    "status": "shipped",
                },
            )
            for block in result.content:
                if block.type == "text":
                    print("search_orders ->", block.text)

            # 3. 读取资源
            schema = await session.read_resource("orders://schema")
            for block in schema.contents:
                if hasattr(block, "text"):
                    print("orders://schema ->", block.text)

if __name__ == "__main__":
    asyncio.run(main())