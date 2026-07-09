# AFSIM Agent Learning Project

这个目录按学习步骤组织，每一步一个独立文件夹。

## 目录

```text
01_json_to_afsim_main/           第一步：JSON -> AFSIM 主控脚本 -> mission.exe 验证
02_generate_platform_instances/  第二步：JSON -> AFSIM 平台实例 -> mission.exe 验证
03_component_library/            第三步：组件库 -> 场景 JSON -> AFSIM 脚本 -> mission.exe 验证
04_local_llm_json_generation/    第四步：自然语言 -> 本地模型/规则生成 JSON -> AFSIM 验证
05_rag_knowledge_base/           第五步：本地知识库检索 -> 场景 JSON -> AFSIM 验证
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
06_local_model_deployment/
07_mcp_tools/
08_custom_skills/
09_agent_orchestration/
```
