# 面向工程应用的验收表

## 当前 EOIR 基线必须满足

- [ ] Ollama 服务可访问，生产模型位于 `D:\AFsim\Agent\ollama\models`。
- [ ] `qwen2.5:7b` 已安装，0.5B 只作为 smoke test。
- [ ] 生成 API 使用 JSON Schema 和 temperature 0。
- [ ] 生产评测不传 `--fallback-rules`。
- [ ] 四个 EOIR 正向回归样例全部通过结构校验。
- [ ] 四个样例全部通过参数和动作语义检查。
- [ ] 四个样例的 `mission.exe` 返回码全部为 0。
- [ ] 超出范围的雷达请求在调用模型前被明确拒绝。
- [ ] 每次运行产物相互隔离并保留 trace。
- [ ] 基准报告明确声明只覆盖 EOIR 能力。
- [ ] 人工确认想定意图、组件口径和事件输出。

## 上线前仍需补齐

- [ ] 把硬编码的本机路径改为部署配置，并增加配置版本。
- [ ] 给 JSON IR 建立正式版本号和迁移策略。
- [ ] 增加非法输入、超限参数、模型不可用和 AFSIM 失败测试。
- [ ] 分析 `.evt/.aer` 输出，而不是只检查进程返回码。
- [ ] 建立业务人员签字、变更审查和模型升级回归流程。
- [ ] 评估数据分级、访问控制、审计留存和离线网络边界。
- [ ] 为雷达、通信、武器、电子战分别建立独立验收集。

## 发布判定

当前版本达到“工程原型基线”的条件是：

```text
doctor.passed == true
benchmark.engineering_gate_passed == true
production_model == qwen2.5:7b
all cases: no_rules_fallback == true
all cases: validation_passed == true
all cases: semantic_checks == true
all cases: run_exit_code == 0
```

它不等于经过组织认证的生产系统。安全、军事业务口径和真实任务有效性仍需要相应领域负责人审核。
