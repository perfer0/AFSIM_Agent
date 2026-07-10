# Step 15 - Real AFSIM Extension

这一课开始把“下一类想定”落到真实 AFSIM demo 证据上。

它扫描本机 AFSIM demos，寻找这些方向的可复用样例：

```text
radar
communications
weapon
electronic warfare
multi-platform coordination
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\15_real_afsim_extension
python .\afsim_demo_scanner.py
```

## 产物

```text
build/afsim_demo_scan.json
build/extension_backlog.md
```

## 成功标准

```text
radar_hits > 0
communications_hits > 0
weapon_hits > 0
electronic_warfare_hits > 0
quality_gate.passed = true
```

## 重点理解

复杂扩展不能凭空发明组件。

必须先从本机 AFSIM demo 中找到真实语法和样例，再把它们抽成：

```text
knowledge snippet
component json
validation rule
scenario template
```
