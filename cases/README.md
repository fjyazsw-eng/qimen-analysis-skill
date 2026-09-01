# 案例规范

每个案例单独存放在 `cases/<case_id>/`：

```text
case.yaml          # 元数据、取用、结论摘要与错误标签
input.md           # 脱敏后的原始标准输入，保持原样
analysis.md        # 事前分析，不在事后改写
prediction-ledger.md # 目标事件、预测窗口、策略与失效条件的冻结台账
outcome.md         # 后续实际结果与证据日期
review.md          # 复盘与规则改进建议
```

`case.yaml` 最小字段：

```yaml
case_id: ""
question: ""
question_category: ""
question_subtype: ""
success_criterion: ""
target_event: ""
event_chain_stage: ""
chart_time: ""
system: "时家拆补转盘法"
input_file: "input.md"
yongshen:
  mode: "self|proxy|multi_party"
  decisions:
    - role: ""
      symbol: ""
      palace: ""
      priority: "primary|secondary"
      rule_id: ""
      source_level: "A|B|C|D|E"
      reason: ""
  overlaps: []
  alternatives: []
  unresolved: []
analysis_file: "analysis.md"
prediction_ledger_file: "prediction-ledger.md"
qualitative_rating: ""
timing_windows: []
prediction_confidence: ""
invalidation_conditions: []
outcome_file: "outcome.md"
review_file: "review.md"
error_types: []
privacy: "anonymized"
created_at: ""
outcome_recorded_at: ""
skill_version: "1.2.1"
```

`error_types` 只能从以下值选择：`问题定义错误`、`取用错误`、`旺衰错误`、`生克关系错误`、`特殊状态误判`、`趋势错误`、`应期错误`、`策略错误`、`过度推断`、`信息不足`。无偏差时为空数组。

案例进入公开仓库前必须脱敏。实际结果注明来源和记录时间；无法验证的反馈标为“主观反馈”，不得当作强回归证据。

首次登记与结案分别使用 [结果记录模板](outcome-template.md) 和 [复盘模板](review-template.md)。完整的事前冻结、结果登记和评审流程见[前瞻案例协议](../tests/forward-test-protocol.md)。

预测字段的权威格式见[预测台账](prediction-ledger.md)。旧局一旦冻结，新局只能追加“强化 / 削弱 / 修正 / 推迟 / 提前 / 反转”，不得覆盖原记录。
