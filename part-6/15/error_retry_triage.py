# error_retry_triage.py
"""错误分诊与全抖动退避：哪些错误该重试，退避时长怎么算。

看两件事：
1. 429 必须分诊：带 retry-after 是瞬时限流，退避重试；不带大概率是配额、账单满了，停止重试。
2. 没有 retry-after 时，用 full jitter 退避：sleep = random(0, cap)，防止所有 worker 同时重发造成惊群。
"""
import random

HANDLED_BY_HUMAN = {400: "改代码", 401: "改密钥", 402: "充钱"}

def triage(status, retry_after=None):
    """分诊：返回该错误的处置建议。"""
    if status in HANDLED_BY_HUMAN:
        return "不重试：" + HANDLED_BY_HUMAN[status]
    if status == 429:
        return "退避重试" if retry_after else "停止重试，报警到人"
    if status in (500, 504):
        return "重试：指数退避"
    if status == 529:
        return "重试：等更久（或上熔断）"
    return "不重试"

def full_jitter(cap):
    """全抖动退避：sleep = random(0, cap)。"""
    return round(random.uniform(0, cap), 2)

print(triage(400), "|", triage(402))
print(triage(429, retry_after=3), "|", triage(429))  # 带头的重试，不带的报警
print(triage(500), "|", triage(529))

print("\n全抖动退避（每次运行都不一样）：")
print([full_jitter(8) for _ in range(4)])

# 输出（你的输出可能不同，这恰好证明了 jitter 的作用）：
# 不重试：改代码 | 不重试：充钱
# 退避重试 | 停止重试，报警到人
# 重试：指数退避 | 重试：等更久（或上熔断）
#
# 全抖动退避（每次运行都不一样）：
# [3.74, 1.21, 6.58, 0.45]