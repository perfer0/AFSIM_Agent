# Step 07 - Agent Loop

这一课把前面的能力串成一个最小 Agent。

第六步已经做到：

```text
自然语言 -> 本地模型 -> 场景 JSON -> validate -> generate -> mission.exe
```

第七步升级为：

```text
用户需求
  -> plan
  -> retrieve 本地知识
  -> draft 场景 JSON
  -> validate
  -> repair
  -> generate AFSIM txt
  -> run mission.exe
```

## 这一步在学什么

Agent 不是一个新模型，而是一个带状态的工作流。

在这个 demo 里：

- `plan`：写入本次任务计划。
- `retrieve`：从 `knowledge/` 检索 AFSIM 片段，这是本地 RAG 的最小形态。
- `draft`：调用本地 Ollama 模型生成 JSON。
- `validate`：用工程规则检查 JSON 是否能生成 AFSIM。
- `repair`：如果 JSON 不合格，让模型按错误列表修复。
- `generate`：把 JSON 转成 AFSIM txt。
- `run`：调用 `mission.exe` 做最终验证。

## 目录

```text
agent_loop.py
afsim_ai.py
requests/eoir_agent_request.txt
prompts/agent_draft_prompt.md
prompts/agent_repair_prompt.md
knowledge/
components/
examples/agent_generated_scenario.json
build/agent_trace.json
build/retrieval_context.md
build/main_generated.txt
build/scenario_generated.txt
```

## 怎么运行

先确认 Ollama 已经能看到本地模型：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
& 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe' list
```

运行第七步 Agent：

```powershell
cd D:\AFsim\Agent\07_agent_loop
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
python .\agent_loop.py agent .\requests\eoir_agent_request.txt --model qwen2.5:0.5b --fallback-rules --run
```

看 Agent 执行轨迹：

```powershell
Get-Content .\build\agent_trace.json -Encoding UTF8
```

看 RAG 检索上下文：

```powershell
Get-Content .\build\retrieval_context.md -Encoding UTF8
```

## 重点理解

这一层的价值是可控：

```text
模型负责生成候选答案
程序负责检索、校验、修复、落盘和仿真验证
```

如果模型输出错了，不直接信它，而是进入 `validate -> repair`。

这就是后续做 MCP、Skill、CLI 的基础：先把一个可靠的本地工具链跑通，再把它包装成更通用的工具。
