# verification_tiers.py
"""三种验证通道的分级排序：能写规则的，绝不交给模型看。

同一批生成的 HTML 邮件、两条流水线：
  A 分级：规则 → 视觉 → LLM 评审
  B 全部交给 LLM 评审
比一比谁漏得多、谁花得多（成本为示意值：评审最贵，也最慢）。
"""
COST = {"规则": 0, "视觉": 1200, "评审": 2000}   # 每次检查的 token 成本，评审最贵也最慢
# 每个通道只对「自己能表达的缺陷」有效：规则判结构，视觉判布局，评审判模糊风格
CAN_CATCH = {"规则": {"缺标签"}, "视觉": {"布局塌"}, "评审": {"语气跑偏"}}

# (邮件, 缺陷类型)；None 表示本来就合格
EMAILS = [("E1", None), ("E2", "缺标签"), ("E3", "布局塌"), ("E4", "缺标签"),
          ("E5", "语气跑偏"), ("E6", None), ("E7", "缺标签"), ("E8", "布局塌")]


def run(channels):
    """按给定顺序过闸：过一关付一关的钱，缺陷被能表达它的通道拦下。"""
    caught = {c: 0 for c in channels}
    leaks, cost = [], 0
    for name, flaw in EMAILS:
        for ch in channels:
            cost += COST[ch]
            if flaw in CAN_CATCH[ch]:
                caught[ch] += 1
                break
        else:
            if flaw is not None:            # 谁也没认领的缺陷 = 漏检
                leaks.append(f"{name} {flaw}")
    return caught, leaks, cost


def show(tag, result):
    caught, leaks, cost = result
    detail = " / ".join(f"{c}拦下{n}" for c, n in caught.items() if n)
    print(f"{tag}：{detail}；漏检 {len(leaks)} 处，成本 {cost} token")
    if leaks:
        print(f"   漏掉的是：{'、'.join(leaks)}")


show("A 分级（规则→视觉→评审）", run(["规则", "视觉", "评审"]))
show("B 全部交给 LLM 评审", run(["评审"]))
print()
print("B 更贵，却漏掉了全部结构性缺陷：分级的价值不是省钱，是省漏")

# 输出：
# A 分级（规则→视觉→评审）：规则拦下3 / 视觉拦下2 / 评审拦下1；漏检 0 处，成本 12000 token
# B 全部交给 LLM 评审：评审拦下1；漏检 5 处，成本 16000 token
#    漏掉的是：E2 缺标签、E3 布局塌、E4 缺标签、E7 缺标签、E8 布局塌
#
# B 更贵，却漏掉了全部结构性缺陷：分级的价值不是省钱，是省漏