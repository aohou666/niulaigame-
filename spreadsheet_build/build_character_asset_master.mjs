import fs from "node:fs/promises";
import path from "node:path";
import readline from "node:readline";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = String.raw`C:\Users\admin\Documents\ChatGPT\安装`;
const recordsPath = path.join(root, "outputs", "game-config-summary", "staging", "records.ndjson");
const assetRoot = path.join(root, "local_game", "resource", "assets");
const outputDir = path.join(root, "outputs", "character-asset-master");
const previewDir = path.join(outputDir, "previews");
const outputPath = path.join(outputDir, "角色资产总表.xlsx");

const wantedTables = new Set(["HeroLO", "HeroDermaLO", "SkillBaseLO"]);
const tables = new Map([...wantedTables].map((name) => [name, []]));
const input = await fs.open(recordsPath, "r");
try {
  const rl = readline.createInterface({ input: input.createReadStream(), crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    const rec = JSON.parse(line);
    if (!wantedTables.has(rec.tableName)) continue;
    tables.get(rec.tableName).push(JSON.parse(rec.json));
  }
} finally {
  await input.close();
}

async function listFiles(dir, out = []) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) await listFiles(full, out);
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

const assetFiles = await listFiles(assetRoot);
const assetIndex = assetFiles.map((fullPath) => {
  const rel = path.relative(root, fullPath).replaceAll("\\", "/");
  const ext = path.extname(fullPath).toLowerCase();
  const stem = path.basename(fullPath, ext);
  const logicalStem = stem.replace(/_[0-9a-f]{7,10}$/i, "");
  return { fullPath, rel, ext, stem, logicalStem };
});

function matchesForKey(key) {
  if (!key) return [];
  const k = String(key);
  return assetIndex.filter((f) => f.logicalStem === k || f.logicalStem.startsWith(`${k}_`));
}

function relPaths(matches, limit = 8) {
  const paths = matches.map((m) => m.rel);
  return paths.length <= limit ? paths.join("\n") : `${paths.slice(0, limit).join("\n")}\n…另有 ${paths.length - limit} 个文件`;
}

function parseArray(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  try { return JSON.parse(value); } catch { return []; }
}

const raceNames = { 0: "通用", 1: "魏国", 2: "蜀国", 3: "吴国", 4: "群雄", 5: "神族", 6: "魔族" };
const professionNames = { 0: "通用", 1: "肉盾", 2: "战士", 3: "谋士", 4: "辅助", 5: "先锋" };
const sexNames = { 0: "女", 1: "男", 2: "其他/未标注" };
const qualityNames = { 0: "未标注", 1: "白色", 2: "绿色", 3: "蓝色", 4: "卓越", 5: "超凡", 6: "绝世", 7: "绝世（神/魔）", 8: "特殊" };
const slotNames = { normalSkill: "普通技能", actSkill: "怒气技能", posSkill1: "被动技能1", posSkill2: "被动技能2", posSkill3: "被动技能3" };
const slotOrder = Object.keys(slotNames);

const heroGroups = new Map();
for (const hero of tables.get("HeroLO")) {
  const subType = Number(hero.subType || 0);
  if (!heroGroups.has(subType)) heroGroups.set(subType, []);
  heroGroups.get(subType).push(hero);
}

const officialSubTypes = [...heroGroups.entries()]
  .filter(([subType, rows]) => subType > 0 && subType < 900 && rows.some((h) => h.isShow || h.storyDesc1 || h.storyDesc2 || h.storyDesc3))
  .map(([subType]) => subType)
  .sort((a, b) => a - b);

function pickBaseHero(rows) {
  return [...rows].sort((a, b) => {
    const aStory = Number(Boolean(a.storyDesc1 || a.storyDesc2 || a.storyDesc3));
    const bStory = Number(Boolean(b.storyDesc1 || b.storyDesc2 || b.storyDesc3));
    const aZero = Number(Number(a.realStarLevel || 0) === 0);
    const bZero = Number(Number(b.realStarLevel || 0) === 0);
    return (bStory - aStory) || (bZero - aZero) || Number(a.realStarLevel || 0) - Number(b.realStarLevel || 0) || Number(a.code || 0) - Number(b.code || 0);
  })[0];
}

