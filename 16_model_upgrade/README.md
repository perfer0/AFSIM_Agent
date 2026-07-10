# Step 16 - Model Upgrade

这一课规划本地模型升级。

当前稳定基线：

```text
qwen2.5:0.5b
```

它适合验证链路，但复杂想定需要更强模型。推荐下一步评估：

```text
qwen2.5:7b
qwen2.5-coder:7b
qwen2.5:14b
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\16_model_upgrade
python .\model_upgrade.py status
python .\model_upgrade.py write-pull-script
```

生成的脚本：

```text
build/pull_candidate_models.ps1
```

## 为什么不自动下载

7B/14B 模型会占用数 GB 到十几 GB。下载前应确认：

```text
磁盘空间
网络时间
是否要保持 qwen2.5:0.5b 作为稳定回归基线
```

## 升级验证门禁

新模型拉取后必须通过：

```text
ollama list 能看到模型
Step 07 Agent draft_provider = ollama
mission.exe exit code = 0
Step 13 capability review 仍然 overall_passed = true
```
