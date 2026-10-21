# memory_write.py —— 记忆写入管线的四类决策（ADD / UPDATE / DELETE / NOOP）
# 简化判定：用「相似度 + 值冲突」。真实系统这一步由 LLM 完成（Mem0 的做法）。
import math

def cos(a: list[float], b: list[float]) -> float:
    n = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / n if n else 0.0

def decide(new: dict, existing: list[dict], sim_th: float = 0.85) -> tuple:
    """新事实进来，四选一：
    ADD    —— 找不到相近记忆，追加          （新事实）
    NOOP   —— 同一件事、同一个值，不必写    （重复；Mem0 的 NOOP 还含「无信息量不记」）
    DELETE —— 新事实明确否定旧事实          （如「我不再过敏了」）
    UPDATE —— 同一件事、值变了，覆盖        （记忆库不是只增的日志）"""
    best, best_sim = None, 0.0
    for m in existing:
        s = cos(new["vec"], m["vec"])
        if s > best_sim:
            best, best_sim = m, s
    if best is None or best_sim < sim_th:
        return "ADD", None                      # 没有相近记忆 → 新增
    if new["value"] == best["value"]:
        return "NOOP", best                     # 同一件事、同一个值 → 不动
    if new.get("negates"):
        return "DELETE", best                   # 明确否定 → 删除
    return "UPDATE", best                       # 同一件事、值变了 → 覆盖

# —— 跑一遍：用户三个月前说用 MySQL，今天说换成了 PostgreSQL ——
existing = [
    {"slot": "database", "value": "MySQL", "vec": [0.9, 0.1, 0.0]},
    {"slot": "city",     "value": "上海",  "vec": [0.1, 0.9, 0.0]},
]
new = {"slot": "database", "value": "PostgreSQL", "vec": [0.9, 0.12, 0.0]}
action, target = decide(new, existing)
print(f"决策：{action}  ← 命中已有记忆「{target['slot']} = {target['value']}」")

# 输出：决策：UPDATE  ← 命中已有记忆「database = MySQL」