const skillById = new Map(tables.get("SkillBaseLO").map((skill) => [Number(skill.id), skill]));
const skinsByHero = new Map();
for (const skin of tables.get("HeroDermaLO")) {
  const subType = Number(skin.subType || 0);
  if (!skinsByHero.has(subType)) skinsByHero.set(subType, []);
  skinsByHero.get(subType).push(skin);
}

const heroRecords = officialSubTypes.map((subType) => {
  const progression = heroGroups.get(subType);
  const base = pickBaseHero(progression);
  const artKeys = [base.avatar, base.avatar2, base.halfPic, base.pictureDraw, base.model];
  const foundCore = artKeys.filter((key) => matchesForKey(key).length > 0).length;
  const skillSummary = {};
  for (const slot of slotOrder) {
    const id = Number(base[slot] || 0);
    const skill = skillById.get(id);
    skillSummary[slot] = id ? `${skill?.name || "未解析技能"}（${id}）` : "";
  }
  const stories = [1, 2, 3].filter((n) => base[`storyDesc${n}`]);
  return { subType, progression, base, foundCore, skillSummary, storyCount: stories.length, skins: skinsByHero.get(subType) || [] };
});

const mainRows = heroRecords.map(({ subType, base, foundCore, skillSummary, storyCount, skins }) => [
  subType,
  base.name,
  raceNames[base.race] || `未知（${base.race}）`,
  professionNames[base.profession] || `未知（${base.profession}）`,
  sexNames[base.sexType] || `未知（${base.sexType}）`,
  qualityNames[base.color] || `未知（${base.color}）`,
  Number(base.isStar || 0),
  Number(base.code || 0),
  Number(base.maxLevel || 0),
  base.definition || "原包未填写",
  base.activeSkillDesc || "原包未填写",
  skillSummary.normalSkill,
  skillSummary.actSkill,
  skillSummary.posSkill1,
  skillSummary.posSkill2,
  skillSummary.posSkill3,
  storyCount,
  skins.length,
  `${foundCore}/5`,
  base.model || "",
  base.avatar || "",
  base.avatar2 || "",
  base.halfPic || "",
  base.pictureDraw || "",
  base.baseAttr || "",
]);

const skillRows = [];
for (const record of heroRecords) {
  for (const slot of slotOrder) {
    const refs = new Map();
    for (const hero of record.progression) {
      const id = Number(hero[slot] || 0);
      if (!id) continue;
      if (!refs.has(id)) refs.set(id, []);
      refs.get(id).push(Number(hero.realStarLevel || 0));
    }
    for (const [id, levels] of refs) {
      const skill = skillById.get(id) || {};
      const iconMatches = matchesForKey(skill.iconName);
      const effectIds = parseArray(skill.skillEffect).join(", ");
      skillRows.push([
        record.subType, record.base.name, slotNames[slot], id, skill.name || "未解析技能", Number(skill.level || 0),
        Math.min(...levels), Math.max(...levels), skill.desc || skill.tapDesc || "原包未填写", skill.skillType ?? "",
        Number(skill.angerCost || 0), Number(skill.angerAdd || 0), skill.prob ?? "", effectIds,
        skill.tiggerCondition || "", skill.iconName || "", iconMatches.length ? "已匹配" : "缺失", relPaths(iconMatches),
        skill.modelId || "", skill.dermaModelId || "", skill.sound || "",
      ]);
    }
  }
}
skillRows.sort((a, b) => a[0] - b[0] || slotOrder.indexOf(Object.keys(slotNames).find((k) => slotNames[k] === a[2])) - slotOrder.indexOf(Object.keys(slotNames).find((k) => slotNames[k] === b[2])) || a[6] - b[6]);

const storyRows = [];
for (const record of heroRecords) {
  for (const n of [1, 2, 3]) {
    const title = record.base[`storyTitle${n}`] || "";
    const desc = record.base[`storyDesc${n}`] || "";
    storyRows.push([record.subType, record.base.name, raceNames[record.base.race] || "", n, title || "原包未填写", desc || "原包未发现", desc ? "有" : "缺失", Number(record.base.code || 0)]);
  }
}

