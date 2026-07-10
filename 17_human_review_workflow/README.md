# Step 17 - Human Review Workflow

这一课补上人机协同审查。

复杂仿真不应该让模型直接拍板。AI 可以生成候选方案，但人需要审查：

```text
任务意图
组件选择
时间线和空间参数
模型输出风险
仿真证据
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\17_human_review_workflow
python .\review_workflow.py
```

## 产物

```text
review_checklist.json
build/human_review_report.json
build/human_review_report.md
```
