import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const sourcePath = String.raw`C:\Users\admin\Documents\ChatGPT\安装\英雄技能导出\英雄技能_原始关联.json`;
const outputDir = String.raw`C:\Users\admin\Documents\ChatGPT\安装\outputs\hero-skill-table`;
const outputPath = `${outputDir}\\英雄技能总表.xlsx`;
const previewDir = `${outputDir}\\previews`;
const font = "Arial";
const navy = "#1F4E78";
const blue = "#D9EAF7";
const pale = "#EEF5FA";
const border = "#B8C7D1";
const text = "#1F2937";

const raw = JSON.parse(await fs.readFile(sourcePath, "utf8"));
const rows = raw.rows.map((r) => ({
  heroCode: Number(r.heroCode),
  heroName: r.heroName,
  race: Number(r.race),
  profession: Number(r.profession),
  initStar: Number(r.initStar),
  slot: r.slot,
  skillId: Number(r.skillId),
  skillName: r.skillName,
  action: Number(r.action),
  angerCost: Number(r.angerCost),
  level: Number(r.level),
  desc: r.desc,
  tapDesc: r.tapDesc || "",
}));

rows.sort((a, b) =>
  a.heroName.localeCompare(b.heroName, "zh-CN") ||
  a.slot.localeCompare(b.slot, "zh-CN") ||
  a.skillName.localeCompare(b.skillName, "zh-CN") ||
  a.level - b.level ||
  a.heroCode - b.heroCode
);

const dedupMap = new Map();
for (const r of rows) {
  const key = [r.heroName, r.slot, r.skillName, r.desc].join("\u0001");
  if (!dedupMap.has(key)) dedupMap.set(key, r);
}
const dedup = [...dedupMap.values()];

const heroGroups = new Map();
for (const r of dedup) {
  if (!heroGroups.has(r.heroName)) heroGroups.set(r.heroName, []);
  heroGroups.get(r.heroName).push(r);
}
const summaryRows = [...heroGroups.entries()].map(([name, list]) => ({
  heroName: name,
  records: list.length,
  normal: list.filter((x) => x.slot === "普攻").length,
  active: list.filter((x) => x.slot === "主动").length,
  passive: list.filter((x) => x.slot.startsWith("被动")).length,
  maxLevel: Math.max(...list.map((x) => x.level)),
})).sort((a, b) => a.heroName.localeCompare(b.heroName, "zh-CN"));

const workbook = Workbook.create();
const overview = workbook.worksheets.add("技能总览");
const clean = workbook.worksheets.add("去重技能");
const full = workbook.worksheets.add("完整关联");

function applyBase(sheet) {
  sheet.showGridLines = false;
  sheet.getRange("A1:K20000").format.font = { name: font, size: 10, color: text };
}

function styleTitle(sheet, title, subtitle, width) {
  sheet.getRange("A2").values = [[title]];
  sheet.getRange("A2").format.font = { name: font, size: 16, bold: true, color: navy };
  sheet.getRange(`A3:${width}3`).format.borders = { bottom: { style: "thin", color: navy } };
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange("A3").format.font = { name: font, size: 10, italic: true, color: "#5B6573" };
}

function styleHeader(range) {
  range.format.fill = navy;
  range.format.font = { name: font, size: 10, bold: true, color: "#FFFFFF" };
  range.format.horizontalAlignment = "center";
  range.format.verticalAlignment = "center";
  range.format.rowHeight = 25;
  range.format.borders = { preset: "inside", style: "thin", color: "#FFFFFF" };
}

function writeSkillSheet(sheet, title, subtitle, data, tableName) {
  applyBase(sheet);
  styleTitle(sheet, title, subtitle, "M");
  const headers = ["英雄编号", "英雄名称", "阵营代码", "职业代码", "初始星级", "技能槽位", "技能编号", "技能名称", "动作类型", "怒气消耗", "技能等级", "技能介绍", "点击说明"];
  const matrix = [headers, ...data.map((r) => [
    r.heroCode, r.heroName, r.race, r.profession, r.initStar, r.slot,
    r.skillId, r.skillName, r.action, r.angerCost, r.level, r.desc, r.tapDesc,
  ])];
  const endRow = 4 + data.length;
  sheet.getRange(`A4:M${endRow}`).values = matrix;
  styleHeader(sheet.getRange("A4:M4"));
  sheet.tables.add(`A4:M${endRow}`, true, tableName);
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(2);
  sheet.getRange(`A5:A${endRow}`).format.numberFormat = "0";
  sheet.getRange(`C5:E${endRow}`).format.numberFormat = "0";
  sheet.getRange(`G5:K${endRow}`).format.numberFormat = "0";
  sheet.getRange(`A5:K${endRow}`).format.verticalAlignment = "center";
  sheet.getRange(`L5:M${endRow}`).format.wrapText = true;
  sheet.getRange(`L5:M${endRow}`).format.verticalAlignment = "top";
  sheet.getRange("A:A").format.columnWidth = 14;
  sheet.getRange("B:B").format.columnWidth = 14;
  sheet.getRange("C:E").format.columnWidth = 10;
  sheet.getRange("F:F").format.columnWidth = 11;
  sheet.getRange("G:G").format.columnWidth = 15;
  sheet.getRange("H:H").format.columnWidth = 18;
  sheet.getRange("I:K").format.columnWidth = 10;
  sheet.getRange("L:L").format.columnWidth = 72;
  sheet.getRange("M:M").format.columnWidth = 32;
  sheet.getRange(`A4:M${endRow}`).format.borders = {
    insideHorizontal: { style: "thin", color: "#E5E7EB" },
    bottom: { style: "thin", color: border },
  };
}

