# shell_injection.py —— 军规四第一课：43% 命令注入的根因就是字符串拼接（标准库即可运行）
import subprocess

repo = "demo & echo PWNED"    # 模型给的“参数”，里头藏了第二条命令（分号、&&、反引号同理）

# 危险写法：f-string 拼进 shell=True —— 43% 审计样本里的同款写法
r1 = subprocess.run(f"git log {repo}", shell=True, capture_output=True, text=True)
print("拼接写法 stdout：", repr(r1.stdout))            # 第二条命令被执行了
print("拼接写法 returncode：", r1.returncode)          # git 明明失败了，退出码却是 0

# 安全写法：参数列表 + shell=False，注入串只是个查无此库的普通参数
r2 = subprocess.run(["git", "log", repo], shell=False, capture_output=True, text=True)
print("列表写法 stdout：", repr(r2.stdout))            # 空的，谁也没执行
print("列表写法 returncode：", r2.returncode)          # git 如实报告失败

# 输出：
# 拼接写法 stdout： 'PWNED\n'
# 拼接写法 returncode： 0
# 列表写法 stdout： ''
# 列表写法 returncode： 128