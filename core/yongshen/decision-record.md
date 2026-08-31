# 取用决策记录

每次分析在读取宫位之前生成记录：

```yaml
question_mode: self | proxy | multi_party
roles:
  - role: asker
    label: ""
    symbol: ""
    location: ""
    priority: primary | secondary | candidate
    rule_id: ""
    source_level: A | B | C | D
    reason: ""
    overlaps_with: []
alternatives: []
unresolved: []
impact_if_wrong: ""
```

## 最小质量门

- 角色表中“求测者”和“问事主体”均已定义。
- 每个用神都有规则编号与理由，不能只写“按惯例”。
- 天盘/地盘、主干/寄干、甲遁定位均写清楚。
- 专题候选没有静默替换通用锚点。
- 重叠、替代方案和未解决问题有记录。
- 取用选择被标记为第三层 AI 分析，不写入原始局式或结构标注。

