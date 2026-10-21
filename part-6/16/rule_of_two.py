# rule_of_two.py
# 动态探测：根据 Agent 此刻正在调用的工具，判断它触发了哪几条要素
TOOL_CAPABILITIES = {
	"read_local_db": {"private_data"},  # 读本地库：访问私有数据
	"fetch_webpage": {"untrusted"},  # 抓网页：处理不可信内容
	"send_email": {"act_out"},  # 发邮件：对外通信
}


def evaluate_session(tools_used):
	"""动态统计当前会话中，Agent 已经触碰过哪些要素。"""
	current_risks = set()
	for tool in tools_used:
		# 把当前工具带来的风险，合并进会话的总风险池
		current_risks.update(TOOL_CAPABILITIES.get(tool, set()))
	return current_risks


def guard(tools_used, next_tool):
	"""执行前守卫：模拟如果调用 next_tool，会不会凑齐三要素。"""
	current = evaluate_session(tools_used)
	next_risks = TOOL_CAPABILITIES.get(next_tool, set())
	
	# 如果加上即将调用的工具，风险凑齐了 3 条
	combined = current | next_risks
	if len(combined) > 2:
		return f"拦截：调用 {next_tool} 会导致三要素齐备 {combined}，必须人工审批"
	return f"放行：调用 {next_tool}，当前风险 {combined}"


# 场景演示：
print(guard(["read_local_db", "fetch_webpage"], "send_email"))
# 输出：拦截：调用 send_email 会导致三要素齐备 {'untrusted', 'act_out', 'private_data'}，必须人工审批

print(guard(["read_local_db"], "fetch_webpage"))
# 输出：放行：调用 fetch_webpage，当前风险 {'untrusted', 'private_data'}