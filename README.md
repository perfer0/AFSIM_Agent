# AFSIM Agent Learning Project

这个目录按学习步骤组织，每一步一个独立文件夹。

## 目录

```text
01_json_to_afsim_main/           第一步：JSON -> AFSIM 主控脚本 -> mission.exe 验证
02_generate_platform_instances/  第二步：JSON -> AFSIM 平台实例 -> mission.exe 验证
03_component_library/            第三步：组件库 -> 场景 JSON -> AFSIM 脚本 -> mission.exe 验证
04_local_llm_json_generation/    第四步：自然语言 -> 本地模型/规则生成 JSON -> AFSIM 验证
05_rag_knowledge_base/           第五步：本地知识库检索 -> 场景 JSON -> AFSIM 验证
06_local_model_deployment/       第六步：本地大模型 -> 场景 JSON -> AFSIM 验证
07_agent_loop/                   第七步：Agent 闭环 -> 检索/生成/校验/修复/仿真
08_mcp_tools/                    第八步：MCP 工具 -> 标准协议调用本地 Agent
09_custom_skills/                第九步：Skill -> 固化 AFSIM Agent 工作流
10_agent_orchestration/          第十步：总控编排 -> Skill/MCP/Agent/AFSIM 审计
11_project_integration/          第十一步：项目入口 -> manifest/status/run/report
12_offline_packaging/            第十二步：离线打包 -> 源码包/清单/校验/恢复说明
13_capability_review/            第十三步：能力复盘 -> 证据化评估当前能力边界
14_next_scenario_types/          第十四步：多想定类型 -> 类型矩阵/组件需求/优先级
15_real_afsim_extension/         第十五步：真实扩展 -> 扫描 AFSIM demo 形成证据
16_model_upgrade/                第十六步：模型升级 -> 7B/14B 候选与验证门禁
17_human_review_workflow/        第十七步：人机审查 -> 任务/组件/参数/证据检查
18_final_project_summary/        第十八步：最终总结 -> 项目质量门禁总报告
```

## 当前路线

```text
CLI 先稳定生成和验证
MCP 再把 CLI 包成工具
Skill 固化 AFSIM 工作流程
Agent 最后负责任务拆解和多步调用
```

## 学习顺序

先看每一步目录里的 `README.md`，再看 `examples` 里的 JSON，最后看 `build` 里生成出来的 AFSIM 脚本。

后续每一步都会新建文件夹，例如：

```text
后续可继续扩展为真实雷达、通信、武器和电子战想定。
```
