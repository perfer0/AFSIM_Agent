# Step 14 - Next Scenario Types

这一课把系统从单一 EOIR demo 扩展到多想定类型规划。

它不直接硬写复杂 AFSIM 脚本，而是先建立：

```text
想定类型目录
组件需求
知识库需求
校验规则需求
风险和优先级
下一步实现建议
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\14_next_scenario_types
python .\plan_scenario_types.py
```

## 产物

```text
scenario_type_catalog.json
build/scenario_type_plan.json
build/scenario_type_plan.md
```

## 成功标准

```text
has_baseline = true
has_radar_candidate = true
has_comm_candidate = true
recommended_next = radar_search_track
```

## 重点理解

复杂想定不要直接让大模型自由发挥。

正确顺序是：

```text
先列类型
再列组件
再找 AFSIM demo 证据
再扩知识库
再扩 JSON schema
最后才让 Agent 生成
```
