# AFSIM Agent Learning MVP

这个目录是第一课：把一个现有 AFSIM demo 抽象成 JSON，再由程序重新生成 AFSIM 主控脚本。

## 这一步在学什么

完整的智能想定生成系统以后会有 Agent、Skill、MCP、RAG、本地大模型。但第一步只做最短闭环：

```text
scenario.json -> validate -> generate AFSIM txt -> mission.exe run
```

这里故意不让 AI 直接生成 AFSIM 脚本。我们先让结构化 JSON 成为中间层，因为 JSON 更容易校验、修复和交给大模型生成。

## 选用的 demo

本例参考：

```text
D:/AFsim/AFSim/afsim-2.9.0-win64/demos/sensor_demos/eoir_demo.txt
```

这个 demo 很适合入门，因为主控文件只做几件事：

1. include 一个 UAV + EOIR 传感器定义。
2. include 一个地面目标类型定义。
3. include 一个场景实例定义。
4. 配置 event_pipe 和 event_output。
5. 设置仿真结束时间。

## 文件说明

```text
examples/eoir_scenario.json  结构化想定描述
afsim_ai.py                  学习版 CLI
build/                       生成出的 AFSIM txt 放这里
```

## 怎么运行

在 PowerShell 里进入本目录：

```powershell
cd D:\AFsim\Agent
python .\afsim_ai.py validate .\examples\eoir_scenario.json
python .\afsim_ai.py generate .\examples\eoir_scenario.json
python .\afsim_ai.py run .\build\eoir_demo_generated.txt
```

如果 Python 命令不可用，可以试：

```powershell
py .\afsim_ai.py validate .\examples\eoir_scenario.json
```

如果本机没有 `python` 和 `py` 命令，但你在 Codex 环境里，可以用当前机器上的这个解释器：

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\eoir_scenario.json
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\eoir_scenario.json
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\eoir_demo_generated.txt
```

我已经验证过这条链路，`mission.exe` 可以正常完成仿真，退出码为 0。输出里能看到：

```text
Starting simulation.
T=60 uav; sensor: eoir
Image processed by processor.
Simulation complete
mission.exe exit code: 0
```

## 你应该重点看懂的地方

`examples/eoir_scenario.json` 不是最终 AFSIM 语法，而是我们自己定义的中间描述。

比如：

```json
"end_time": {
  "value": 20,
  "unit": "min"
}
```

会生成：

```text
end_time 20 min
```

再比如：

```json
"enabled_events": [
  "SENSOR_DETECTION_ATTEMPT",
  "SENSOR_TRACK_INITIATED"
]
```

会生成：

```text
enable SENSOR_DETECTION_ATTEMPT
enable SENSOR_TRACK_INITIATED
```

这就是后面接本地大模型的关键：模型先生成 JSON，程序再负责生成严格的 AFSIM 文件。

## 下一步怎么扩展

下一课可以把 `scenarios/eoir_demo.txt` 里面的平台实例也抽象进 JSON：

```text
platform uav UAV
side blue
route ...
execute ...
```

也就是从“只生成主控脚本”升级到“生成平台实例和任务行为”。
