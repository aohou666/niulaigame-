import json
import re
from datetime import datetime
from pathlib import Path

import xlsxwriter


ROOT = Path(r"C:\Users\admin\Documents\ChatGPT\安装")
STAGING = ROOT / "outputs" / "game-config-summary" / "staging"
OUTPUT_DIR = ROOT / "outputs" / "game-config-summary"
OUTPUT = OUTPUT_DIR / "原包与当前包体-游戏配置总表.xlsx"


with (STAGING / "metadata.json").open("r", encoding="utf-8") as f:
    meta = json.load(f)

summary = meta["extractionSummary"]
tables = meta["tables"]
current_config = meta["currentConfig"]
runtime_catalog = meta["runtimeCatalog"]
current_rules = meta["currentRules"]
save_summary = meta["currentSaveSummary"]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
workbook = xlsxwriter.Workbook(OUTPUT, {"constant_memory": True, "strings_to_urls": False})
workbook.set_properties({
    "title": "原包与当前包体游戏配置总表",
    "subject": "原包配置、当前离线覆盖与运行目录汇总",
    "author": "OpenAI",
    "comments": "原始数值表来自恢复出的 localdata 二进制。",
})

navy = "#1F4E78"
dark = "#17365D"
light_blue = "#D9EAF7"
light_gray = "#E2E8F0"
line = "#CBD5E1"
text = "#1F2937"

fmt_title = workbook.add_format({"font_name": "Arial", "font_size": 16, "bold": True, "font_color": dark})
fmt_note = workbook.add_format({"font_name": "Arial", "font_size": 10, "italic": True, "font_color": "#5B6573"})
fmt_header = workbook.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "font_color": "#FFFFFF", "bg_color": navy, "align": "center", "valign": "vcenter", "border": 0})
fmt_text = workbook.add_format({"font_name": "Arial", "font_size": 10, "font_color": text, "valign": "top"})
fmt_wrap = workbook.add_format({"font_name": "Arial", "font_size": 10, "font_color": text, "valign": "top", "text_wrap": True})
fmt_int = workbook.add_format({"font_name": "Arial", "font_size": 10, "font_color": text, "num_format": "#,##0", "valign": "top"})
fmt_date = workbook.add_format({"font_name": "Arial", "font_size": 10, "font_color": text, "num_format": "yyyy-mm-dd hh:mm", "valign": "top"})
fmt_label = workbook.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "font_color": dark, "bg_color": light_blue, "border": 1, "border_color": line})
fmt_value = workbook.add_format({"font_name": "Arial", "font_size": 11, "bold": True, "font_color": text, "border": 1, "border_color": line, "num_format": "#,##0"})
fmt_value_text = workbook.add_format({"font_name": "Arial", "font_size": 10, "font_color": text, "border": 1, "border_color": line})
fmt_section = workbook.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "font_color": dark, "bg_color": light_gray})


def setup_sheet(name, title, note, widths, tab_color=None):
    ws = workbook.add_worksheet(name)
    ws.hide_gridlines(2)
    ws.set_row(0, 8)
    ws.write(1, 0, title, fmt_title)
    ws.write(2, 0, note, fmt_note)
    ws.set_row(2, 18)
    for col, width in enumerate(widths):
        ws.set_column(col, col, width)
    if tab_color:
        ws.set_tab_color(tab_color)
    return ws


def write_header(ws, headers, row=3):
    ws.set_row(row, 25)
    for col, value in enumerate(headers):
        ws.write(row, col, value, fmt_header)
    ws.freeze_panes(row + 1, 0)


def safe_cell(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))[:32760]
    return value


