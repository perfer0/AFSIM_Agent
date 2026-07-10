# Step 13 Capability Review

Generated at: 2026-07-10T18:25:41
Overall passed: True
Capabilities passed: 14/14

## 已具备能力

### PASS - JSON 到 AFSIM 脚本

能把结构化 JSON 转为 AFSIM 主控脚本，理解最小生成链路。

Evidence:
- `01_json_to_afsim_main/afsim_ai.py` exists=True bytes=5175
- `01_json_to_afsim_main/build/eoir_demo_generated.txt` exists=True bytes=793

### PASS - 平台实例生成

能生成平台实例、航线、执行脚本，并理解 AFSIM 平台展开。

Evidence:
- `02_generate_platform_instances/build/scenario_generated.txt` exists=True bytes=1515

### PASS - 组件库建模

能把平台类型、目标集、事件输出抽象成可复用组件。

Evidence:
- `03_component_library/components/platform_types/uav_eoir.json` exists=True bytes=266
- `03_component_library/components/target_sets/eoir_short_long_targets.json` exists=True bytes=938

### PASS - 本地模型生成 JSON

能用本地 Ollama 模型生成想定 JSON，并保留工程校验。

Evidence:
- `06_local_model_deployment/examples/local_model_drafted_scenario.json` exists=True bytes=984

Checks:
- `06_local_model_deployment/examples/local_model_drafted_scenario.json` expected `ollama`, actual `ollama`, passed=True

### PASS - 本地 RAG 知识检索

能把 AFSIM 模板知识放入本地知识库并用于生成上下文。

Evidence:
- `05_rag_knowledge_base/knowledge/afsim_snippets/eoir_platform_instance.md` exists=True bytes=717

### PASS - Agent 闭环

能完成 plan/retrieve/draft/validate/generate/run 的自动闭环。

Evidence:
- `07_agent_loop/build/agent_trace.json` exists=True bytes=1662
- `07_agent_loop/examples/agent_generated_scenario.json` exists=True bytes=1109

Checks:
- `07_agent_loop/examples/agent_generated_scenario.json` expected `ollama`, actual `ollama`, passed=True
- `07_agent_loop/build/agent_trace.json` expected `0`, actual `0`, passed=True

### PASS - MCP 工具封装

能把本地 Agent 暴露为标准 MCP 工具，供外部客户端调用。

Evidence:
- `08_mcp_tools/mcp_server.py` exists=True bytes=6816
- `08_mcp_tools/build/mcp_test_result.json` exists=True bytes=5061

### PASS - 定制 Skill

能把项目经验固化为 AI 可复用的专业操作手册。

Evidence:
- `09_custom_skills/afsim-scenario-agent/SKILL.md` exists=True bytes=2074
- `09_custom_skills/afsim-scenario-agent/references/workflow.md` exists=True bytes=1677

### PASS - 总控编排审计

能跨 Skill、MCP、Agent、AFSIM 做端到端审计。

Evidence:
- `10_agent_orchestration/build/orchestration_audit.json` exists=True bytes=326

Checks:
- `10_agent_orchestration/build/orchestration_audit.json` expected `True`, actual `True`, passed=True

### PASS - 项目级入口

能用一个项目入口统一查看状态、运行编排、生成报告。

Evidence:
- `11_project_integration/afsim_project.py` exists=True bytes=6715
- `11_project_integration/build/project_run_report.json` exists=True bytes=1025

Checks:
- `11_project_integration/build/project_run_report.json` expected `True`, actual `True`, passed=True

### PASS - 离线打包交付

能生成离线源码包、校验清单和恢复说明，并排除模型 blob。

Evidence:
- `12_offline_packaging/build/package_manifest.json` exists=True bytes=3044
- `12_offline_packaging/build/package_verify.json` exists=True bytes=194

Checks:
- `12_offline_packaging/build/package_verify.json` expected `True`, actual `True`, passed=True

### PASS - AFSIM 事件效果验收

能解析 .evt，将探测、目标覆盖和航迹生命周期转成任务效果证据。

Evidence:
- `21_event_evidence_analysis/event_evidence.py` exists=True bytes=12478
- `21_event_evidence_analysis/build/reference_verification.json` exists=True bytes=7841

Checks:
- `21_event_evidence_analysis/build/reference_verification.json` expected `True`, actual `True`, passed=True

### PASS - 可重复参数实验

能控制参数和随机种子，批量运行 AFSIM，并汇总任务指标与变异。

Evidence:
- `22_reproducible_experiments/experiment_runner.py` exists=True bytes=9521
- `22_reproducible_experiments/build/experiment_report.json` exists=True bytes=10072

Checks:
- `22_reproducible_experiments/build/experiment_report.json` expected `True`, actual `True`, passed=True

### PASS - 统一项目质量门禁

能用一个入口重复执行编译、JSON、单元测试、事件验收和参数实验。

Evidence:
- `23_project_quality_gate/quality_gate.py` exists=True bytes=5658
- `23_project_quality_gate/build/core_quality_report.json` exists=True bytes=6155

Checks:
- `23_project_quality_gate/build/core_quality_report.json` expected `True`, actual `True`, passed=True

## 下一阶段能力缺口

### 扩展想定类型

当前主要是 EOIR 侦察 demo，下一步需要扩展到雷达、通信、武器、电子战或多平台协同。

### 更强本地模型

qwen2.5:0.5b 已实测不满足工程要求；需要由 7B 候选模型通过固定回归集后才能成为生产基线。

### 真实 AFSIM 组件映射

当前组件库很小，后续要把真实平台库、传感器库、武器库、场景约束纳入 RAG 和校验。

### 人机协同审查

复杂军事仿真不能只靠模型，需要人工确认约束、参数和战术意图。

### 随机实验与统计推断

当前已有单次事件指标，下一步要管理随机种子、重复实验、参数扫描和置信区间。
