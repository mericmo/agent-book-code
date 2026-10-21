# skills_trigger.py
"""description 是触发器：同一份技能、两种写法，在同一个任务集上的表现。

一级元数据常驻（约 100 token/技能），description 命中才付二级正文的钱。
真实系统由模型判断匹配；这里用「触发词命中即触发」做可复现的替身。
"""
META_TOKENS = 100      # 一级：name + description，启动时常驻
BODY_TOKENS = 1800     # 二级：SKILL.md 正文

# 同一份 PDF 技能，两种 description 写法
VAGUE = "帮助你完成工作，处理文档相关的任务。"
TIGHT = ("处理 PDF 文件的拆分、合并与表单字段提取。当用户提到 PDF 表单、发票、"
         "合同字段提取时使用。不适用于纯文本阅读或格式转换。")

# 从 description 里抽出的触发词：模糊版只能抽到泛词，精准版抽到领域词
VAGUE_WORDS = ["工作", "文档", "任务", "处理"]
TIGHT_WORDS = ["PDF", "表单", "发票", "合同"]

TASKS = [
    ("帮我把合同里的甲方填到 PDF 表单里", True),
    ("把这份发票的字段提取出来",         True),
    ("写一段 Python 代码做二分查找",      False),
    ("整理今天的会议纪要文档",           False),
    ("处理一下这个报错日志",             False),
]


def fires(words, task):
    return any(w in task for w in words)


def report(name, words):
    fired = [t for t, _ in TASKS if fires(words, t)]
    right = sum(1 for t, s in TASKS if fires(words, t) == s)
    useful = sum(1 for t, s in TASKS if fires(words, t) and s)
    cost = META_TOKENS + len(fired) * BODY_TOKENS
    waste = (len(fired) - useful) * BODY_TOKENS
    print(f"{name}：触发 {len(fired)}/5，判定正确 {right}/5，"
          f"本轮成本 {cost} token（其中浪费 {waste}）")
    for t, should in TASKS:
        f = fires(words, t)
        flag = "OK" if f == should else "!!"
        print(f"  [{flag}] {'触发  ' if f else '不触发'}｜应"
              f"{'触发' if should else '不触发'}｜{t}")


report("模糊写法", VAGUE_WORDS)
print()
report("精准写法", TIGHT_WORDS)

# 输出：
# 模糊写法：触发 2/5，判定正确 1/5，本轮成本 3700 token（其中浪费 3600）
#   [!!] 不触发｜应触发｜帮我把合同里的甲方填到 PDF 表单里
#   [!!] 不触发｜应触发｜把这份发票的字段提取出来
#   [OK] 不触发｜应不触发｜写一段 Python 代码做二分查找
#   [!!] 触发  ｜应不触发｜整理今天的会议纪要文档
#   [!!] 触发  ｜应不触发｜处理一下这个报错日志
#
# 精准写法：触发 2/5，判定正确 5/5，本轮成本 3700 token（其中浪费 0）
#   [OK] 触发  ｜应触发｜帮我把合同里的甲方填到 PDF 表单里
#   [OK] 触发  ｜应触发｜把这份发票的字段提取出来
#   [OK] 不触发｜应不触发｜写一段 Python 代码做二分查找
#   [OK] 不触发｜应不触发｜整理今天的会议纪要文档
#   [OK] 不触发｜应不触发｜处理一下这个报错日志