const artRows = [];
const artFields = [
  ["主头像", "avatar"], ["次头像", "avatar2"], ["半身像", "halfPic"], ["立绘", "pictureDraw"],
  ["战斗模型", "model"], ["语音", "voice"], ["攻击语音", "voiceGJ"],
];
for (const record of heroRecords) {
  for (const [assetType, field] of artFields) {
    const key = record.base[field] || "";
    const matches = matchesForKey(key);
    const bytes = matches.length ? (await Promise.all(matches.map((m) => fs.stat(m.fullPath)))).reduce((sum, stat) => sum + stat.size, 0) : 0;
    artRows.push([
      record.subType, record.base.name, raceNames[record.base.race] || "", assetType, field, key,
      key ? (matches.length ? "已匹配" : "缺失") : "原包未填写", matches.length, bytes, relPaths(matches),
    ]);
  }
}

const skinRows = [];
for (const skin of tables.get("HeroDermaLO")) {
  const hero = heroRecords.find((r) => r.subType === Number(skin.subType || 0));
  const coreKeys = [skin.avatar, skin.avatar2, skin.halfPic, skin.dermaPic, skin.model];
  const found = coreKeys.filter((key) => matchesForKey(key).length > 0).length;
  skinRows.push([
    Number(skin.subType || 0), hero?.base.name || "未匹配角色", Number(skin.code || 0), skin.name || "", skin.desc || "",
    qualityNames[skin.color] || `未知（${skin.color}）`, skin.unlockText || "", skin.source || "", skin.condition || "",
    skin.avatar || "", skin.avatar2 || "", skin.halfPic || "", skin.dermaPic || "", skin.model || "", skin.anim || "",
    skin.skills || "", `${found}/5`, coreKeys.flatMap((key) => matchesForKey(key)).map((m) => m.rel).slice(0, 10).join("\n"),
  ]);
}
skinRows.sort((a, b) => a[0] - b[0] || a[2] - b[2]);

const workbook = Workbook.create();
const main = workbook.worksheets.add("角色资产总表");
const skillSheet = workbook.worksheets.add("技能明细");
const storySheet = workbook.worksheets.add("背景故事");
const artSheet = workbook.worksheets.add("美术资源");
const skinSheet = workbook.worksheets.add("皮肤明细");
const sourceSheet = workbook.worksheets.add("来源与口径");

const colors = {
  navy: "#17365D", blue: "#1F4E78", pale: "#D9EAF7", line: "#CBD5E1", text: "#1F2937",
  muted: "#5B6573", green: "#E8F3EA", greenText: "#216E39", red: "#FDECEC", redText: "#B91C1C",
};
const font = "Arial";

function colName(index) {
  let n = index + 1;
  let result = "";
  while (n > 0) {
    n--;
    result = String.fromCharCode(65 + (n % 26)) + result;
    n = Math.floor(n / 26);
  }
  return result;
}

function styleTitle(sheet, title, note, lastCol) {
  sheet.showGridLines = false;
  sheet.getRange("A1").format.rowHeight = 8;
  sheet.getRange("A2").values = [[title]];
  sheet.getRange("A2").format.font = { name: font, size: 16, bold: true, color: colors.navy };
  sheet.getRange(`A3:${lastCol}3`).format.borders = { bottom: { style: "thin", color: colors.navy } };
  sheet.getRange("A3").values = [[note]];
  sheet.getRange("A3").format.font = { name: font, size: 10, italic: true, color: colors.muted };
}

function styleHeader(range) {
  range.format.fill = colors.blue;
  range.format.font = { name: font, size: 10, bold: true, color: "#FFFFFF" };
  range.format.horizontalAlignment = "center";
  range.format.verticalAlignment = "center";
  range.format.rowHeight = 28;
  range.format.wrapText = true;
  range.format.borders = { insideVertical: { style: "thin", color: "#FFFFFF" } };
}

