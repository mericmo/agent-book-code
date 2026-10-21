# goal_evaluator.py
"""还原 /goal 的完成判定：评估器只读 transcript，不查世界。

同一个目标条件“tests passed 出现在对话里”，两个世界：
  A：工作模型真跑了测试，把输出写进了对话；
  B：工作模型没跑测试，只在对话里说了一句“测试都过了”。
评估器对两个世界给出同样的答案：它判得了对话，判不了世界。
"""

def evaluator(transcript, goal="tests passed"):
    """官方文档的边界：评估器不执行工具、不读文件，只读对话记录。"""
    return any(goal in text for _, text in transcript)


WORLD_A = [("assistant", "运行 pytest test/auth，3 passed in 0.42s（tests passed）")]
WORLD_B = [("assistant", "tests passed，任务完成。")]   # 没跑测试，只是说了

for name, world in (("A（真跑了测试）", WORLD_A), ("B（只是说了）", WORLD_B)):
    print(f"世界{name} → 评估器判定：{'完成' if evaluator(world) else '未完成'}")

print("两个世界拿到同一个『完成』：模型没把证据端进对话时，评估器就瞎了；")
print("端进去的是假证据时，评估器照样放行。副作用真发生了没，得靠后置条件断言。")

# 输出：
# 世界A（真跑了测试） → 评估器判定：完成
# 世界B（只是说了） → 评估器判定：完成
# 两个世界拿到同一个『完成』：模型没把证据端进对话时，评估器就瞎了；
# 端进去的是假证据时，评估器照样放行。副作用真发生了没，得靠后置条件断言。