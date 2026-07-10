# 第 22 步：可重复参数实验

本步骤不调用大模型。它用确定性代码改变一个因素，并显式设置 AFSIM `random_seed`，演示如何用仿真回答问题。

实验设计：

```text
自变量：UAV 高度 30000 / 45000 / 60000 ft
随机种子：13579 / 24680 / 97531
控制变量：起点、速度、航向、目标集、任务动作和结束时间
运行数：3 x 3 = 9
```

运行：

```powershell
cd D:\AFsim\Agent\22_reproducible_experiments
python .\experiment_runner.py run
Get-Content .\build\experiment_report.md -Encoding UTF8
```

每次运行保留结构化输入、生成的 AFSIM 文本、随机种子、事件摘要和 SHA-256。实验汇总报告记录 Git commit、Python 版本、`mission.exe` 哈希、实验规范哈希，并给出均值、样本标准差、最小值和最大值。

三个种子只适合学习工作流，不足以支撑高置信度业务结论。真正研究需要根据效应大小、方差和置信水平确定重复次数。
