# Step 02 - Generate Platform Instances

这一课把第一步往前推进一层：不再只生成 AFSIM 主控脚本，还要从 JSON 生成 `platform` 实例。

## 这一步在学什么

第一步生成的是：

```text
include ...
event_pipe ...
event_output ...
end_time ...
```

第二步生成的是：

```text
platform uav UAV
   side blue
   route
      position ...
   end_route
   execute at_time ...
      BeginImaging(...)
   end_execute
end_platform

platform sr_target_01 GROUND_SITE
   side red
   position ...
end_platform
```

也就是说，我们开始进入真正的想定内容：平台、阵营、位置、航线、任务动作。

## 目录

```text
examples/eoir_platform_scenario.json  结构化想定输入
afsim_ai.py                           第二步 CLI
build/main_generated.txt              生成的 AFSIM 主控文件
build/scenario_generated.txt          生成的平台实例文件
```

## 怎么运行

在 PowerShell 里执行：

```powershell
cd D:\AFsim\Agent\02_generate_platform_instances

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\eoir_platform_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\eoir_platform_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\main_generated.txt
```

## 重点理解

JSON 里的 UAV：

```json
{
  "name": "uav",
  "type": "UAV",
  "side": "blue"
}
```

会生成：

```text
platform uav UAV
   side blue
```

JSON 里的 route：

```json
"route": [
  {
    "position": "34:30:00n 116:00w",
    "altitude": "60000 ft",
    "speed": "350 kts",
    "heading": "0 deg"
  }
]
```

会生成：

```text
route
   position 34:30:00n 116:00w altitude 60000 ft speed 350 kts heading 0 deg
end_route
```

JSON 里的 execute：

```json
{
  "time": "1 min",
  "relative": true,
  "script": "BeginImaging(\"eoir\", \"\", -90, 68000);"
}
```

会生成：

```text
execute at_time 1 min relative
   BeginImaging("eoir", "", -90, 68000);
end_execute
```

这就是智能想定生成的核心方法：让模型以后生成结构化 JSON，程序把 JSON 稳定翻译成 AFSIM 语法。

## 和 Agent 的关系

现在还没有 Agent。当前只是底层 CLI 能力。

后面的完整路线是：

```text
CLI 先稳定生成和验证
MCP 再把 CLI 包成工具
Skill 固化 AFSIM 工作流程
Agent 最后负责任务拆解和多步调用
```
