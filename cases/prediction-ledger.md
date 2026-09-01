# Prediction Ledger｜预测台账

每个重要案例在结果未知时新增一条记录并冻结。不得覆盖旧版本；新局、新事实或修正以追加记录保存。

```yaml
case_id: ""
forecast_id: ""
created_at: ""
skill_version: "1.2.1"
question: ""
target_event: ""
event_chain_stage: ""
chart_time: ""
input_hash: ""
analysis_hash: ""
yongshen:
  primary: []
  secondary: []
qualitative_rating: "大吉|吉|小吉|平偏吉|平|平偏凶|小凶|凶|大凶"
current_state: ""
forecast_trend: ""
event_tree: []
timing_windows:
  - window: ""
    possible_event: ""
    evidence: []
    confidence: "高|中高|中|中低|低"
    verification_signal: ""
strategy: []
invalidation_conditions: []
uncertainties: []
rule_ids: []
status: "frozen|superseded-by-new-chart|resolved|unresolved"
outcome: ""
hit_status: "正确|部分正确|错误|不可验证|未决"
timing_error: ""
error_causes: []
post_hoc_findings: []
rule_change_candidates: []
```

## 回测口径

按目标事件逐项统计命中与时间误差，不把更早阶段算成最终事件命中。可以分别统计用神宫触发、冲墓、出空、连续触宫、马星等规则，但必须公开样本量、适用问题、排除标准、未决案例和失败案例。

传统来源强不等于现实命中率高。规则调整必须遵守[规则可信度](../rules/rule-confidence.md)和[前瞻案例协议](../tests/forward-test-protocol.md)。