function writeDataSheet(sheet, title, note, headers, rows, widths, tableName, options = {}) {
  const lastCol = colName(headers.length - 1);
  styleTitle(sheet, title, note, lastCol);
  const headerRow = options.headerRow || 4;
  const dataStart = headerRow + 1;
  const endRow = headerRow + rows.length;
  sheet.getRange(`A${headerRow}:${lastCol}${endRow}`).values = [headers, ...rows];
  styleHeader(sheet.getRange(`A${headerRow}:${lastCol}${headerRow}`));
  sheet.getRange(`A${dataStart}:${lastCol}${endRow}`).format.font = { name: font, size: 10, color: colors.text };
  sheet.getRange(`A${dataStart}:${lastCol}${endRow}`).format.verticalAlignment = "top";
  for (let i = 0; i < widths.length; i++) sheet.getRange(`${colName(i)}:${colName(i)}`).format.columnWidth = widths[i];
  if (rows.length) sheet.tables.add(`A${headerRow}:${lastCol}${endRow}`, true, tableName);
  sheet.freezePanes.freezeRows(headerRow);
  if (options.freezeColumns) sheet.freezePanes.freezeColumns(options.freezeColumns);
  return { headerRow, dataStart, endRow, lastCol };
}

styleTitle(main, "原包角色资产总表", "按角色聚合原包角色配置、技能、背景故事、美术资源与皮肤。角色口径为非测试角色且存在展示或故事配置。", "Y");
main.tabColor = colors.navy;
main.getRange("A5:J6").values = [
  ["角色数", heroRecords.length, "有故事角色", heroRecords.filter((r) => r.storyCount > 0).length, "皮肤数", skinRows.length, "技能关联变体", skillRows.length, "核心美术完整角色", heroRecords.filter((r) => r.foundCore === 5).length],
  ["原包角色配置行", tables.get("HeroLO").length, "原包技能配置行", tables.get("SkillBaseLO").length, "原包美术文件", assetFiles.length, "美术关联记录", artRows.length, "数据版本", 49781],
];
for (const col of ["A", "C", "E", "G", "I"]) {
  main.getRange(`${col}5:${col}6`).format.fill = colors.pale;
  main.getRange(`${col}5:${col}6`).format.font = { name: font, size: 10, bold: true, color: colors.navy };
}
main.getRange("A5:J6").format.borders = { preset: "all", style: "thin", color: colors.line };
main.getRange("B5:J6").format.numberFormat = "#,##0";
main.getRange("A5:J6").format.verticalAlignment = "center";

const mainHeaders = ["角色ID", "名称", "阵营", "职业", "性别", "品质", "初始星阶码", "基准配置码", "最大等级", "角色定位", "主动技能说明", "普通技能", "怒气技能", "被动技能1", "被动技能2", "被动技能3", "故事段数", "皮肤数", "核心美术覆盖", "模型键", "主头像键", "次头像键", "半身像键", "立绘键", "基础属性JSON"];
const mainInfo = writeDataSheet(main, "原包角色资产总表", "按角色聚合原包角色配置、技能、背景故事、美术资源与皮肤。角色口径为非测试角色且存在展示或故事配置。", mainHeaders, mainRows, [9,14,10,10,8,14,10,15,10,26,32,24,24,24,24,24,10,9,12,22,24,24,24,18,42], "CharacterMaster", { headerRow: 9, freezeColumns: 2 });
main.getRange(`A${mainInfo.dataStart}:A${mainInfo.endRow}`).format.numberFormat = "0";
main.getRange(`G${mainInfo.dataStart}:I${mainInfo.endRow}`).format.numberFormat = "#,##0";
main.getRange(`Q${mainInfo.dataStart}:R${mainInfo.endRow}`).format.numberFormat = "#,##0";
main.getRange(`J${mainInfo.dataStart}:Y${mainInfo.endRow}`).format.wrapText = true;
main.getRange(`S${mainInfo.dataStart}:S${mainInfo.endRow}`).conditionalFormats.add("containsText", { text: "5/5", format: { fill: colors.green, font: { color: colors.greenText, bold: true } } });

