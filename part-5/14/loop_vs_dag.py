# loop_vs_dag.py
"""环：DAG 与 Agent 图之间差的那一个字。

同一段「生成、测试、没过就回头改」的循环，两种表达都跑一遍。
"""

FAILS = 2                      # 前两次测试不过，第三次通过（模拟真实收敛）


def test(attempt):
    return attempt > FAILS


# ① DAG：图上没有环，重试次数只能写死在编排层
def dag(max_tries):
    for attempt in range(1, max_tries + 1):
        if test(attempt):
            return f"passed（第 {attempt} 轮）"
    return f"gave_up（跑满 {max_tries} 轮就放弃）"


# ② Agent 图：一条回边跑到收敛，上限只当刹车
def agent_graph(recursion_limit):
    attempt = 0
    while attempt < recursion_limit:
        attempt += 1
        if test(attempt):
            return f"passed（第 {attempt} 轮）"
    return f"hit_recursion_limit（{recursion_limit}）"


print("DAG  max_tries=2 :", dag(2))
print("DAG  max_tries=9 :", dag(9))
print("Agent 图 limit=25:", agent_graph(25))

# 输出：
# DAG  max_tries=2 : gave_up（跑满 2 轮就放弃）
# DAG  max_tries=9 : passed（第 3 轮）
# Agent 图 limit=25: passed（第 3 轮）
# 次数是猜的：写少了提前放弃，写多了白烧 token；
# 回边跑到收敛才停，上限只当刹车。