# Step 04 - Local LLM JSON Generation

这一课开始接近“智能想定生成”：用户输入自然语言需求，系统生成场景 JSON，再继续走校验、生成 AFSIM、运行验证。

当前环境不要求已经安装本地大模型。为了保证离线可学、可跑，本步骤提供两个生成器：

```text
rules   离线规则生成器，默认可用，用来模拟本地模型输出
ollama  本地 Ollama 兼容接口，等你安装本地模型后再用
```

## 为什么先做接口

本项目最终要走：

```text
自然语言
-> 本地模型生成 JSON
-> CLI 校验 JSON
-> CLI 生成 AFSIM
-> mission.exe 验证
```

如果一开始就追求模型效果，很容易变成“模型输出一段看起来像脚本的文本”，但工程上不可控。

所以本步骤先把模型输出限定为 JSON。模型以后只需要学会“选组件 + 填参数”。

## 目录

```text
requests/eoir_request.txt       用户自然语言需求
prompts/system_prompt.md        给本地模型看的系统提示词
components/                     从第三步继承来的组件库
examples/drafted_scenario.json  draft 命令生成的场景 JSON
build/main_generated.txt        生成的 AFSIM 主控脚本
build/scenario_generated.txt    生成的平台实例脚本
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\04_local_llm_json_generation

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py components

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py draft .\requests\eoir_request.txt

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\drafted_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\main_generated.txt
```

## 接本地模型

等本机有 Ollama 或兼容服务后，可以改用：

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py draft .\requests\eoir_request.txt --provider ollama --model qwen2.5:7b-instruct
```

这里访问的是本机地址：

```text
http://127.0.0.1:11434/api/generate
```

不需要互联网。

## 重点理解

`requests/eoir_request.txt` 是人话。

`examples/drafted_scenario.json` 是模型应该输出的结构化结果。

`validate` 是质量门禁。只要模型输出的 JSON 不符合组件库约束，就不能进入 AFSIM 生成。

这就是 AI 工程化的核心：模型可以生成，但程序必须验证。
