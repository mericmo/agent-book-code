# mcp_wire.py —— MCP 线上跑的就是 JSON-RPC 2.0 报文：两个往返看清协议骨架（标准库即可运行）
# 结构按 spec 的 JSON-RPC 骨架还原，非官方实现；_meta 携带协议版本是 2026-07-28 起的无状态约定
import json

TOOLS = [{"name": "search_orders",
          "description": "搜索当前用户的历史订单。",
          "inputSchema": {"type": "object",
                          "properties": {"start_date": {"type": "string"},
                                         "end_date": {"type": "string"}},
                          "required": ["start_date", "end_date"]}}]

def server_handle(msg: dict):
    """一条请求进，一条响应出：请求带 id 必须回。"""
    if msg["method"] == "tools/list":
        return {"jsonrpc": "2.0", "id": msg["id"], "result": {"tools": TOOLS}}
    if msg["method"] == "tools/call":
        a = msg["params"]["arguments"]         # 参数是结构化来的，不是从文本里抠的
        text = f"返回 {a['start_date']} 至 {a['end_date']} 的订单 3 条"
        return {"jsonrpc": "2.0", "id": msg["id"],
                "result": {"content": [{"type": "text", "text": text}]}}
    return {"jsonrpc": "2.0", "id": msg["id"],
            "error": {"code": -32601, "message": "Method not found"}}

def request(mid, method, params=None):
    """2026-07-28 起：协议版本随每个请求在 _meta 中携带，不再有握手。"""
    return {"jsonrpc": "2.0", "id": mid, "method": method,
            "params": {**(params or {}),
                       "_meta": {"protocolVersion": "2026-07-28"}}}

for msg in [request(1, "tools/list"),
            request(2, "tools/call", {"name": "search_orders",
                                      "arguments": {"start_date": "2026-01-01",
                                                    "end_date": "2026-01-31"}})]:
    print("client ->", json.dumps(msg, ensure_ascii=False))
    print("server <-", json.dumps(server_handle(msg), ensure_ascii=False))

# 服务器也可以主动发通知：无 id，客户端不回复
push = {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"}
print("server ->", json.dumps(push, ensure_ascii=False), "  # 无 id，客户端不回复")

# 输出：
# client -> {"jsonrpc": "2.0", "id": 1, "method": "tools/list",
#            "params": {"_meta": {"protocolVersion": "2026-07-28"}}}
# server <- {"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "search_orders",
#            "description": "搜索当前用户的历史订单。", "inputSchema": {"type": "object",
#            "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}},
#            "required": ["start_date", "end_date"]}}]}}
# client -> {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name":
#            "search_orders", "arguments": {"start_date": "2026-01-01", "end_date":
#            "2026-01-31"}, "_meta": {"protocolVersion": "2026-07-28"}}}
# server <- {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text",
#            "text": "返回 2026-01-01 至 2026-01-31 的订单 3 条"}]}}
# server -> {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"}   # 无 id，客户端不回复