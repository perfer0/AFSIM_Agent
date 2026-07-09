# Step 03 - Component Library

这一课开始建立“组件库”。第二步的 JSON 已经能生成平台实例，但平台类型、事件输出、目标集合仍然写在同一个场景文件里。第三步把这些内容拆出来：

```text
components/platform_types/  平台类型组件
components/event_outputs/   事件输出组件
components/target_sets/     目标集合组件
examples/                   具体场景，只引用组件 ID
```

## 为什么要做组件库

智能想定生成不能只靠模型自由发挥。我们希望模型以后做的是：

```text
选择已有组件 -> 填参数 -> 生成 JSON -> CLI 校验和生成 AFSIM
```

这样可以降低乱编平台类型、传感器名字、事件名字的概率。

## 目录

```text
components/platform_types/uav_eoir.json
components/platform_types/ground_site.json
components/event_outputs/eoir_sensor_events.json
components/target_sets/eoir_short_long_targets.json
examples/eoir_component_scenario.json
afsim_ai.py
build/main_generated.txt
build/scenario_generated.txt
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\03_component_library

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py validate .\examples\eoir_component_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py generate .\examples\eoir_component_scenario.json

& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\afsim_ai.py run .\build\main_generated.txt
```

## 重点理解

场景里现在不直接写 AFSIM include，而是写组件 ID：

```json
"platform_type_refs": [
  "uav_eoir",
  "ground_site"
]
```

程序会去这里找：

```text
components/platform_types/uav_eoir.json
components/platform_types/ground_site.json
```

然后取出里面的：

```json
"afsim_type": "UAV",
"include": "D:/AFsim/AFSim/afsim-2.9.0-win64/demos/sensor_demos/platforms/uav_eoir.txt"
```

最终生成：

```text
include D:/AFsim/AFSim/afsim-2.9.0-win64/demos/sensor_demos/platforms/uav_eoir.txt
```

同理，目标集合不再写在主场景里，而是引用：

```json
"target_set_refs": [
  "eoir_short_long_targets"
]
```

程序会展开成多个 AFSIM `platform ... GROUND_SITE`。

## 这和本地大模型有什么关系

以后本地模型不用记住所有 AFSIM 细节。它只需要知道：

```text
我要一个 EOIR UAV
我要一组地面目标
我要 EOIR sensor events
```

然后生成引用组件 ID 的 JSON。真正的 AFSIM 语法由 CLI 生成。
