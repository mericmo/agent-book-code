# tri_factor_memory.py —— Park 三因子检索公式的最小实现（标准库即可运行）
import math, time

def recency(last_access: float, now: float, decay: float = 0.995) -> float:
    """近期性：指数时间衰减。decay 是逐小时衰减系数，越久没被访问分数越低。"""
    return decay ** ((now - last_access) / 3600.0)

def relevance(a: list[float], b: list[float]) -> float:
    """相关性：查询与记忆的向量余弦相似度（复用第 5 章的检索口径）。"""
    n = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / n if n else 0.0

def score(mem: dict, query_vec: list[float], now: float,
          w: tuple = (0.4, 0.3, 0.3)) -> tuple:
    """三因子各自归一到 0–1 再加权求和。
    重要性是【写入时】由 LLM 打好的 1–10 分，存在记忆里，不是查询时临时算的。
    w 是三个权重，生产系统按业务调，不是照抄这组值。"""
    r = recency(mem["last_access"], now)
    i = mem["importance"] / 10.0
    q = relevance(query_vec, mem["vec"])
    return w[0] * r + w[1] * i + w[2] * q, (r, i, q)

now, H = time.time(), 3600.0
memory = [
    {"text": "用户偏好 PostgreSQL，不用 MySQL", "importance": 7,
     "last_access": now - 10*H,   "vec": [0.95, 0.05]},
    {"text": "用户三个月前提过用 MySQL",        "importance": 5,
     "last_access": now - 2000*H, "vec": [0.90, 0.10]},
    {"text": "用户提过公司有年度审计",          "importance": 2,
     "last_access": now - 200*H,  "vec": [0.02, 0.05]},
]
query_vec = [1.0, 0.0]          # 当前情境：正在讨论数据库选型
for m in sorted(memory, key=lambda m: score(m, query_vec, now)[0], reverse=True):
    s, (r, i, q) = score(m, query_vec, now)
    print(f"{s:.3f}  {m['text']}   [近期 {r:.3f} | 重要 {i:.1f} | 相关 {q:.3f}]")

# 输出：
# 0.890  用户偏好 PostgreSQL，不用 MySQL   [近期 0.951 | 重要 0.7 | 相关 0.999]
# 0.448  用户三个月前提过用 MySQL          [近期 0.000 | 重要 0.5 | 相关 0.994]
# 0.318  用户提过公司有年度审计            [近期 0.367 | 重要 0.2 | 相关 0.371]