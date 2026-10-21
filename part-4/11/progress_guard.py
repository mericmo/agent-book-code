# progress_guard.py
"""无进展检测器：三元组签名 + 三级处置。

签名 =（工具名，规范化参数，结果签名）。
同一签名连续出现：第 3 次轻推（注入提醒）、第 4 次断粮（拒绝执行）、
第 5 次急刹（剥离工具调用，有界降级交部分结果）。
参数要做规范化（键排序、空白归一），否则多一个空格就能骗过比对。
"""
import json


def normalize(args):
    """键排序 + 紧凑分隔符：语义相同的参数序列化成同一个串。"""
    return json.dumps(args, sort_keys=True, separators=(",", ":"))


def signature(tool, raw_args, result):
    # 这里假定 raw_args 是合法 JSON 串。真实实现要先做类型归一：
    # 入参可能是嵌套对象、非 JSON 标量或含不可序列化类型，json.loads 会抛异常。
    # 先 try json.loads，失败就退化为 str(raw_args) 再规范化。
    return (tool, normalize(json.loads(raw_args)), str(result))


def guard(history):
    """pre-execution guard：执行前判定放行、轻推、断粮还是急刹。"""
    same, prev = 0, None
    for i, sig in enumerate(history, 1):
        same = same + 1 if sig == prev else 1
        prev = sig
        if same >= 5:
            print(f"  第 {i} 轮：急刹，剥离工具调用，强制交部分结果（有界降级）")
        elif same >= 4:
            print(f"  第 {i} 轮：断粮，拒绝执行，返回纠错信号「与上一轮完全相同」")
        elif same >= 3:
            print(f"  第 {i} 轮：轻推，注入提醒「基于已有结果收尾」")
        else:
            print(f"  第 {i} 轮：放行")


ERR = "Error: connection refused"
guard([signature("run_query", '{"q": "SELECT 1"}', ERR)] * 5)

print()
raw1, raw2 = '{"q":"SELECT 1"}', '{"q": "SELECT 1"}'
print("原样字符串比对：", raw1 == raw2, "（冒号后多一个空格，语义相同的调用被判成不同）")
print("规范化后比对：",
      normalize(json.loads(raw1)) == normalize(json.loads(raw2)), "（骗不过签名）")

# 输出：
#   第 1 轮：放行
#   第 2 轮：放行
#   第 3 轮：轻推，注入提醒「基于已有结果收尾」
#   第 4 轮：断粮，拒绝执行，返回纠错信号「与上一轮完全相同」
#   第 5 轮：急刹，剥离工具调用，强制交部分结果（有界降级）
#
# 原样字符串比对： False （冒号后多一个空格，语义相同的调用被判成不同）
# 规范化后比对： True （骗不过签名）