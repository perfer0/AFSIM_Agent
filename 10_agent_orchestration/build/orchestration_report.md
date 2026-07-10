# Step 10 Orchestration Report

Generated at: 2026-07-10T15:31:58

## Request

使用项目级入口运行一次完整 AFSIM EOIR 智能想定生成：

1. 读取项目 manifest。
2. 检查本地模型和 AFSIM 环境。
3. 调用第十步总控编排器。
4. 通过 MCP 调用本地 Agent。
5. 生成 AFSIM 脚本并运行 mission.exe。
6. 汇总项目级状态报告。

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
