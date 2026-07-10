# 第 19 步：工程级模型基线与回归评测

这一层解决的不是“模型能不能回答”，而是“模型生成的想定能不能稳定通过结构校验、语义检查和 AFSIM 实跑”。

模型分工：

- `qwen2.5:0.5b`：仅用于 Ollama、显卡和 API 冒烟测试。
- `qwen2.5:7b`：当前 8GB 显存机器的生产基线候选。
- 14B 及更大模型：当前显存下容易发生 CPU 卸载和速度下降，不作为默认方案。

验收命令：

```powershell
$env:OLLAMA_MODELS='D:\AFsim\Agent\ollama\models'
cd D:\AFsim\Agent\19_engineering_baseline
python .\engineering_benchmark.py doctor
python .\engineering_benchmark.py benchmark --models qwen2.5:7b
```

对比 0.5B 和 7B 时使用：

```powershell
python .\engineering_benchmark.py benchmark --models qwen2.5:0.5b,qwen2.5:7b
```

工程门禁要求全部满足：四个正向样例 JSON Schema 约束成功、项目校验成功、需求语义检查成功、`mission.exe` 返回 0、没有规则兜底；一个超范围雷达请求必须在调用模型前被明确拒绝。

结果在 `build/benchmark_report.md`，每个样例的 JSON、AFSIM 文件、日志和 trace 在 `build/runs/<model>/<case>/`。

## 下载控制

本次 7B 下载已按用户要求暂停。之后恢复或再次暂停：

```powershell
cd D:\AFsim\Agent\19_engineering_baseline
.\resume_7b_download.ps1
.\pause_7b_download.ps1
```

恢复脚本会先确认 D 盘可用空间，把 `OLLAMA_MODELS` 指向项目目录，再重启本地 Ollama 服务。Ollama 会复用仍有效的已下载分片；只有 `ollama list` 出现完整模型后，`doctor` 才会通过。