applyBase(overview);
overview.tabColor = navy;
styleTitle(overview, "英雄技能总览", "来源：恢复出的客户端英雄配置与技能配置；重复皮肤、进阶和等级版本已在去重页合并。", "F");

const kpis = [
  ["不同英雄名称", summaryRows.length, "技能配置", Number(raw.skillCount)],
  ["去重技能记录", dedup.length, "完整关联记录", rows.length],
];
overview.getRange("A5:D6").values = kpis;
overview.getRange("A5:D6").format.borders = { preset: "all", style: "thin", color: border };
overview.getRange("A5:D6").format.verticalAlignment = "center";
overview.getRange("A5:D6").format.rowHeight = 28;
overview.getRange("A5:A6").format.fill = blue;
overview.getRange("C5:C6").format.fill = blue;
overview.getRange("A5:A6").format.font = { name: font, bold: true, color: navy };
overview.getRange("C5:C6").format.font = { name: font, bold: true, color: navy };
overview.getRange("B5:B6").format.font = { name: font, size: 12, bold: true, color: text };
overview.getRange("D5:D6").format.font = { name: font, size: 12, bold: true, color: text };
overview.getRange("B5:B6").format.numberFormat = "#,##0";
overview.getRange("D5:D6").format.numberFormat = "#,##0";

const summaryHeaders = ["英雄名称", "去重记录数", "普攻记录", "主动记录", "被动记录", "最高技能等级"];
const summaryMatrix = [summaryHeaders, ...summaryRows.map((r) => [r.heroName, r.records, r.normal, r.active, r.passive, r.maxLevel])];
const summaryEnd = 9 + summaryRows.length;
overview.getRange(`A9:F${summaryEnd}`).values = summaryMatrix;
styleHeader(overview.getRange("A9:F9"));
overview.tables.add(`A9:F${summaryEnd}`, true, "HeroSummaryTable");
overview.freezePanes.freezeRows(9);
overview.getRange(`B10:F${summaryEnd}`).format.numberFormat = "#,##0";
overview.getRange("A:A").format.columnWidth = 18;
overview.getRange("B:F").format.columnWidth = 14;
overview.getRange(`A10:F${summaryEnd}`).format.borders = { insideHorizontal: { style: "thin", color: "#E5E7EB" } };

clean.tabColor = "#4F81BD";
writeSkillSheet(clean, "英雄技能表（按名称去重）", "每行代表一个英雄、技能槽位、技能名称与描述组合；保留不同等级产生的描述差异。", dedup, "DedupSkillTable");

full.tabColor = "#A6A6A6";
writeSkillSheet(full, "英雄技能完整关联", "包含皮肤、进阶、英雄代码和技能等级造成的全部重复与变体记录。", rows, "FullSkillTable");

workbook.recalculate();
await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, fileName] of [
  ["技能总览", "A1:F28", "01-overview.png"],
  ["去重技能", "A1:M18", "02-dedup.png"],
  ["完整关联", "A1:M18", "03-full.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1.2, format: "png" });
  await fs.writeFile(`${previewDir}\\${fileName}`, new Uint8Array(await preview.arrayBuffer()));
}

console.log((await workbook.inspect({ kind: "table", range: "技能总览!A1:F20", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 8, maxChars: 5000 })).ndjson);
console.log((await workbook.inspect({ kind: "table", range: "去重技能!A1:M10", include: "values,formulas", tableMaxRows: 10, tableMaxCols: 13, maxChars: 5000 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "final formula error scan" })).ndjson);

await fs.mkdir(outputDir, { recursive: true });
const out = await SpreadsheetFile.exportXlsx(workbook);
await out.save(outputPath);
console.log(`OUTPUT=${outputPath}`);
