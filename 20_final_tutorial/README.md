# AFSIM 离线智能想定生成：从零到工程基线

这套教程面向第一次接触 AI 工程和 AFSIM 自动化的人。完成后，你应当能解释并亲手维护以下完整链路：

```text
自然语言需求
  -> 本地知识检索（RAG）
  -> 本地模型生成受约束 JSON
  -> 组件白名单与规则校验
  -> 模型修复（最多两次）
  -> 确定性代码生成 AFSIM 文本
  -> mission.exe 实跑
  -> 语义评测、审计报告与人工复核
```

## 1. 先理解核心判断

`0.5B` 模型的价值是快速确认 Ollama、API、模型目录和 JSON 通路正常。它参数量太小，面对长约束、多平台关系、参数一致性和错误修复时稳定性不足，因此不能把“偶尔生成一个可运行样例”当作工程能力。

本机 RTX 5060 Laptop GPU 有 8GB 显存。`qwen2.5:7b` 在 Ollama 中约 4.7GB，是更现实的本地基线；14B 版本约 9GB，仅模型权重就超过显存，容易部分卸载到内存并显著变慢。因此先对 7B 做实测，不按参数量想当然。

工程系统也不能只依赖“大一点的模型”。可靠性来自约束、校验、回归测试和证据链，模型只是其中一个不确定组件。

## 2. CLI、MCP、Skill、Agent、RAG 的关系

它们不是五套必须同时搭建的模型，而是不同职责：

| 层 | 解决什么问题 | 本项目位置 |
|---|---|---|
| CLI | 最稳定、最容易测试的执行入口 | `07_agent_loop/agent_loop.py` |
| RAG | 按本地目录、中文术语和关键词检索 AFSIM 组件证据 | `07_agent_loop/knowledge/` |
| Agent | 串联检索、生成、校验、修复、仿真 | `07_agent_loop/agent_loop.py` |
| MCP | 让其他 AI 客户端以标准工具协议调用 CLI | `08_mcp_tools/` |
| Skill | 固化操作规范、边界和入口说明 | `09_custom_skills/` |

正确建设顺序是先把 CLI 和确定性生成器做稳，再加 RAG 和 Agent，最后按集成需要接 MCP 与 Skill。MCP 和 Skill不会提升模型智力，它们提升的是复用、接口标准化和操作一致性。

## 3. 环境和目录

固定路径：

```text
D:\AFsim\Agent                                      项目与模型数据
D:\AFsim\Agent\ollama\models                       Ollama 模型存储
D:\AFsim\AFSim\afsim-2.9.0-win64\bin\mission.exe  AFSIM 执行器
```

每次新开 PowerShell 先执行：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
```

如果 Ollama 已经在设置变量之前启动，必须重启服务，因为服务进程不会自动继承后来设置的变量：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
$ollama='C:\Users\lenovo\AppData\Local\Programs\Ollama\ollama.exe'
Get-Process | Where-Object { $_.ProcessName -like 'ollama*' } | Stop-Process -Force
Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
```

确认模型确实在 D 盘服务中：

```powershell
& $ollama list
```

应同时看到 `qwen2.5:0.5b` 和 `qwen2.5:7b`。模型 blob 被 `.gitignore` 排除，不能推送到 GitHub。

## 4. 为什么使用 JSON 中间表示

让模型直接生成 AFSIM 文本有三个问题：语法容易幻觉、组件引用不可控、错误难以定位。当前系统让模型只决定“想定意图和参数”，确定性 Python 代码负责渲染 AFSIM 文本。

JSON 还要经过三层约束：

1. Ollama `format` 使用 JSON Schema，从解码阶段限制结构。
2. `validate_scenario()` 检查必填字段、组件白名单、本地 include、side、时间单位等。
3. 第 19 步对用户需求做语义断言，例如指定坐标是否保留、航点数量和成像次数是否满足。

只有 `mission.exe` 返回 0 仍然不够。它主要证明语法和引用可执行，不证明军事意图、参数口径或任务效果正确，所以最后仍需人工复核。

## 5. 第一次工程运行

先做环境诊断：

```powershell
cd D:\AFsim\Agent\19_engineering_baseline
python .\engineering_benchmark.py doctor
```

`passed: true` 才继续。然后运行 7B 工程评测：

