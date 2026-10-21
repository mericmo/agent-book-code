# async_job_lifecycle.py
JOBS = {}  # 教学用进程内字典；生产应外置到数据库 / Redis，并考虑并发锁与定期归档
def submit(job_id, now):
    """幂等提交：客户端重试、消息重放，都不会开出第二个任务。
    注意：真实高并发下，依赖内存字典判断会有竞态，生产应依赖数据库唯一键或分布式锁。"""
    if job_id not in JOBS:
        JOBS[job_id] = {"state": "running", "start": now}
    return JOBS[job_id]["state"]

def query(job_id):
    """幂等查询：断线重连后再查，拿到的是同一个任务、同一个状态。"""
    return JOBS.get(job_id, {"state": "not_found"})["state"]

def sweep(now, ttl=3600):
    """超时清扫：卡死的任务兜底标记失败，别让轮询永远等下去。
    注：生产环境里标记为 failed_timeout 的旧任务应定期清理或归档，避免状态表无限膨胀。"""
    hit = [jid for jid, j in JOBS.items()
           if j["state"] == "running" and now - j["start"] > ttl]
    for jid in hit:
        JOBS[jid]["state"] = "failed_timeout"
    return hit

print(submit("job-1", now=0))    # running
print(submit("job-1", now=0))    # running（重放不再新建）
print(query("job-1"))            # running
print(sweep(now=4000))           # ['job-1']（超时兜底）
print(query("job-1"))            # failed_timeout