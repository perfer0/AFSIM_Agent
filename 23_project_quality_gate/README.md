# 第 23 步：统一项目质量门禁

不用记住所有测试命令。当前不下载 7B 时运行核心门禁：

```powershell
cd D:\AFsim\Agent\23_project_quality_gate
python .\quality_gate.py core
```

它会执行：Python 编译、全项目 JSON 解析、第 19/21/22 步单元测试、真实 EOIR `.evt` 验收，以及九次可重复实验。

以后 7B 完整安装后运行生产门禁：

```powershell
python .\quality_gate.py production
```

生产模式会在核心门禁之后增加模型环境诊断和五样例 Agent 工程评测。它不会自动下载模型。
