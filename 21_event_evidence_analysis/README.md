# 第 21 步：AFSIM 事件证据与任务效果验收

`mission.exe` 返回 0 只说明仿真程序完成，不能说明侦察任务有效。本步骤解析 AFSIM 文本事件文件 `.evt`，把仿真输出转换为可审计指标。

```text
.evt
  -> 多行事件记录解析
  -> 探测/航迹/目标指标
  -> 验收 profile
  -> JSON + Markdown 证据报告
```

验证第 01 步确定性 EOIR 参考想定：

```powershell
cd D:\AFsim\Agent\21_event_evidence_analysis
python .\event_evidence.py verify `
  ..\01_json_to_afsim_main\build\output\eoir_demo_generated.evt `
  --profile .\profiles\eoir_reference_demo.json `
  --output .\build\reference_verification.json `
  --markdown .\build\reference_verification.md
```

重点观察：

- `detection_attempts`：发生了多少次传感器探测尝试。
- `successful_detections`：事件中 `Detected: 1` 的数量。
- `unique_targets_detected`：真正被发现的不同目标数。
- `tracks_initiated/tracks_dropped`：航迹生命周期是否闭合。
- `first_detection_seconds`：首次发现时间。
- `failure_reasons`：视场角等约束导致失败的次数。

`.aer` 是二进制事件管道，适合 AFSIM 工具链回放，不应当用文本正则解析。本步骤只处理明确为文本格式的 `.evt`。
