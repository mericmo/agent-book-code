# skill_lint.py
"""SKILL.md 体检器：把 9.1.1 的规范约束与 9.4.3 的四条纪律脚本化。

启发式骨架，不是穷尽的 linter：泛词、负向排除、引用检查都基于子串匹配，
会误报也会漏报，挂 CI 前按 agentskills.io 规范补全正则，或改人工评审。
"""
import os
import re
import sys

NAME_MAX, DESC_MAX, BODY_MAX = 64, 1024, 500
VAGUE = ["帮助你", "完成工作", "相关任务", "各种", "等等"]


def parse_fm(fm):
    """极简 frontmatter 解析：支持 description 的 YAML 折行。"""
    d, key = {}, None
    for ln in fm.splitlines():
        m = re.match(r"^([A-Za-z-]+):\s*(.*)$", ln)
        if m:
            key, d[key] = m.group(1), m.group(2).strip()
        elif key and ln.startswith(" "):
            d[key] += " " + ln.strip()
    return d


def lint(skill_dir):
    """返回问题清单：P0 = 技能失效，P1 = 违反规范，P2 = 坏味道。"""
    name = os.path.basename(skill_dir)
    text = open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()
    issues = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return ["[P0] 缺少 YAML frontmatter：元数据缺失等于技能不存在"]
    fm, body = m.groups()
    d = parse_fm(fm)

    nm = d.get("name", "")
    if not re.fullmatch(rf"[a-z0-9-]{{1,{NAME_MAX}}}", nm):
        issues.append(f"[P1] name「{nm}」不合规：只允许小写字母/数字/连字符")
    if nm.strip("-") != nm or "--" in nm:
        issues.append("[P1] name 首尾或连续连字符：规范不允许")
    if nm != name:
        issues.append("[P1] name 与目录名不一致（规范要求同名）")

    desc = d.get("description", "")
    if not desc:
        issues.append("[P0] 缺 description：触发器缺失 = 永远不会被加载")
    else:
        if len(desc) > DESC_MAX:
            issues.append(f"[P1] description 超 {DESC_MAX} 字符上限")
        hit = next((w for w in VAGUE if w in desc), None)
        if hit:
            issues.append(f"[P2] description 含泛词「{hit}」：会到处误触发")
        if not re.search(r"不适[用于]|不含|除外", desc):
            issues.append("[P2] 没有负向排除：边界外的任务也会被吸进来")

    lines = [ln for ln in body.splitlines() if ln.strip()]
    if len(lines) > BODY_MAX:
        issues.append(f"[P1] 正文 {len(lines)} 行，超出 {BODY_MAX} 行软建议")
    for ref in re.findall(r"见 (references/[\w./-]+)", body):
        if not os.path.exists(os.path.join(skill_dir, ref)):
            issues.append(f"[P2] 引用的 {ref} 不存在（引用断裂）")
    for scr in re.findall(r"参见 (scripts/[\w./-]+\.py)", body):
        issues.append(f"[P2] 「参见 {scr}」是阅读不是执行：改成「运行」")
    return issues


if __name__ == "__main__":
    for d in sys.argv[1:]:
        result = lint(d)
        if result:
            print(f"◆ {os.path.basename(d)}：{len(result)} 处问题")
            for issue in result:
                print(f"   {issue}")
        else:
            print(f"◆ {os.path.basename(d)}：通过")

# 用法：python skill_lint.py <技能目录>。对一个真实坏技能体检的输出：
#
# ◆ pdf-tool-2026：7 处问题
#    [P1] name「pdf_tool_2026」不合规：只允许小写字母/数字/连字符
#    [P1] name 与目录名不一致（规范要求同名）
#    [P2] description 含泛词「帮助你」：会到处误触发
#    [P2] 没有负向排除：边界外的任务也会被吸进来
#    [P1] 正文 523 行，超出 500 行软建议
#    [P2] 引用的 references/forms.md 不存在（引用断裂）
#    [P2] 「参见 scripts/extract_fields.py」是阅读不是执行：改成「运行」