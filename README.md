# AFSIM Agent：离线智能想定生成工程

本仓库是一套从 JSON 生成入门，逐步走到本地模型、RAG、Agent、MCP、Skill、AFSIM 实跑和工程评测的学习工程。所有代码、知识和模型数据均位于 `D:\AFsim\Agent`；AFSIM 安装位于 `D:\AFsim\AFSim\afsim-2.9.0-win64`。

## 当前结论

- `qwen2.5:0.5b` 只用于环境冒烟测试，不是工程生产模型。
- `qwen2.5:7b` 是当前 8GB 显存设备的生产基线候选，必须通过第 19 步评测后才可使用。
- 模型不直接写 AFSIM 文本，而是生成受 JSON Schema 约束的中间表示，再经过组件白名单、规则校验、自动修复和 `mission.exe` 实跑。
- 当前工程能力边界是 EOIR 侦察；雷达、通信、武器和电子战尚需各自增加组件和评测证据。

## 主入口

先阅读 [最终教程](20_final_tutorial/README.md)，再运行工程验收：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
cd D:\AFsim\Agent\19_engineering_baseline
python .\engineering_benchmark.py doctor
python .\engineering_benchmark.py benchmark --models qwen2.5:7b
```

## 学习目录

```text
01-03  JSON、平台实例和组件库
04-07  本地模型、RAG 和 Agent 闭环
08-11  MCP、Skill、编排和项目入口
12-18  离线打包、能力复盘和训练版总结
19     工程模型配置、多样本回归和严格门禁
20     从零复现教程、避坑手册和扩展路线
```

前 18 步保留为学习历史。工程判断以第 19 步的最新基准报告为准，不能用旧的单样例“通过”替代。
