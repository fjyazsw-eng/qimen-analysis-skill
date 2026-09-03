#!/usr/bin/env python3
"""Deterministic stock dashboard renderer reference for qimen-analysis-skill v1.2.6.
Reads IMAGE_PAYLOAD JSON and writes a six-module PNG. No divination or inference occurs here.
"""
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('payload'); ap.add_argument('output'); args=ap.parse_args()
    data=json.loads(Path(args.payload).read_text(encoding='utf-8'))
    if len(data.get('ten_days',[])) != 10: raise SystemExit('ten_days must contain exactly 10 rows')
    from PIL import Image, ImageDraw, ImageFont
    W,H=1536,1024; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    fonts=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc']; fp=next((x for x in fonts if Path(x).exists()),None)
    def F(n): return ImageFont.truetype(fp,n) if fp else ImageFont.load_default()
    navy=(8,34,74); red=(145,0,0); d.rectangle([0,0,W,55],fill=navy)
    d.text((20,10),f"{data.get('security_name','')}（{data.get('security_code','')}）奇门遁甲分析 & 操作建议",font=F(28),fill='white')
    boxes=[(8,62,490,450),(496,62,1080,450),(1086,62,1528,450),(8,460,1080,1000),(1086,460,1528,720),(1086,730,1528,1000)]
    titles=['一、最新行情','二、奇门十日节奏曲线（未来十个交易日）','三、关键价格区域（元）','四、未来十个交易日操作计划表','五、卦象定性判断','六、综合结论']
    for b,t in zip(boxes,titles): d.rectangle(b,outline='black',width=2); d.rectangle([b[0],b[1],b[2],b[1]+40],fill=red); d.text((b[0]+12,b[1]+7),t,font=F(18),fill='white')
    snap=data.get('market_snapshot',{}); y=120
    for k in ['last_price','change_amount','change_percent','open','high','low','volume','turnover_amount','turnover_rate']:
        if snap.get(k) not in (None,''): d.text((25,y),f"{k}: {snap[k]}",font=F(16),fill='black'); y+=30
    d.text((1110,520),f"等级：{data.get('qimen_rating','')}",font=F(25),fill='black'); d.text((1110,570),str(data.get('qimen_one_sentence',''))[:24],font=F(15),fill='black')
    y=515
    for row in data['ten_days']:
        d.text((25,y),f"{row.get('date','')} {row.get('weekday','')} | {row.get('direction','')} | {row.get('suggestion','')}"[:70],font=F(14),fill='black'); y+=44
    d.text((1110,790),f"重点日期：{'、'.join(data.get('key_dates',[]))}",font=F(15),fill='black'); d.text((1110,830),f"总体节奏：{data.get('overall_rhythm','')}"[:35],font=F(14),fill='black'); im.save(args.output)
if __name__=='__main__': main()
