# Step 13 - Capability Review

这一课做能力复盘。

前面 12 步已经搭出一个离线 AFSIM 智能想定生成原型。第十三步不新增生成能力，而是回答：

```text
我现在到底具备了哪些 AI + 仿真复合能力？
哪些证据证明我具备？
下一阶段还缺什么？
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\13_capability_review
python .\capability_review.py
```

## 产物

```text
build/capability_review.json
build/capability_review.md
```

## 成功标准

```text
overall_passed = true
passed_count = total_count
每项能力都有文件证据或 JSON 校验证据
```

## 重点理解

这一阶段你已经不是只会“调一个大模型”。

你已经做过：

```text
AFSIM 脚本生成
组件库抽象
本地模型接入
RAG
Agent 闭环
MCP 工具
Skill 固化
总控编排
项目入口
离线打包
```

第十三步把这些能力用证据串起来，方便你复盘和继续扩展。
