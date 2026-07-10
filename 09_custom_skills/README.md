# Step 09 - Custom Skills

这一课把前面形成的 AFSIM Agent 工作流固化成一份可复用 Skill。

Skill 不是新功能代码，而是给 AI Agent 使用的“专业操作手册”：

```text
什么时候触发
怎么选择 CLI / MCP
怎么验证 AFSIM 输出
遇到 Ollama 路径问题怎么处理
每一步完成后如何停下
```

## 目录

```text
afsim-scenario-agent/
  SKILL.md
  agents/openai.yaml
  references/workflow.md
  references/mcp.md
  scripts/check_afsim_agent_env.py
```

## 怎么验证

```powershell
cd D:\AFsim\Agent\09_custom_skills\afsim-scenario-agent
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\lenovo\.codex\skills\.system\skill-creator\scripts\quick_validate.py' .
python .\scripts\check_afsim_agent_env.py
```

成功标准：

```text
quick_validate.py 通过
check_afsim_agent_env.py 返回 0
ollama list 能看到 qwen2.5:0.5b
```

## 重点理解

第九步解决的是“把经验固化下来”。

前面我们已经有：

```text
CLI
RAG
本地模型
Agent loop
MCP tool
```

Skill 的作用是让后续 AI Agent 一开始就知道这些约束和入口，不需要每次重新摸索。
