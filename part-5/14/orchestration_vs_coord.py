# orchestration_vs_coord.py
"""编排 vs 协调：买到灵活，付掉的是可复现性。

同一件三步骤的活，两种控制流各跑三遍，比轨迹。
"""
import random

STEPS = ["查资料", "写初稿", "审校"]

# 能力声明：谁能做哪一步。两个人都能查资料，谁来是运行时的事。
AGENTS = {
    "研究员A": {"查资料"},
    "研究员B": {"查资料"},
    "撰稿": {"写初稿"},
    "审校": {"审校"},
}

def orchestrated():
    """编排：谁做哪一步，开发者写死。跑一百遍，轨迹一字不差。"""
    plan = {"查资料": "研究员A", "写初稿": "撰稿", "审校": "审校"}
    return [f"{step}：{plan[step]}" for step in STEPS]

def coordinated():
    """协调：Agent 按能力认领，谁来由运行时定。"""
    log = []
    for step in STEPS:
        able = [name for name, skills in AGENTS.items() if step in skills]
        log.append(f"{step}：{random.choice(able)}")
    return log

random.seed(7)
print("编排跑三遍：")
for _ in range(3):
    print("   ", orchestrated())
print("协调跑三遍：")
for _ in range(3): # 如果协调次数多了，研究员A选中次数会约等于研究员B的情况
    print("   ", coordinated())

# 输出：
# 编排跑三遍：
#    ['查资料：研究员A', '写初稿：撰稿', '审校：审校']
#    ['查资料：研究员A', '写初稿：撰稿', '审校：审校']
#    ['查资料：研究员A', '写初稿：撰稿', '审校：审校']
# 协调跑三遍：
#    ['查资料：研究员B', '写初稿：撰稿', '审校：审校']
#    ['查资料：研究员A', '写初稿：撰稿', '审校：审校']
#    ['查资料：研究员B', '写初稿：撰稿', '审校：审校']
# 编排的轨迹可复现（可审计、好排错）；协调的轨迹每次可能不同（灵活，难复现）。