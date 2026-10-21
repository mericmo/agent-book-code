# parallel_tools.py —— 并行调用 harness 的两个必答题：依赖竞态与非幂等防重（标准库即可运行）
import asyncio

class Harness:
    def __init__(self):
        self.users = {}            # name -> user_id
        self.orders = []           # 已成订单，业务键防重用
        self.executed_ids = set()  # tool_call_id 防重：同一个 id 只执行一次

    async def execute(self, call: dict):
        cid = call["id"]
        if cid in self.executed_ids:          # 防线一：模型重发同一 tool_call_id，直接短路
            return f"[{cid} 已执行过，跳过]"
        self.executed_ids.add(cid)
        if call["name"] == "create_user":
            await asyncio.sleep(0.03)         # 创建走完整流程，明显慢于查询
            uid = f"u{len(self.users) + 1}"
            self.users[call["args"]["name"]] = uid
            return {"user_id": uid}
        if call["name"] == "search_user":     # 隐含依赖：要求用户已存在
            await asyncio.sleep(0.01)
            return self.users.get(call["args"]["name"], "NOT_FOUND（竞态命中：调用早于创建）")
        if call["name"] == "place_order":     # 非幂等工具，按业务键防重
            sku = call["args"]["sku"]
            if sku in self.orders:            # 防线二：同一商品拒绝重复下单
                return f"[sku {sku} 已下单，拒绝重复]"
            self.orders.append(sku)
            return f"下单成功：{sku}"

async def run(h: Harness, calls: list, concurrent: bool) -> dict:
    if concurrent:
        results = await asyncio.gather(*(h.execute(c) for c in calls))  # 无脑并发
    else:
        results = [await h.execute(c) for c in calls]                   # 按返回顺序保守串行
    return dict(zip((c["id"] for c in calls), results))  # 按 tool_call_id 对账回填

async def main():
    # 模型把有依赖的调用混进同一批：先建用户再查同一个用户，还把同一商品下了两次单
    batch = [{"id": "c1", "name": "create_user", "args": {"name": "王小明"}},
             {"id": "c2", "name": "search_user",  "args": {"name": "王小明"}},
             {"id": "c3", "name": "place_order",  "args": {"sku": "A1001"}},
             {"id": "c4", "name": "place_order",  "args": {"sku": "A1001"}}]
    print("无脑并发：", await run(Harness(), batch, concurrent=True))
    print("保守串行：", await run(Harness(), batch, concurrent=False))

asyncio.run(main())

# 输出：
# 无脑并发： {'c1': {'user_id': 'u1'}, 'c2': 'NOT_FOUND（竞态命中：调用早于创建）',
#             'c3': '下单成功：A1001', 'c4': '[sku A1001 已下单，拒绝重复]'}
# 保守串行： {'c1': {'user_id': 'u1'}, 'c2': 'u1', 'c3': '下单成功：A1001',
#             'c4': '[sku A1001 已下单，拒绝重复]'}