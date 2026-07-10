# Step 11 - Project Integration

这一课把前面的学习步骤集成为一个项目级入口。

你以后不需要记住每一层怎么跑，先从这里看：

```text
11_project_integration/afsim_project.py
```

## 这一步在学什么

第十一步解决的是项目工程化入口问题：

```text
project manifest
  -> status
  -> run orchestration
  -> collect audit
  -> project-level report
```

它不替代前面的层，而是统一调用它们：

```text
07 Agent loop
08 MCP tools
09 Skill
10 Orchestration
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\11_project_integration
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
python .\afsim_project.py status
python .\afsim_project.py run .\requests\integrated_eoir_request.txt
python .\afsim_project.py report
```

## 成功标准

```text
status 返回 0
run 返回 0
project_run_report.json 里的 quality_gates.passed = true
orchestration_audit.json 里的 passed = true
draft_provider = ollama
run_exit_code = 0
```

## 产物

```text
project_manifest.json
build/project_status.json
build/orchestration_run.json
build/project_run_report.json
build/project_run_report.md
```

## 重点理解

到这一步，项目已经开始像一个小型工程系统：

```text
底层：AFSIM + mission.exe
中间：JSON schema + validation + generation
智能层：RAG + Ollama + Agent repair loop
工具层：MCP
方法层：Skill
总控层：Orchestration
项目入口：Project Integration
```