```powershell
python .\engineering_benchmark.py benchmark --models qwen2.5:7b
```

评测不会启用规则兜底。每个样例必须同时满足：

- 本地模型确实生成 JSON；
- JSON 通过结构与组件校验；
- 用户参数和动作次数通过语义断言；
- AFSIM `mission.exe` 返回 0；
- `draft_provider` 不是任何 rules fallback。

查看结果：

```powershell
Get-Content .\build\benchmark_report.md -Encoding UTF8
```

每个样例都保留 `scenario.json`、`agent_trace.json`、`main_generated.txt`、`scenario_generated.txt` 和仿真日志，便于定位失败属于模型、校验器、生成器还是 AFSIM。

RAG 的每条检索结果还会记录本地来源和 SHA-256。这样可以回答“模型生成时参考了哪份知识、那份知识当时是否发生变化”。当前知识库很小，使用可解释的目录加权检索比引入向量数据库更合适；当文档扩展到大量手册和 demo 后，再增加本地 embedding 与混合检索，并用召回率评测决定是否升级。

## 6. 0.5B 与 7B 对比

要用相同数据公平比较：

```powershell
python .\engineering_benchmark.py benchmark --models qwen2.5:0.5b,qwen2.5:7b
```

重点看通过率、参数忠实度、修复次数和耗时，不要只看语言是否流畅。即使 0.5B 在四个样例上全部通过，也只能说明它适配了当前狭窄测试集；增加平台关系和复杂约束后必须重新评测。

## 7. 如何增加一个新想定类型

以雷达搜索跟踪为例，按以下顺序扩展：

1. 从 AFSIM 自带 demo 中找到可运行的最小雷达平台、传感器和事件输出证据。
2. 把稳定引用封装成组件 JSON，分配不可歧义的组件 ID。
3. 给组件添加来源、适用边界、必填参数和已验证 demo。
4. 扩展 JSON Schema 与 `validate_scenario()`，禁止模型发明引用。
5. 增加雷达 RAG 文档；文档只提供事实，不承担程序校验职责。
6. 建立至少包含基线、参数忠实度、边界条件和非法请求的评测样例。
7. 逐个执行 `mission.exe`，保存 trace 和事件输出证据。
8. 由懂业务的人确认探测、跟踪和事件结果符合建模意图。

新能力没有独立评测集和实跑证据，就不能写入“已支持”清单。

## 8. Git 与离线交付

代码、配置、提示词、知识文档和小型报告进入 Git；模型权重、仿真大文件、日志和敏感想定数据不进入 Git。

```powershell
cd D:\AFsim\Agent
git status --short
git add <本次文件>
git commit -m "描述本次可验证能力"
git push origin main
```

离线包使用第 12 步生成。它故意不包含模型和 AFSIM 安装，需要在目标机上单独准备并校验哈希、版本和许可证。

## 9. 你最终应具备的能力

完成并理解本教程后，你具备的是一组可迁移的复合能力：

- 把仿真需求拆成结构化数据契约和可执行组件；
- 部署本地模型并判断显存、内存、磁盘和速度之间的取舍；
- 设计本地 RAG，而不是把整个手册无差别塞进提示词；
- 用 Agent 编排不确定的模型与确定性的校验、生成和仿真工具；
- 用 MCP/Skill 把成熟 CLI 接入其他 AI 工作台；
- 建立多样本回归、语义门禁、日志审计和人工复核；
- 对外准确说明“已证明的能力”和“尚未验证的边界”。

下一阶段的工程重点不应继续堆 Agent 框架，而应扩充真实 AFSIM 组件、领域校验规则和代表性评测集。

## 10. 官方参考

- Ollama Structured Outputs: <https://docs.ollama.com/capabilities/structured-outputs>
- Ollama Generate API: <https://docs.ollama.com/api/generate>
- Ollama Qwen2.5 模型页: <https://ollama.com/library/qwen2.5>

完整问题清单见 [避坑手册](PITFALLS.md)，验收标准见 [工程验收表](ACCEPTANCE.md)，当前优化优先级见 [项目差距审计](PROJECT_GAP_ANALYSIS.md)，长期学习见 [专家能力路线](EXPERT_ROADMAP.md)，做实验时使用 [实验记录模板](EXPERIMENT_TEMPLATE.md)。
