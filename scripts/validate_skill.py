#!/usr/bin/env python3
from pathlib import Path
import sys
import re
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def need(path,*phrases):
    p=ROOT/path
    if not p.is_file(): errors.append(f'missing {path}'); return
    if p.suffix in {'.md','.py','.yaml','.yml',''} or p.name=='VERSION':
        s=p.read_text(encoding='utf-8')
        for x in phrases:
            if x not in s: errors.append(f'{path} missing: {x}')
VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
if not re.fullmatch(r'\d+\.\d+\.\d+', VERSION): errors.append(f'invalid VERSION: {VERSION}')
for p in ['SKILL.md','core/analysis-sop.md','rules/analysis-stability.md','modules/commerce/stock-ten-day-forecast.md']:
    need(p)
need('modules/commerce/README.md','stock-image-protocol.md')
need('modules/commerce/stock-image-protocol.md','TEXT_FREEZE','IMAGE_PAYLOAD','一、最新行情','二、奇门十日节奏曲线（未来十个交易日）','三、关键价格区域（元）','四、未来十个交易日操作计划表','五、卦象定性判断','六、综合结论','禁止生成九宫格','程序化渲染','文件附件/下载链接','禁止用生成式图片模型')
need('scripts/render_stock_dashboard.py','ten_days','六、综合结论')
need('assets/stock-dashboard-template.svg','一、最新行情','六、综合结论')

# V1.4.0 core regression gates
need('README.md',f'当前版本：V{VERSION}','盘内寻机与趋避转化','解局权不拥有改判权')
need('SKILL.md','减凶、转吉、增吉、寻生','候选生机/转化宫','相关升权、不相关作背景')
need('core/analysis-sop.md','全局相关宫与寻机扫描','盘内寻机与决策/趋吉避凶层')
need('rules/strategy-engine.md','减凶','转吉','增吉','寻生','解局权不拥有改判权','候选生机/转化宫')
need('rules/prosperity.md','核心宫位的八门、九星必须分别读取落宫旺衰与月令旺衰')
need('rules/global-structure.md','值符、值使每局必查','相关则提升证据权重，不相关则保留为背景')
need('tests/strategy-transformation-scenarios.yaml','ST-01','ST-06')

if errors:
    print('Skill validation failed:')
    for e in errors: print('-',e)
    sys.exit(1)
print('Skill validation passed.')
print(f'Version: {VERSION}')
print('Stock delivery: TEXT_FREEZE -> IMAGE_PAYLOAD -> deterministic PNG attachment')
