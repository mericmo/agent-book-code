# rag_pipeline.py —— RAG 五段流水线的最小骨架（标准库即可运行）
import math
from collections import Counter

def chunk(text: str, size: int = 400, overlap: int = 60) -> list[str]:
    """第一段：分块。按固定长度切，留 overlap 保住跨块语境。
    生产里应优先按标题/段落这类文档结构切，并给每块带元数据。"""
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap          # 重叠区 10–20% 的简单实现
    return chunks

def build_vocab(chunks: list[str]) -> list[str]:
    """第二段（前半）：建词表。关键：语料和查询必须【共用同一份词表】，
    否则两边向量的维度/词序不一致，相似度算出来是错的。真实系统里这份
    词表由 embedding 模型固定——换模型就必须重建全库向量。"""
    return sorted({w for c in chunks for w in c.split()})

def vectorize(chunks: list[str], vocab: list[str]) -> list[list[float]]:
    """第二段（后半）：按词表把文本编码成向量。这里用「词频向量」占位——
    真实系统换成 embedding 模型（稠密）与 BM25（稀疏）两路，语义与精确
    匹配互补。"""
    def vec(c):
        cnt = Counter(c.split())
        return [cnt.get(w, 0) for w in vocab]
    return [vec(c) for c in chunks]

def _cos(a: list[float], b: list[float]) -> float:
    """余弦相似度（工具函数，抽出以免 retrieve / rerank 各写一份）。
    n == 0 返回 0 分——对应「空向量」或「两向量维度不一致」。真实系统这里
    必须显式校验维度一致并告警：换了 embedding 模型、旧向量却没重建，是
    经典生产事故，静默返回 0 分会让检索「看似正常、实则全错」。"""
    n = math.sqrt(sum(x*x for x in a) * sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / n if n else 0.0

def retrieve(query_vec, chunk_vecs, top_k: int = 5) -> list[int]:
    """第三段：检索（粗排）。双编码器：查询与文档【各自】编码后比余弦，
    快，但没有查询-文档交互。K 别贪心——取太多等于把第 4 章的语义干扰
    亲手塞回窗口。"""
    scored = sorted(enumerate(chunk_vecs),
                    key=lambda t: _cos(query_vec, t[1]), reverse=True)
    return [i for i, _ in scored[:top_k]]

def cross_encoder_score(query: str, doc: str) -> float:
    """交叉编码器（示意）：把查询和文档【拼在一起】再打分，而不是各自编码。
    真实系统这里调一个 rerank 模型（如 bge-reranker / Cohere Rerank）；
    示意用「精确串命中」的高权重，模拟它比粗排更准的那一档。"""
    exact = 1.0 if query in doc else 0.0
    q_terms, d_terms = set(query.split()), set(doc.split())
    overlap = len(q_terms & d_terms) / max(1, len(q_terms))
    return overlap * 0.7 + exact * 1.0

def rerank(hits: list[int], chunks: list[str], query: str) -> list[int]:
    """第四段：重排（精排）。关键在【换模型】：第一段用双编码器，这里换成
    交叉编码器重新打分——不是把第一段的分数再排一遍（那样等于没做重排，
    排序结果几乎不变）。真实系统只对这几十个候选做，慢而准。"""
    return sorted(hits, key=lambda i: cross_encoder_score(query, chunks[i]),
                  reverse=True)

def generate(query: str, top_chunks: list[str]) -> str:
    """第五段：生成。真实系统把重排后的块拼进 prompt，三条纪律：
    ① 锚定「先定位再作答」 ② 要求并校验引用 ③ 材料不足时允许弃权。"""
    return f"[锚定+引用+弃权] 基于 {len(top_chunks)} 块回答: {query}"

# —— 跑一遍 ——（此处语料已是小块；真实流水线从 chunk(long_doc) 开始）
docs   = ["ACME 营收 公司 简介",
          "ACME 公司 营收 2023 Q2 环比 增长 3%",
          "团队 同步 会"]
vocab  = build_vocab(docs)                     # 语料与查询共用的词表
vecs   = vectorize(docs, vocab)                # 第二段
qvec   = vectorize(["ACME 公司 营收"], vocab)[0]
hits   = retrieve(qvec, vecs, top_k=2)         # 第三段：粗排
ranked = rerank(hits, docs, "ACME 公司 营收")   # 第四段：换模型精排
print("检索候选：", hits, "→ 重排后：", ranked)   # 输出：[0, 1] → [1, 0]
print(generate("ACME 公司 营收", [docs[i] for i in ranked]))