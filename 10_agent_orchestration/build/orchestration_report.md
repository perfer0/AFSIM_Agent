# Step 10 Orchestration Report

Generated at: 2026-07-10T15:28:35

## Request

编排一个完整的离线 AFSIM EOIR 侦察想定生成任务：

1. 检查本地环境是否可用。
2. 使用 MCP 工具调用本地 Agent。
3. 使用 qwen2.5:0.5b 生成场景 JSON。
4. 运行 mission.exe 验证。
5. 输出可审计报告。

场景要求：
蓝方一架 EOIR 无人机在 34:30:00n 116:00w 附近执行对地成像侦察，
目标是红方地面目标区，仿真时间不超过 20 分钟。

## Orchestration Path

```text
Skill constraints
  -> environment check
  -> MCP client
  -> MCP server tool: afsim_agent_run
  -> Step 07 Agent loop
  -> AFSIM mission.exe
  -> audit report
```

## Audit Status

```text
PASSED
```

## Key Evidence

```text
env_check_returncode = 0
mcp_returncode       = 0
draft_provider       = ollama
run_exit_code        = 0
events_complete      = True
```

## Artifacts

```text
MCP result      D:\AFsim\Agent\08_mcp_tools\build\mcp_test_result.json
Agent trace     D:\AFsim\Agent\07_agent_loop\build\agent_trace.json
Scenario JSON   D:\AFsim\Agent\07_agent_loop\examples\agent_generated_scenario.json
```

## MCP Stdout

```text
Agent trace: D:\AFsim\Agent\07_agent_loop\build\agent_trace.json
Retrieval context: D:\AFsim\Agent\07_agent_loop\build\retrieval_context.md
Scenario JSON: D:\AFsim\Agent\07_agent_loop\examples\agent_generated_scenario.json
AFSIM main: D:\AFsim\Agent\07_agent_loop\build\main_generated.txt
mission.exe exit code: 0
```
