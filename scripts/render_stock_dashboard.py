#!/usr/bin/env python3
"""Deterministic stock dashboard renderer for qimen-analysis-skill v1.2.8.

Reads a frozen IMAGE_PAYLOAD JSON and writes a six-module 16:9 PNG.
This layer MUST NOT perform Qimen analysis, infer missing prices, alter dates,
or reinterpret frozen directions.
"""
import argparse
import json
import textwrap
from pathlib import Path

DIRECTION_SCORE = {
    "强势上行": 2,
    "偏强整理": 1,
    "横盘整理": 0,
    "偏弱整理": -1,
    "明显下行": -2,
}

REQUIRED_TITLES = [
    "一、最新行情",
    "二、奇门十日节奏曲线（未来十个交易日）",
    "三、关键观察信号",
    "四、未来十个交易日操作计划表",
    "五、卦象定性判断",
    "六、综合结论",
]


def validate(data):
    rows = data.get("ten_days", [])
    if len(rows) != 10:
        raise ValueError("ten_days must contain exactly 10 rows")
    dates = [r.get("date") for r in rows]
    if any(not x for x in dates) or len(set(dates)) != 10:
        raise ValueError("ten_days dates must be 10 unique non-empty values")
    for row in rows:
        direction = row.get("direction")
        if direction not in DIRECTION_SCORE:
            raise ValueError(f"invalid direction: {direction}")
        expected = DIRECTION_SCORE[direction]
        if row.get("rhythm_score") not in (None, expected):
            raise ValueError(f"rhythm_score conflicts with direction on {row.get('date')}")
    if not data.get("security_name"):
        raise ValueError("security_name is required")
    if not data.get("chart_time"):
        raise ValueError("chart_time is required")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload")
    ap.add_argument("output")
    args = ap.parse_args()
    data = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    validate(data)

    from PIL import Image, ImageDraw, ImageFont

    W, H = 1600, 900  # exact 16:9
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    fp = next((x for x in fonts if Path(x).exists()), None)
    def F(n): return ImageFont.truetype(fp, n) if fp else ImageFont.load_default()

    navy, red, grid, light = (8,34,74), (145,0,0), (190,195,205), (247,248,250)
    d.rectangle([0,0,W,58], fill=navy)
    code = data.get("security_code", "")
    name = data["security_name"]
    d.text((24,13), f"{name}{'（'+code+'）' if code else ''} 奇门十日分析总览", font=F(29), fill="white")
    d.text((1120,18), f"起局：{data['chart_time']}", font=F(17), fill="white")

    boxes = [(10,68,500,390),(510,68,1090,390),(1100,68,1590,390),(10,400,1090,885),(1100,400,1590,635),(1100,645,1590,885)]
    titles = REQUIRED_TITLES.copy()
    price_zones = data.get("price_zones") or []
    signals = data.get("observation_signals") or []
    if price_zones:
        titles[2] = "三、关键价格区域（元）"
    for b,t in zip(boxes,titles):
        d.rectangle(b, outline=(40,40,40), width=2, fill="white")
        d.rectangle([b[0],b[1],b[2],b[1]+38], fill=red)
        d.text((b[0]+12,b[1]+7), t, font=F(18), fill="white")

    # 1 latest market: only payload values, never inferred.
    b=boxes[0]; y=b[1]+58
    if data.get("market_data_time"):
        d.text((b[0]+20,y), f"数据截止：{data['market_data_time']}", font=F(16), fill=(40,40,40)); y+=38
    snap=data.get("market_snapshot",{})
    labels={"last_price":"最新价","change_amount":"涨跌额","change_percent":"涨跌幅","previous_close":"前收","open":"开盘","high":"最高","low":"最低","volume":"成交量","turnover_amount":"成交额","turnover_rate":"换手率"}
    for k in labels:
        if snap.get(k) not in (None,"") and y < b[3]-30:
            d.text((b[0]+25,y), f"{labels[k]}：{snap[k]}", font=F(17), fill=(25,25,25)); y+=31

    # 2 rhythm chart: derived only from frozen direction mapping.
    b=boxes[1]; x0,y0,x1,y1=b[0]+55,b[1]+75,b[2]-25,b[3]-62
    for s in [-2,-1,0,1,2]:
        yy=y1-(s+2)/4*(y1-y0); d.line([x0,yy,x1,yy],fill=(225,225,225),width=1); d.text((x0-32,yy-8),str(s),font=F(12),fill=(60,60,60))
    pts=[]
    for i,row in enumerate(data["ten_days"]):
        score=DIRECTION_SCORE[row["direction"]]; xx=x0+i*(x1-x0)/9; yy=y1-(score+2)/4*(y1-y0); pts.append((xx,yy))
        d.ellipse([xx-4,yy-4,xx+4,yy+4],fill=navy); d.text((xx-17,y1+10),str(row["date"])[-5:],font=F(11),fill=(40,40,40))
    d.line(pts,fill=red,width=3)
    d.text((b[0]+150,b[1]+45),"相对强弱节奏，不是股价预测",font=F(15),fill=(90,90,90))

    # 3 price zones OR observation signals.
    b=boxes[2]; y=b[1]+58
    items=price_zones if price_zones else signals
    if not items: items=["无可靠现实价位：不补全、不猜测"]
    for item in items[:7]:
        text = item if isinstance(item,str) else "：".join(str(v) for v in item.values() if v not in (None,""))
        for line in textwrap.wrap(text,width=24): d.text((b[0]+20,y),line,font=F(15),fill=(30,30,30)); y+=25
        y+=8

    # 4 exactly ten rows.
    b=boxes[3]; cols=[b[0]+8,b[0]+118,b[0]+205,b[0]+385,b[2]-8]; top=b[1]+42; rh=40
    for j,h in enumerate(["日期","星期","预计节奏","操作/观察"]):
        d.rectangle([cols[j],top,cols[j+1],top+36],fill=navy); d.text((cols[j]+7,top+8),h,font=F(14),fill="white")
    y=top+36
    for i,row in enumerate(data["ten_days"]):
        d.rectangle([cols[0],y,b[2]-8,y+rh],fill=light if i%2==0 else "white",outline=grid)
        vals=[row.get("date",""),row.get("weekday",""),row["direction"],row.get("suggestion") or row.get("observation") or ""]
        widths=[10,5,10,40]
        for j,val in enumerate(vals):
            val=str(val); shown=val if len(val)<=widths[j] else val[:widths[j]-1]+"…"
            d.text((cols[j]+7,y+9),shown,font=F(14),fill=(25,25,25))
            if j: d.line([cols[j],y,cols[j],y+rh],fill=grid,width=1)
        y+=rh

    # 5 qualitative judgment.
    b=boxes[4]; y=b[1]+58
    d.text((b[0]+20,y),f"等级：{data.get('qimen_rating','')}",font=F(25),fill=red); y+=45
    for label,key in [("一句话","qimen_one_sentence"),("核心判断","core_judgment"),("风险原则","risk_principle")]:
        text=data.get(key,"")
        if text:
            d.text((b[0]+20,y),f"{label}：",font=F(15),fill=navy); y+=23
            for line in textwrap.wrap(str(text),width=26): d.text((b[0]+20,y),line,font=F(14),fill=(30,30,30)); y+=22
            y+=5

    # 6 conclusion.
    b=boxes[5]; y=b[1]+55
    conclusions=[]
    if data.get("key_dates"): conclusions.append("重点日期："+"、".join(data["key_dates"]))
    if data.get("overall_rhythm"): conclusions.append("总体节奏："+str(data["overall_rhythm"]))
    if data.get("failure_conditions"): conclusions.append("失效条件："+str(data["failure_conditions"]))
    if data.get("confidence"): conclusions.append("置信度："+str(data["confidence"]))
    for item in conclusions:
        for line in textwrap.wrap(item,width=27): d.text((b[0]+20,y),line,font=F(14),fill=(30,30,30)); y+=23
        y+=5

    # Mechanical output checks before publication.
    if im.size != (1600,900): raise RuntimeError("output is not 16:9")
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    im.save(args.output)

if __name__ == "__main__":
    main()
