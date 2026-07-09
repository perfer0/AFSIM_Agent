# Step 06 - Local Model Deployment

这一课把第 4 步预留的本地模型接口真正落地到 Ollama 兼容接口。

## 这一步在学什么

前面已经完成：

```text
自然语言 -> 规则/检索生成 JSON -> AFSIM -> mission.exe
```

第 6 步开始变成：

```text
自然语言 -> 本地大模型 -> 场景 JSON -> validate -> generate -> mission.exe
```

大模型仍然不直接写 AFSIM txt。它只输出 JSON，CLI 负责校验和生成 AFSIM。

## 推荐本地模型

入门先用小模型：

```text
qwen2.5:0.5b
```

优点是下载小、启动快，适合验证本地链路。后续可以换：

```text
qwen2.5:7b-instruct
qwen2.5-coder:7b
deepseek-coder:6.7b
```

## 安装 Ollama

如果本机没有 `ollama` 命令，可以安装 Ollama for Windows。

常用方式：

```powershell
winget install Ollama.Ollama
```

安装后重新打开 PowerShell，检查：

```powershell
ollama --version
ollama list
```

拉取小模型：

```powershell
ollama pull qwen2.5:0.5b
```

## 模型文件放到 D 盘项目目录

本项目要求下载的模型文件放在：

```text
D:\AFsim\Agent\ollama\models
```

已经设置用户环境变量：

```powershell
OLLAMA_MODELS=D:\AFsim\Agent\ollama\models
```

如果以后重新打开电脑，发现 `ollama list` 看不到模型，先完全退出 Ollama，再重新打开。新下载的模型不要提交到 Git，仓库只提交代码、提示词、组件库和示例输出。

## 目录

```text
requests/eoir_local_model_request.txt
prompts/local_model_prompt.md
examples/local_model_drafted_scenario.json
components/
knowledge/
build/main_generated.txt
build/scenario_generated.txt
```

## 怎么运行

检查本地模型环境：

```powershell
cd D:\AFsim\Agent\06_local_model_deployment

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py doctor
```

调用本地模型生成 JSON：

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py draft .\requests\eoir_local_model_request.txt --provider ollama --model qwen2.5:0.5b --fallback-rules
```

如果 Ollama 不可用，`--fallback-rules` 会退回规则生成器，保证后续教学链路还能继续跑。

脚本访问 `127.0.0.1:11434` 时会绕过系统代理，避免本地 Ollama 请求被代理转发后返回 `502 Bad Gateway`。

验证并生成 AFSIM：

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\local_model_drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\local_model_drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\main_generated.txt
```

## 重点理解

本地大模型只是替换了 `draft` 这一步：

```text
draft: request.txt -> scenario.json
```

后面的质量门禁不变：

```text
validate -> generate -> run
```

这就是工程化 AI 的关键：模型可以换，但验证链路不能丢。
