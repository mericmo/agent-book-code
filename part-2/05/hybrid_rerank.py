# hybrid_rerank.py —— 混合检索（RRF）+ 交叉编码器重排的最小示意
from collections import defaultdict

# 统一语料库：doc_id -> 文本（两路检索器都返回 doc_id，重排时再取回文本）
CORPUS = {
    0: "错误码处理指南",
    1: "常见报错排查手册",
    2: "错误码 TS-999：鉴权失败，请检查密钥",
    3: "网络超时排查",
}

def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[int]:
    """混合检索的核心：把稠密、稀疏等多路【排序结果】用 RRF 合并。
    每路里排第 1 名记 1/(k+1) 分、第 2 名记 1/(k+2)…… 分数相加再降序。
    RRF 不依赖各路的原始分数量纲，这是它能稳健融合不同检索器的原因。"""
    score = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            score[doc_id] += 1.0 / (k + rank)
    return sorted(score, key=score.get, reverse=True)

def cross_encoder_score(query: str, doc: str) -> float:
    """交叉编码器（示意）：把查询和文档【拼在一起】再打分，
    而不是像双编码器那样【各自编码】。拼起来才能让模型「看见」查询与
    文档之间的词级交互——这正是重排比第一段检索更准、也更慢的原因。"""
    # 真实系统这里调一个 rerank 模型（如 bge-reranker / Cohere Rerank）
    exact = 1.0 if query in doc else 0.0        # 模拟它比粗排更看重「精确串」
    q_terms, d_terms = set(query.split()), set(doc.split())
    overlap = len(q_terms & d_terms) / max(1, len(q_terms))
    return overlap * 0.7 + exact * 1.0

def hybrid_pipeline(query: str, dense_hits: list[int], sparse_hits: list[int]) -> list[int]:
    """典型配置：稠密(embedding)+稀疏(BM25)各取 top-K，
    RRF 融合候选 → 交叉编码器精排 → 只留 top-N 给生成模型。
    dense_hits / sparse_hits 是两路检索器各自按相关度排好的 doc_id 列表。"""
    fused = reciprocal_rank_fusion([dense_hits, sparse_hits])       # 1. RRF 融合候选
    return sorted(fused, key=lambda i: cross_encoder_score(query, CORPUS[i]),
                  reverse=True)[:5]                                  # 2. 交叉编码器精排

# —— 跑一遍：精确匹配是稠密检索的盲区，BM25 恰好能命中 ——
dense_hits  = [0, 1, 3]   # 稠密：召回「语义相近」的错误码文档，但都抓不到 TS-999
sparse_hits = [2]         # 稀疏 BM25：精确命中 TS-999
top = hybrid_pipeline("TS-999", dense_hits, sparse_hits)
print("混合检索 + 重排后 top-1：", CORPUS[top[0]])
# 输出：混合检索 + 重排后 top-1： 错误码 TS-999：鉴权失败，请检查密钥