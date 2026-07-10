# Step 10 - Agent Orchestration

这一课把前面的能力放到一个更高层的总控编排器里。

前面已经有：

```text
07_agent_loop      Agent 本体
08_mcp_tools       MCP 工具封装
09_custom_skills   Skill 操作手册
```

第十步做的是：

```text
Skill 约束
  -> 环境检查
  -> MCP 客户端
  -> MCP 工具
  -> Agent
  -> AFSIM
  -> 审计报告
```

## 这一步在学什么

Orchestration 不是再写一个模型，而是总控流程：

- 先确认环境是否可用。
- 再选择已有工具入口。
- 调用 MCP 工具，而不是直接跳进底层逻辑。
- 读取 Agent 产物。
- 判断本次任务是否真的成功。
- 输出可审计报告。

## 怎么运行

```powershell
cd D:\AFsim\Agent\10_agent_orchestration
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
python .\orchestrator.py .\requests\eoir_orchestration_request.txt
```

## 成功标准

```text
env_check_returncode = 0
mcp_returncode       = 0
draft_provider       = ollama
run_exit_code        = 0
events_complete      = True
```

## 产物

```text
build/environment_check.json
build/mcp_client_run.json
build/orchestration_audit.json
build/orchestration_report.md
```

## 重点理解

现在你的系统开始分层：

```text
Skill:      告诉 AI 怎么做
MCP:        把能力暴露成工具
Agent:      负责检索、生成、校验、修复、运行
CLI:        可重复运行和验证
AFSIM:      最终仿真裁判
```

这就是后面做更复杂想定生成的基础结构。