const skillHeaders = ["角色ID", "角色名称", "技能槽位", "技能ID", "技能名称", "技能等级", "首次引用星级", "最后引用星级", "技能描述", "技能类型码", "怒气消耗", "怒气增加", "触发概率", "效果ID", "触发条件", "图标键", "图标状态", "图标资源路径", "表现模型键", "皮肤表现模型键", "声音键"];
const skillInfo = writeDataSheet(skillSheet, "角色技能明细", "按角色进阶过程去重保留每个技能槽位引用过的技能版本，并关联技能文案、图标和表现资源键。", skillHeaders, skillRows, [9,14,12,15,18,10,12,12,54,11,10,10,10,18,22,24,10,55,24,24,20], "CharacterSkills", { freezeColumns: 2 });
skillSheet.getRange(`D${skillInfo.dataStart}:D${skillInfo.endRow}`).format.numberFormat = "0";
skillSheet.getRange(`F${skillInfo.dataStart}:H${skillInfo.endRow}`).format.numberFormat = "#,##0";
skillSheet.getRange(`K${skillInfo.dataStart}:M${skillInfo.endRow}`).format.numberFormat = "#,##0";
skillSheet.getRange(`I${skillInfo.dataStart}:U${skillInfo.endRow}`).format.wrapText = true;
skillSheet.getRange(`Q${skillInfo.dataStart}:Q${skillInfo.endRow}`).conditionalFormats.add("containsText", { text: "缺失", format: { fill: colors.red, font: { color: colors.redText, bold: true } } });

const storyHeaders = ["角色ID", "角色名称", "阵营", "故事段", "标题", "背景故事", "状态", "来源配置码"];
const storyInfo = writeDataSheet(storySheet, "角色背景故事", "HeroLO 原包字段 storyTitle1–3 / storyDesc1–3。空白字段明确标记为原包未发现。", storyHeaders, storyRows, [9,14,10,9,24,88,10,15], "CharacterStories", { freezeColumns: 2 });
storySheet.getRange(`D${storyInfo.dataStart}:D${storyInfo.endRow}`).format.numberFormat = "0";
storySheet.getRange(`H${storyInfo.dataStart}:H${storyInfo.endRow}`).format.numberFormat = "0";
storySheet.getRange(`E${storyInfo.dataStart}:F${storyInfo.endRow}`).format.wrapText = true;
storySheet.getRange(`A${storyInfo.dataStart}:H${storyInfo.endRow}`).format.rowHeight = 72;
storySheet.getRange(`G${storyInfo.dataStart}:G${storyInfo.endRow}`).conditionalFormats.add("containsText", { text: "缺失", format: { fill: colors.red, font: { color: colors.redText, bold: true } } });

const artHeaders = ["角色ID", "角色名称", "阵营", "资产类型", "配置字段", "资源键", "匹配状态", "文件数", "总字节数", "原包资源路径"];
const artInfo = writeDataSheet(artSheet, "角色美术资源", "根据 HeroLO 资源键匹配原包恢复目录中的头像、半身像、立绘、战斗模型与语音文件。", artHeaders, artRows, [9,14,10,12,14,28,12,9,14,82], "CharacterArtAssets", { freezeColumns: 2 });
artSheet.getRange(`H${artInfo.dataStart}:I${artInfo.endRow}`).format.numberFormat = "#,##0";
artSheet.getRange(`J${artInfo.dataStart}:J${artInfo.endRow}`).format.wrapText = true;
artSheet.getRange(`G${artInfo.dataStart}:G${artInfo.endRow}`).conditionalFormats.add("containsText", { text: "缺失", format: { fill: colors.red, font: { color: colors.redText, bold: true } } });
artSheet.getRange(`G${artInfo.dataStart}:G${artInfo.endRow}`).conditionalFormats.add("containsText", { text: "已匹配", format: { fill: colors.green, font: { color: colors.greenText } } });

const skinHeaders = ["角色ID", "角色名称", "皮肤配置码", "皮肤名称", "皮肤说明", "品质", "解锁说明", "来源说明", "解锁条件", "主头像键", "次头像键", "半身像键", "皮肤卡图键", "模型键", "展示动画键", "技能替换", "核心美术覆盖", "资源路径"];
const skinInfo = writeDataSheet(skinSheet, "角色皮肤明细", "HeroDermaLO 全量皮肤配置，并关联所属角色、解锁文案、技能替换和核心美术路径。", skinHeaders, skinRows, [9,14,15,18,46,14,18,18,22,24,24,24,24,24,24,20,12,75], "CharacterSkins", { freezeColumns: 2 });
skinSheet.getRange(`C${skinInfo.dataStart}:C${skinInfo.endRow}`).format.numberFormat = "0";
skinSheet.getRange(`E${skinInfo.dataStart}:R${skinInfo.endRow}`).format.wrapText = true;

