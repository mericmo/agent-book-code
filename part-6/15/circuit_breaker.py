# circuit_breaker.py
class Breaker:
    """熔断器：闭合 →（连败 N 次）打开 →（冷却期满）半开。
    探针成功回闭合，失败回打开。持续过载时，重试是浇汽油，熔断才是正解。"""
    def __init__(self, n=3, cooldown=60):
        self.n, self.cooldown = n, cooldown
        self.fails, self.state, self.opened_at = 0, "closed", None

    def allow(self, now):
        """该不该把这次请求发往上游。"""
        if self.state == "open":
            if now - self.opened_at >= self.cooldown:
                self.state = "half_open"  # 冷却期满，放探针
            else:
                return False              # 冷却中，直接降级
        return True

    def record(self, ok, now):
        """记录结果：半开态探针成功闭合、失败回打开。"""
        if self.state == "half_open":
            self.state, self.fails = ("closed" if ok else "open"), 0
            self.opened_at = None if ok else now
        elif not ok:
            self.fails += 1
            if self.fails >= self.n:
                self.state, self.opened_at = "open", now
        else:
            self.fails = 0


# 演示：连败 3 次触发熔断，冷却期满放探针，成功后恢复
b = Breaker(n=3, cooldown=60)
for _ in range(3): b.record(False, now=0)  # 三连败

print(b.state, b.allow(now=30))            # open False（冷却中，走降级）
print(b.allow(now=60))                     # True（冷却期满，放探针）
b.record(True, now=60)                     # 探针成功
print(b.state, b.allow(now=61))            # closed True