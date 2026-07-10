# Step 08 - MCP Tools

这一课把第七步 Agent 包装成本地 MCP 工具。

前面第七步是：

```text
人直接运行 CLI -> Agent -> AFSIM
```

第八步变成：

```text
MCP Client -> MCP Server -> afsim_agent_run 工具 -> Agent -> AFSIM
```

## 这一步在学什么

MCP 的核心作用是把本地能力暴露成标准工具。

在这个 demo 里，MCP server 暴露两个工具：

```text
afsim_agent_run      调用第七步 Agent，生成并运行 AFSIM 想定
afsim_agent_status   读取最近一次 Agent 运行状态
```

大模型、RAG、校验、仿真仍由第七步 Agent 完成。MCP 只负责工具协议和调用边界。

## 目录

```text
mcp_server.py
mcp_client_test.py
requests/eoir_mcp_request.txt
build/mcp_request.txt
build/mcp_test_result.json
```

## 怎么验证

先确认 Ollama 能看到 D 盘模型：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
& 'C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe' list
```

运行 MCP 客户端测试：

```powershell
cd D:\AFsim\Agent\08_mcp_tools
python .\mcp_client_test.py
```

测试会做三件事：

```text
initialize
tools/list
tools/call afsim_agent_run
```

成功标准：

```text
draft_provider = ollama
mission.exe exit_code = 0
```

测试结果会保存到：

```text
build/mcp_test_result.json
```

## 重点理解

MCP 不是替代 Agent。

它解决的是“怎么让外部 AI 助手、IDE、桌面端或其他客户端，以统一方式调用你的本地能力”。

到这里，我们已经有了：

```text
CLI       第七步 Agent 可以命令行运行
MCP       第八步把 Agent 变成标准工具
RAG       Agent 内部会检索本地知识
本地模型  Ollama 负责离线生成 JSON
AFSIM     mission.exe 负责最终仿真验证
```