const sourceRows = [
  ["角色主数据", "preload_localdata_49784.bin / HeroLO", tables.get("HeroLO").length, "按 subType 聚合。基准行优先选择包含故事且 realStarLevel=0 的配置；技能进阶关联扫描该角色全部配置行。"],
  ["技能主数据", "preload_localdata_49784.bin / SkillBaseLO", tables.get("SkillBaseLO").length, "按技能 ID 关联名称、描述、图标键、效果 ID、条件和表现资源键。"],
  ["皮肤主数据", "preload_localdata_49784.bin / HeroDermaLO", tables.get("HeroDermaLO").length, "按 subType 关联角色；保留全部 125 条皮肤配置。"],
  ["原包美术目录", "local_game/resource/assets", assetFiles.length, "由原包资源恢复目录建立文件索引。路径为工作区相对路径，哈希后缀文件按逻辑资源键匹配。"],
  ["角色纳入口径", "HeroLO", heroRecords.length, "保留 subType 1–899 且存在展示标记或背景故事的角色；自动排除 900+ 测试木桩/内部角色。"],
  ["阵营映射", "recovered_runtime/main.formatted.js / HeroRaceConfig", 6, "1 魏国、2 蜀国、3 吴国、4 群雄、5 神族、6 魔族。"],
  ["职业映射", "recovered_runtime/main.formatted.js / ProfessionConfig", 5, "1 肉盾、2 战士、3 谋士、4 辅助、5 先锋。"],
  ["性别与星阶", "HeroLO / sexType、isStar", 0, "sexType：0 女、1 男；初始星阶码保留 isStar 原始值（如 50、55），不擅自换算显示星数。"],
  ["缺失值处理", "本工作簿口径", 0, "原包字段为空或资源文件未恢复时标注“原包未填写”“原包未发现”或“缺失”，不补写推测内容。"],
];
const sourceHeaders = ["来源/口径", "配置表或目录", "记录数", "说明"];
const sourceInfo = writeDataSheet(sourceSheet, "来源与汇总口径", "本工作簿只使用当前工作区中由原安装包恢复出的配置与资源，不采用联网资料或人工补写背景故事。", sourceHeaders, sourceRows, [18,58,14,88], "SourcesAndMethod");
sourceSheet.tabColor = "#8497B0";
sourceSheet.getRange(`C${sourceInfo.dataStart}:C${sourceInfo.endRow}`).format.numberFormat = "#,##0";
sourceSheet.getRange(`B${sourceInfo.dataStart}:D${sourceInfo.endRow}`).format.wrapText = true;
sourceSheet.getRange(`A${sourceInfo.dataStart}:D${sourceInfo.endRow}`).format.rowHeight = 44;

for (const sheet of [main, skillSheet, storySheet, artSheet, skinSheet, sourceSheet]) {
  const used = sheet.getUsedRange();
  if (used) used.format.verticalAlignment = "top";
}

workbook.recalculate();
await fs.mkdir(previewDir, { recursive: true });
const previews = [
  ["角色资产总表", "A1:Y22", "01-character-master.png"],
  ["技能明细", "A1:U18", "02-skills.png"],
  ["背景故事", "A1:H14", "03-stories.png"],
  ["美术资源", "A1:J18", "04-art-assets.png"],
  ["皮肤明细", "A1:R16", "05-skins.png"],
  ["来源与口径", "A1:D13", "06-sources.png"],
];
for (const [sheetName, range, fileName] of previews) {
  const preview = await workbook.render({ sheetName, range, scale: 1.05, format: "png" });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await preview.arrayBuffer()));
}

console.log((await workbook.inspect({ kind: "table", range: "角色资产总表!A1:Y16", include: "values,formulas", tableMaxRows: 16, tableMaxCols: 25, maxChars: 12000 })).ndjson);
console.log((await workbook.inspect({ kind: "table", range: "来源与口径!A1:D13", include: "values,formulas", tableMaxRows: 13, tableMaxCols: 4, maxChars: 8000 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" })).ndjson);

await fs.mkdir(outputDir, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(JSON.stringify({
  outputPath,
  counts: { heroes: heroRecords.length, skills: skillRows.length, stories: storyRows.length, skins: skinRows.length, art: artRows.length },
}, null, 2));
