# agent_card_check.py
"""Agent Card 校验：拿到名片先验五类字段，再验该问的能力。

名片是写给机器读的：客户端拿到 Agent Card 之后按这张表逐项检查，
缺项的 Agent 直接从候选里剔除，而不是等委派出错再排查。
"""

def check(card):
    """返回缺项清单；全齐返回空列表。"""
    missing = []
    if not card.get("name") or not card.get("description"):
        missing.append("身份（name/description）")
    if not card.get("supportedInterfaces"):
        missing.append("服务地址（supportedInterfaces）")
    if not card.get("securitySchemes"):
        missing.append("安全要求（securitySchemes）")
    if not card.get("skills"):
        missing.append("技能列表（skills）")
    for s in card.get("skills", []):
        if len(s.get("description", "")) < 15:
            missing.append("技能描述太短（description 是触发器）")
    return missing


LAZY = {
    "name": "travel-agent",
    "description": "订机票",
    "skills": [{"id": "flight", "description": "帮你订机票"}],
}
STRICT = {
    "name": "travel-agent",
    "description": "预订国内航班，返回行程单与确认号",
    "supportedInterfaces": [
        {"url": "https://a.example", "protocolBinding": "JSONRPC"},
    ],
    "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}},
    "skills": [{
        "id": "flight-booking",
        "description": "预订国内单程或往返航班，输入出发地、目的地"
                       "与日期，输出行程单与确认号",
        "tags": ["travel", "flight"],
        "examples": ["下周四订一张北京飞上海的机票"],
    }],
}
m = check(LAZY)
print("糊弄卡缺项数：", len(m))
for x in m:
    print("  -", x)
print("规范卡缺项数：", len(check(STRICT)))
print("注：签名可选，未签名至今仍是常态，这道口子只堵了一半。")

# 输出：
# 糊弄卡缺项数： 3
#   - 服务地址（supportedInterfaces）
#   - 安全要求（securitySchemes）
#   - 技能描述太短（description 是触发器）
# 规范卡缺项数： 0
# 注：签名可选，未签名至今仍是常态，这道口子只堵了一半。