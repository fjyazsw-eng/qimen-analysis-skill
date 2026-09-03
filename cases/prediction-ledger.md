# Prediction Ledger｜预测台账

每个重要案例在结果未知时新增一条记录并冻结。不得覆盖旧版本；新局、新事实或修正以追加记录保存。

```yaml
case_id: ""
forecast_id: ""
created_at: ""
skill_version: "1.2.4"
analysis_fingerprint: ""
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
evidence_ledger:
  support: []
  resistance: []
  modifiers: []
  uncertainties: []
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

同一 `analysis_fingerprint` 再次分析时，必须先读取冻结台账，核对取用、九级定性、主趋势、关键转折与已冻结应期/逐日方向。没有合法变化原因却出现不同结论时，标记为“分析漂移”，不得覆盖旧记录。