def flatten(value, prefix=""):
    rows = []
    if isinstance(value, list):
        for i, item in enumerate(value):
            rows.extend(flatten(item, f"{prefix}[{i}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            rows.extend(flatten(item, f"{prefix}.{key}" if prefix else key))
    else:
        rows.append((prefix, "null" if value is None else value, type(value).__name__))
    return rows


overview = setup_sheet(
    "配置总览",
    "原包与当前包体游戏配置总表",
    "原始数值表来自恢复出的 localdata 二进制；当前包体包含离线覆盖、运行目录和本地玩法规则。",
    [18, 16, 18, 16, 18, 16, 18, 16],
    dark,
)
kpis = [
    ("原始配置表", summary["tables"], "原始配置记录", summary["records"], "当前英雄目录", len(runtime_catalog.get("heroes", [])), "当前技能目录", len(runtime_catalog.get("skills", []))),
    ("成功解析表", summary["parsedTables"], "解析异常表", len(summary["tableErrors"]), "当前皮肤目录", len(runtime_catalog.get("skins", [])), "当前美人技能", len(runtime_catalog.get("beautySkills", []))),
    ("数据版本", summary["localVersion"], "分支", summary["branch"], "当前存档英雄", save_summary.get("heroes", 0), "当前上阵人数", save_summary.get("formation", 0)),
]
for r, values in enumerate(kpis, 4):
    for c, value in enumerate(values):
        overview.write(r, c, value, fmt_label if c % 2 == 0 else (fmt_value if isinstance(value, (int, float)) else fmt_value_text))

overview.write(9, 0, "系统分类", fmt_header)
overview.write(9, 1, "配置记录数", fmt_header)
for r, (category, count) in enumerate(sorted(summary["categories"].items(), key=lambda x: -x[1]), 10):
    overview.write(r, 0, category, fmt_text)
    overview.write_number(r, 1, count, fmt_int)
overview.autofilter(9, 0, 9 + len(summary["categories"]), 1)

notes = [
    ("原包配置", "恢复缓存内的 preload/localdata 配置表，代表原游戏客户端数值底表。"),
    ("当前包体", "v0.18 离线覆盖配置、当前运行时目录、本地玩法入口及规则。"),
    ("完整记录", "每行保存一条配置记录的完整 JSON，复杂数组、奖励、条件和属性不会丢失。"),
    ("差异判断", "当前 heroes/skills/skins/equips 覆盖为空，核心原始数值未被后台覆盖；离线玩法规则为新增层。"),
    ("限制", "法律协议文本、玩家即时进度不作为玩法配置明细；存档仅用于统计当前可用范围。"),
]
overview.write(9, 3, "口径说明", fmt_section)
for r, (label, note) in enumerate(notes, 10):
    overview.write(r, 3, label, fmt_label)
    overview.merge_range(r, 4, r, 7, note, fmt_wrap)

catalog = setup_sheet("配置表目录", "原包配置表目录", "覆盖 preload 与完整 localdata。字段列表保留每张表的全部字段名。", [14, 30, 28, 12, 10, 72, 18, 16])
catalog_headers = ["系统", "配置表", "源文件", "记录数", "字段数", "字段列表", "当前离线引用次数", "解析状态"]
write_header(catalog, catalog_headers)
source_text = (ROOT / "local_game" / "index_bh_lite3zbtest_andr.html").read_text("utf-8") + "\n" + (ROOT / "local_game" / "offline-ui.js").read_text("utf-8")
for r, table in enumerate(tables, 4):
    row = [table["category"], table["tableName"], table["sourceName"], table["rowCount"], len(table["fields"]), ", ".join(table["fields"]), source_text.count(f'config.{table["tableName"]}'), table["status"]]
    for c, value in enumerate(row):
        catalog.write(r, c, value, fmt_int if c in (3, 4, 6) else (fmt_wrap if c == 5 else fmt_text))
catalog.autofilter(3, 0, 3 + len(tables), len(catalog_headers) - 1)

records = setup_sheet("全部配置记录", "全部原始配置记录", "每行对应原包配置表的一条记录；完整 JSON 保留嵌套数组、奖励、条件与属性结构。", [14, 28, 28, 10, 18, 28, 110])
record_headers = ["系统", "配置表", "源文件", "序号", "主键", "名称/说明", "完整配置 JSON"]
write_header(records, record_headers)
records.freeze_panes(4, 2)

hero = setup_sheet("英雄配置", "英雄及主角配置", "Hero、Summoner、皮肤、图鉴、羁绊、升阶、升级、升星及阵容相关配置。", [30, 10, 18, 28, 110])
skill = setup_sheet("技能配置", "技能、Buff与战斗配置", "技能、Buff、属性、战斗帮助、兵种与敌方单位相关配置。", [30, 10, 18, 28, 110])
item = setup_sheet("装备物品配置", "装备、物品与养成载体配置", "装备、物品、宝物、神兵、符石、锦囊、坐骑及虎符相关配置。", [30, 10, 18, 28, 110])
topic_headers = ["配置表", "序号", "主键", "名称/说明", "完整配置 JSON"]
for ws in (hero, skill, item):
    write_header(ws, topic_headers)

hero_re = re.compile(r"^(Hero|Summoner|Handbook|LineUp|Altar)", re.I)
skill_re = re.compile(r"Skill|Buff|Battle|Attribute|Property|Creep|Abstract|Halo", re.I)
item_re = re.compile(r"Item|Equip|Treasure|Magical|Runestone|Chaks|Kit|Mount|Artifact|Catilla|Jewel", re.I)
topic_rows = {"hero": 4, "skill": 4, "item": 4}
record_row = 4
with (STAGING / "records.ndjson").open("r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        values = [obj["category"], obj["tableName"], obj["sourceName"], obj["index"], obj["key"], obj["name"], obj["json"]]
        for c, value in enumerate(values):
            records.write(record_row, c, value, fmt_int if c == 3 else fmt_text)
        record_row += 1
        topic_values = [obj["tableName"], obj["index"], obj["key"], obj["name"], obj["json"]]
        for key, regex, ws in (("hero", hero_re, hero), ("skill", skill_re, skill), ("item", item_re, item)):
            if regex.search(obj["tableName"]):
                rr = topic_rows[key]
                for c, value in enumerate(topic_values):
                    ws.write(rr, c, value, fmt_int if c == 1 else fmt_text)
                topic_rows[key] += 1
records.autofilter(3, 0, record_row - 1, len(record_headers) - 1)
hero.autofilter(3, 0, topic_rows["hero"] - 1, len(topic_headers) - 1)
skill.autofilter(3, 0, topic_rows["skill"] - 1, len(topic_headers) - 1)
item.autofilter(3, 0, topic_rows["item"] - 1, len(topic_headers) - 1)

current = setup_sheet("当前离线规则", "当前离线包新增与覆盖规则", "包含 v0.18 后台配置、历练入口和战斗场景；空覆盖集合表示继续使用原包底表。", [18, 42, 32, 18, 72])
current_headers = ["类型", "配置路径/标识", "当前值/名称", "值类型/编号", "来源/说明"]
write_header(current, current_headers)
current_row = 4
for cfg_path, value, value_type in flatten(current_config):
    for c, cell in enumerate(["后台覆盖配置", cfg_path, safe_cell(value), value_type, str(ROOT / "pc_server_data" / "offline-replica-config.json")]):
        current.write(current_row, c, cell, fmt_wrap if c in (2, 4) else fmt_text)
    current_row += 1
for rule in current_rules:
    kind, ident, name, number, desc, source = rule
    row = [kind, f"{ident}.{number}", name, number, f"{desc}；{source}"]
    for c, cell in enumerate(row):
        current.write(current_row, c, cell, fmt_wrap if c == 4 else fmt_text)
    current_row += 1
current.autofilter(3, 0, current_row - 1, len(current_headers) - 1)

runtime = setup_sheet("当前可用目录", "当前包体可用对象目录", "由当前客户端运行后导出的英雄、技能、皮肤、装备、美人及美人技能目录。", [18, 10, 20, 26, 110])
runtime_headers = ["对象类型", "序号", "主键", "名称", "完整配置 JSON"]
write_header(runtime, runtime_headers)
runtime_row = 4
for obj_type, values in runtime_catalog.items():
    if not isinstance(values, list):
        continue
    for idx, obj in enumerate(values, 1):
        key = next((obj.get(k) for k in ("id", "code", "key", "subType", "level", "type") if obj.get(k) is not None), idx)
        name = next((obj.get(k) for k in ("name", "showName", "title", "desc") if obj.get(k) is not None), "")
        row = [obj_type, idx, key, str(name)[:200], json.dumps(obj, ensure_ascii=False, separators=(",", ":"))[:32760]]
        for c, cell in enumerate(row):
            runtime.write(runtime_row, c, cell, fmt_int if c == 1 else fmt_text)
        runtime_row += 1
runtime.autofilter(3, 0, runtime_row - 1, len(runtime_headers) - 1)

performance = setup_sheet("技能表现配置", "技能表现与特效映射", "来源于原包 g_skill 配置；每行代表一个顶级技能、Buff、神兽或特效映射节点。", [34, 18, 118])
performance_headers = ["配置键", "节点类型", "完整配置 JSON"]
write_header(performance, performance_headers)
g_skill = json.loads((ROOT / "local_game" / "resource" / "config" / "g_skill_96a92798.json").read_text("utf-8"))
for r, (key, value) in enumerate(g_skill.items(), 4):
    row = [key, "对象" if isinstance(value, dict) else "数组" if isinstance(value, list) else type(value).__name__, json.dumps(value, ensure_ascii=False, separators=(",", ":"))[:32760]]
    for c, cell in enumerate(row):
        performance.write(r, c, cell, fmt_text)
performance.autofilter(3, 0, 3 + len(g_skill), len(performance_headers) - 1)

sources = setup_sheet("来源与说明", "来源、口径与限制", "文件时间来自当前工作区；玩家即时存档值不作为游戏设计配置。", [62, 16, 22, 78])
source_headers = ["来源文件", "字节数", "修改时间", "用途/口径"]
write_header(sources, source_headers)
source_rows = []
for item_stat in meta["fileStats"]:
    p = Path(item_stat["path"])
    purpose = "原始安装包" if p == ROOT / "apk_analysis" / "package_test" / "original.apk" else "当前发布 APK" if p == ROOT / "离线复刻测试-v0.18-原包界面与世界状态修复版.apk" else "配置来源"
    source_rows.append((str(p.relative_to(ROOT)), item_stat["bytes"], item_stat["modified"], purpose))
source_rows.extend([
    ("recovered_runtime/main.formatted.js", (ROOT / "recovered_runtime" / "main.formatted.js").stat().st_size, datetime.fromtimestamp((ROOT / "recovered_runtime" / "main.formatted.js").stat().st_mtime).isoformat(), "配置字段定义与二进制解析顺序"),
    ("local_game/resource/config/g_skill_96a92798.json", (ROOT / "local_game" / "resource" / "config" / "g_skill_96a92798.json").stat().st_size, datetime.fromtimestamp((ROOT / "local_game" / "resource" / "config" / "g_skill_96a92798.json").stat().st_mtime).isoformat(), "技能与特效表现映射，已单独展开"),
    ("local_game/resource/config/g_help_7c756b4f.json", (ROOT / "local_game" / "resource" / "config" / "g_help_7c756b4f.json").stat().st_size, datetime.fromtimestamp((ROOT / "local_game" / "resource" / "config" / "g_help_7c756b4f.json").stat().st_mtime).isoformat(), "协议与帮助文本，非玩法数值表，未展开正文"),
])
for r, row in enumerate(source_rows, 4):
    for c, cell in enumerate(row):
        if c == 1:
            sources.write_number(r, c, int(cell), fmt_int)
        elif c == 2:
            try:
                sources.write_datetime(r, c, datetime.fromisoformat(str(cell).replace("Z", "+00:00")).replace(tzinfo=None), fmt_date)
            except ValueError:
                sources.write(r, c, cell, fmt_text)
        else:
            sources.write(r, c, cell, fmt_wrap if c == 3 else fmt_text)
sources.autofilter(3, 0, 3 + len(source_rows), len(source_headers) - 1)

workbook.close()
print(f"OUTPUT={OUTPUT}")
print(json.dumps({
    "sheets": 10,
    "tables": summary["tables"],
    "records": summary["records"],
    "runtime_records": runtime_row - 4,
    "hero_topic_rows": topic_rows["hero"] - 4,
    "skill_topic_rows": topic_rows["skill"] - 4,
    "item_topic_rows": topic_rows["item"] - 4,
}, ensure_ascii=False))
