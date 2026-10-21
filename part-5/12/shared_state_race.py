# shared_state_race.py
"""共享内存的隐藏代价：两个 Agent 写同一份状态，更新会凭空消失。

三个演示用同一段交错顺序（A 读、B 读、A 写、B 写），输出可复现。
真实线程里顺序是随机的，这正是你没法靠「谁先谁后」保命的原因。
裸文件的 open + write 本身也不是原子的，读的一方可能读到写了一半的内容。
"""
import threading
class SharedState:
    """共享状态：value 是业务值，ver 是版本号。"""

    def __init__(self):
        self.value = 0
        self.ver = 0
        
def raw_read_write(st):
    """裸读改写：没有原子性，后写者覆盖先写者。"""
    a = st.value          # A 读到 0
    b = st.value          # B 也读到 0（A 还没写）
    st.value = a + 1      # A 写入 1
    st.value = b + 1      # B 写入 1，A 的更新被覆盖
    return st.value       # 期望 2，实际 1

def locked_read_write(st, lock):
    """临界区串行：锁把读改写变成不可分割的一段，B 只能等 A 写完再读。"""
    with lock:
        st.value += 1
    return st.value

def optimistic_commit(st, base_ver, delta):
    """版本号乐观并发：提交时发现版本已变就拒绝，调用方重读后重试。"""
    if base_ver != st.ver:
        return None       # 拒绝，谁也没被覆盖
    st.ver += 1
    st.value += delta
    return st.value

st = SharedState()
print("① 裸读改写：", raw_read_write(st), "（应为 2，一次更新凭空消失）")

st = SharedState()
lock = threading.Lock()
locked_read_write(st, lock)
locked_read_write(st, lock)
print("② 临界区串行：", st.value, "（两次更新都在, 0 + 1 + 1 = 2）")

st = SharedState()
v = st.ver
optimistic_commit(st, v, 1)
print("③ 拿旧版本提交：", optimistic_commit(st, v, 1), "（被拒绝）")
print("③ 重读后再提交：", optimistic_commit(st, st.ver, 1), "（成功）")

# 输出：
# ① 裸读改写： 1 （应为 2，一次更新凭空消失）
# ② 临界区串行： 2 （两次更新都在, 0 + 1 + 1 = 2）
# ③ 拿旧版本提交： None （被拒绝）
# ③ 重读后再提交： 2 （成功）
