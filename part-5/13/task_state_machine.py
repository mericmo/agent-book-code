# task_state_machine.py
"""Task 八态状态机：转移是否合法，用一张表机器检查。

终态不可逆是硬规则；working -> working 是合法自转移（进度更新）；
input-required 是中断态，补信息后从原处继续。
"""

TERMINAL = {"completed", "failed", "canceled", "rejected"}

# 转移表按正文那张图写（教学骨架，生产实现以官方 spec 为准）。
# auth-required 官方定义为非中断态（认证走带外），这里不建模成「挂起等回调」；
# 对应的「等多久算超时、超时走 failed 还是 canceled」是客户端在状态机外兜的。
NEXT = {
    "submitted": {"working", "rejected"},   # 受理阶段也可直接拒单
    "working": {"working", "input-required", "completed",
                "failed", "canceled", "rejected"},
    "input-required": {"working"},
}


def legal(src, dst):
    """返回 (是否合法, 非法原因)。"""
    if src in TERMINAL:
        return False, "终态不可逆"
    if dst in NEXT.get(src, set()):
        return True, ""
    return False, "转移不在状态机内"


CASES = [
    ("submitted", "working"),       # 正常受理
    ("submitted", "rejected"),      # 受理阶段拒单
    ("working", "working"),         # 进度更新
    ("working", "input-required"),  # 中途缺信息
    ("input-required", "working"),  # 补信息后原处继续
    ("completed", "working"),       # 终态不可逆
    ("rejected", "completed"),      # 拒单之后什么都不接
]
for src, dst in CASES:
    ok, reason = legal(src, dst)
    tag = "合法" if ok else f"非法（{reason}）"
    print(f"{src} -> {dst}".ljust(36), tag)

# 输出：
# submitted -> working                合法
# submitted -> rejected               合法
# working -> working                  合法
# working -> input-required           合法
# input-required -> working           合法
# completed -> working                非法（终态不可逆）
# rejected -> completed               非法（终态不可逆）