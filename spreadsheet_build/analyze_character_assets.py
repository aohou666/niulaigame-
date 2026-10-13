import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\admin\Documents\ChatGPT\安装")
RECORDS = ROOT / "outputs" / "game-config-summary" / "staging" / "records.ndjson"

tables = defaultdict(list)
wanted = {"HeroLO", "HeroDermaLO", "SkillBaseLO", "HandbookLO", "HeroHaloLO", "HeroResonateLO", "StoryLO", "StorySubLO"}
with RECORDS.open("r", encoding="utf-8") as fh:
    for line in fh:
        rec = json.loads(line)
        if rec["tableName"] in wanted:
            obj = json.loads(rec["json"])
            tables[rec["tableName"]].append(obj)

heroes = tables["HeroLO"]
print("HERO_ROWS", len(heroes))
print("UNIQUE_SUBTYPE", len({h.get("subType") for h in heroes}))
print("IS_SHOW", Counter(h.get("isShow") for h in heroes))
print("IS_DERMA", Counter(h.get("isDerma") for h in heroes))
print("UNIQUE_NAMES", len({h.get("name") for h in heroes}))
print("STORY_NONEMPTY", sum(any(h.get(f"storyDesc{i}") for i in (1,2,3)) for h in heroes))
print("PICTURE_NONEMPTY", sum(bool(h.get("pictureDraw")) for h in heroes))
print("HALF_NONEMPTY", sum(bool(h.get("halfPic")) for h in heroes))

by_sub = defaultdict(list)
for h in heroes:
    by_sub[h.get("subType")].append(h)

for sub in sorted(by_sub, key=lambda x: (x is None, x)):
    rows = by_sub[sub]
    visible = [h for h in rows if h.get("isShow")]
    story = [h for h in rows if any(h.get(f"storyDesc{i}") for i in (1,2,3))]
    if sub <= 110 or visible or story:
        candidates = sorted(rows, key=lambda h: (not bool(h.get("isShow")), -int(h.get("realStarLevel") or 0), int(h.get("code") or 0)))
        h = candidates[0]
        print(json.dumps({
            "subType": sub, "rows": len(rows), "visible": len(visible), "story": len(story),
            "candidate": {k: h.get(k) for k in ("code","name","race","profession","initStar","realStarLevel","tier","isShow","isStar","isDerma","color","model","avatar","avatar2","halfPic","pictureDraw","storyTitle1","storyDesc1")}
        }, ensure_ascii=False))

for name in ("HeroDermaLO", "SkillBaseLO", "HandbookLO", "HeroHaloLO", "HeroResonateLO", "StoryLO", "StorySubLO"):
    print(name, len(tables[name]))

for sub in (1, 19, 76, 94):
    print("DETAIL", sub)
    for h in by_sub[sub]:
        if h.get("isShow") or any(h.get(f"storyDesc{i}") for i in (1,2,3)):
            print(json.dumps({k: h.get(k) for k in ("code","name","initStar","realStarLevel","isShow","isStar","isDerma","color","normalSkill","actSkill","posSkill1","posSkill2","posSkill3","storyTitle1","storyDesc1","model")}, ensure_ascii=True))
