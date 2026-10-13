import fs from "node:fs/promises";
import vm from "node:vm";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = String.raw`C:\Users\admin\Documents\ChatGPT\安装`;
const outputDir = path.join(root, "outputs", "game-config-summary");
const outputPath = path.join(outputDir, "原包与当前包体-游戏配置总表.xlsx");
const previewDir = path.join(outputDir, "previews");
const extractOnly = process.argv.includes("--extract-only");
const dumpData = process.argv.includes("--dump-data");

const formattedSourcePath = path.join(root, "recovered_runtime", "main.formatted.js");
const localBinPath = path.join(root, "local_game", "resource", "localdata", "localdata_49784.bin");
const preloadBinPath = path.join(root, "local_game", "resource", "localdata", "preload_localdata_49784.bin");
const currentConfigPath = path.join(root, "pc_server_data", "offline-replica-config.json");
const runtimeCatalogPath = path.join(root, "pc_server_data", "offline-runtime-catalog.json");
const currentSavePath = path.join(root, "pc_server_data", "offline-replica-save.json");
const currentHtmlPath = path.join(root, "local_game", "index_bh_lite3zbtest_andr.html");
const currentUiPath = path.join(root, "local_game", "offline-ui.js");
const originalApkPath = path.join(root, "apk_analysis", "package_test", "original.apk");
const currentApkPath = path.join(root, "离线复刻测试-v0.18-原包界面与世界状态修复版.apk");

class Reader {
  constructor(buffer) { this.buffer = buffer; this.offset = 0; }
  readByte() { return this.buffer[this.offset++]; }
  readShort() {
    const value = this.buffer[this.offset] | (this.buffer[this.offset + 1] << 8);
    this.offset += 2;
    return value;
  }
  readInt() {
    const value = this.buffer[this.offset] | (this.buffer[this.offset + 1] << 8) |
      (this.buffer[this.offset + 2] << 16) | (this.buffer[this.offset + 3] << 24);
    this.offset += 4;
    return value;
  }
  readLong() {
    let value = 0n;
    for (let i = 0; i < 8; i++) value |= BigInt(this.buffer[this.offset++]) << BigInt(i * 8);
    return value <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(value) : value.toString();
  }
  readBoolean() { return Boolean(this.buffer[this.offset++]); }
  readNumber() { return Number(this.readString()); }
  readString() {
    let length = 0;
    let shift = 0;
    while (true) {
      const byte = this.buffer[this.offset++];
      length |= (byte & 0x7f) << shift;
      if (!(byte & 0x80)) break;
      shift += 7;
    }
    const start = this.offset;
    this.offset += length;
    return new TextDecoder("utf-8").decode(this.buffer.subarray(start, start + length));
  }
}

function quickLzDecompress(input) {
  const headerLen = (input[0] & 2) === 2 ? 9 : 3;
  const outLength = headerLen === 9
    ? input[5] | (input[6] << 8) | (input[7] << 16) | (input[8] << 24)
    : input[2];
  if (!(input[0] & 1)) return input.slice(headerLen, headerLen + outLength);
  const level = (input[0] >> 2) & 3;
  if (level !== 1 && level !== 3) throw new Error(`Unsupported QuickLZ level ${level}`);
  let src = headerLen, dst = 0, cword = 1, lastMatch = -1, fetch = 0;
  const output = new Uint8Array(outLength);
  const hash = new Int32Array(4096);
  const hasHash = new Uint8Array(4096);
  const guaranteed = outLength - 6 - 4 - 1;
  while (true) {
    if (cword === 1) {
      cword = input[src] | (input[src + 1] << 8) | (input[src + 2] << 16) | (input[src + 3] << 24);
      src += 4;
      fetch = level === 1
        ? input[src] | (input[src + 1] << 8) | (input[src + 2] << 16)
        : input[src] | (input[src + 1] << 8) | (input[src + 2] << 16) | (input[src + 3] << 24);
    }
    if (cword & 1) {
      cword >>>= 1;
      let matchLength, matchOffset;
      if (level === 1) {
        const h = (fetch >> 4) & 4095;
        matchOffset = hash[h];
        if (fetch & 15) { matchLength = (fetch & 15) + 2; src += 2; }
        else { matchLength = input[src + 2]; src += 3; }
      } else {
        let distance;
        if ((fetch & 3) === 0) { distance = (fetch & 255) >> 2; matchLength = 3; src += 1; }
        else if ((fetch & 2) === 0) { distance = (fetch & 65535) >> 2; matchLength = 3; src += 2; }
        else if ((fetch & 1) === 0) { distance = (fetch & 65535) >> 6; matchLength = ((fetch >> 2) & 15) + 3; src += 2; }
        else if ((fetch & 127) !== 3) { distance = (fetch >> 7) & 131071; matchLength = ((fetch >> 2) & 31) + 2; src += 3; }
        else { distance = fetch >> 15; matchLength = ((fetch >> 7) & 255) + 3; src += 4; }
        matchOffset = dst - distance;
      }
      output[dst] = output[matchOffset];
      output[dst + 1] = output[matchOffset + 1];
      output[dst + 2] = output[matchOffset + 2];
      for (let i = 3; i < matchLength; i++) output[dst + i] = output[matchOffset + i];
      dst += matchLength;
      if (level === 1) {
        for (fetch = output[lastMatch + 1] | (output[lastMatch + 2] << 8) | (output[lastMatch + 3] << 16); dst - matchLength > lastMatch;) {
          lastMatch++;
          const h = ((fetch >> 12) ^ fetch) & 4095;
          hash[h] = lastMatch;
          hasHash[h] = 1;
          fetch = ((fetch >> 8) & 65535) | (output[lastMatch + 3] << 16);
        }
        fetch = input[src] | (input[src + 1] << 8) | (input[src + 2] << 16);
      } else {
        fetch = input[src] | (input[src + 1] << 8) | (input[src + 2] << 16) | (input[src + 3] << 24);
      }
      lastMatch = dst - 1;
    } else {
      if (dst > guaranteed) {
        while (dst < outLength) {
          if (cword === 1) { src += 4; cword = 0x80000000; }
          output[dst++] = input[src++];
          cword >>>= 1;
        }
        return output;
      }
      output[dst++] = input[src++];
      cword >>>= 1;
      if (level === 1) {
        while (dst - 3 > lastMatch) {
          lastMatch++;
          const triple = output[lastMatch] | (output[lastMatch + 1] << 8) | (output[lastMatch + 2] << 16);
          const h = ((triple >> 12) ^ triple) & 4095;
          hash[h] = lastMatch;
          hasHash[h] = 1;
        }
        fetch = ((fetch >> 8) & 65535) | (input[src + 2] << 16);
      } else {
        fetch = ((fetch >> 8) & 65535) | (input[src + 2] << 16) | (input[src + 3] << 24);
      }
    }
  }
}

function configCategory(name) {
  const rules = [
    ["英雄养成", /Hero|Summoner|Altar|Destiny|Resonate|Awaken|Handbook|LineUp/i],
    ["技能战斗", /Skill|Buff|Battle|Fight|Attribute|Property|Creep|Abstract|Halo/i],
    ["装备宝物", /Equip|Treasure|Magical|Runestone|Chaks|Kit|Mount|Artifact|Catilla|Jewel/i],
    ["关卡挂机", /Stage|Chapter|HangUp|Champion|Tower|Trial|Abyss|Maze|Dojo|Risk|Bridge/i],
    ["竞技玩法", /Arena|War|Boss|WorldKing|Fair|Peak|Storm|Expedition|Naval/i],
    ["天下地图", /WorldEmpires|CaptureCities|City|Mine|Guild|Manor|Fortress|Map/i],
    ["任务活动", /Task|Activity|Achievement|Reward|Gift|Gashapon|Turntable|Sign|Mail/i],
    ["经济商店", /Item|Shop|Cost|Price|Buy|Exchange|Market|Recharge|Vip|Drop/i],
    ["引导系统", /Guide|Unlock|Entrance|Help|Error|Broadcast|Name|Head|Const/i],
  ];
  for (const [category, regex] of rules) if (regex.test(name)) return category;
  return "其他系统";
}

function guessKey(row, index) {
  for (const key of ["id", "code", "key", "subType", "level", "type", "stageId", "chapterCode", "moduleId"]) {
    if (row?.[key] !== undefined && row[key] !== null) return String(row[key]);
  }
  return String(index + 1);
}

function guessName(row) {
  for (const key of ["name", "showName", "title", "desc", "shortDesc", "moduleName"]) {
    if (row?.[key] !== undefined && row[key] !== null) return String(row[key]).slice(0, 200);
  }
  return "";
}

function sanitizeJson(value) {
  const text = JSON.stringify(value, (_k, v) => typeof v === "bigint" ? v.toString() : v);
  return text.length <= 32000 ? text : `${text.slice(0, 31980)}…[截断]`;
}

function parseConfigClasses(source) {
  const tolerantJson = {
    parse(value) {
      if (value === "" || value === null || value === undefined) return "";
      try { return JSON.parse(value); } catch { return value; }
    },
    stringify: JSON.stringify,
  };
  const context = vm.createContext({
    config: {},
    game: { Config: { pack: {} } },
    __reflect: () => {},
    console: { log() {}, warn() {}, error() {} },
    JSON: tolerantJson, Map, Array, Object, Number, String, Boolean, Math,
  });
  const chunks = source.split("var config;");
  const failures = [];
  for (const raw of chunks) {
    if (!raw.includes("parseData = function")) continue;
    const chunk = `var config = globalThis.config;${raw}`;
    try { vm.runInContext(chunk, context, { timeout: 1000 }); }
    catch (error) { failures.push(String(error.message || error)); }
  }
  return { config: context.config, failures };
}

function parserOrder(source, parserName) {
  const marker = `e.${parserName} = t`;
  const end = source.indexOf(marker);
  if (end < 0) throw new Error(`Parser ${parserName} not found`);
  const start = source.lastIndexOf("var config;", end);
  const chunk = source.slice(start, end);
  return [...chunk.matchAll(/this\._dic\.add\(\s*"([A-Za-z0-9_]+LO)"/g)].map((m) => m[1]);
}

async function parseBinary(filePath, sourceName, order, classes) {
  const compressed = new Uint8Array(await fs.readFile(filePath));
  const decompressed = quickLzDecompress(compressed);
  const reader = new Reader(decompressed);
  const version = reader.readInt();
  const branch = reader.readString();
  const tables = [];
  for (const tableName of order) {
    if (reader.offset >= decompressed.length) break;
    const blockStart = reader.offset;
    const byteLength = reader.readInt();
    const endOffset = blockStart + byteLength;
    const rowCount = reader.readInt();
    const rows = [];
    let error = "";
    const cls = classes[tableName];
    if (!cls?.parseData) {
      error = "未找到解析类";
    } else {
      try {
        for (let i = 0; i < rowCount; i++) rows.push(cls.parseData(reader));
      } catch (e) {
        error = String(e.message || e);
      }
    }
    const consumed = reader.offset;
    if (reader.offset !== endOffset) reader.offset = endOffset;
    const fields = [...new Set(rows.flatMap((row) => Object.keys(row || {})))];
    tables.push({ tableName, sourceName, category: configCategory(tableName), rowCount, rows, fields, byteLength, consumedBytes: consumed - blockStart, status: error || "已解析" });
  }
  return { sourceName, version, branch, decompressedBytes: decompressed.length, tables };
}

function flattenObject(value, prefix = "", rows = []) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => flattenObject(item, `${prefix}[${index}]`, rows));
  } else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) flattenObject(item, prefix ? `${prefix}.${key}` : key, rows);
  } else {
    rows.push([prefix, value === null ? "null" : value, typeof value]);
  }
  return rows;
}

function extractCurrentRules(html, ui) {
  const rows = [];
  for (const match of html.matchAll(/\{ moduleId:\s*(\d+), module:\s*"([^"]+)", action:\s*"([^"]+)", name:\s*"([^"]+)" \}/g)) {
    rows.push(["历练入口", match[2], match[4], Number(match[1]), match[3], "index_bh_lite3zbtest_andr.html"]);
  }
  for (const match of ui.matchAll(/\{id:"([^"]+)",name:"([^"]+)",desc:"([^"]*)",offset:(\d+),color:"([^"]+)"\}/g)) {
    rows.push(["战斗场景", match[1], match[2], Number(match[4]), match[3], `颜色 ${match[5]}；offline-ui.js`]);
  }
  return rows;
}

function statFile(filePath) {
  return fs.stat(filePath).then((s) => ({ path: filePath, bytes: s.size, modified: s.mtime }));
}

function styleSheet(sheet) {
  sheet.showGridLines = false;
}

function styleTitle(sheet, title, note, lastCol) {
  sheet.getRange("A2").values = [[title]];
  sheet.getRange("A2").format.font = { name: "Arial", size: 16, bold: true, color: "#17365D" };
  sheet.getRange(`A3:${lastCol}3`).format.borders = { bottom: { style: "thin", color: "#17365D" } };
  sheet.getRange("A3").values = [[note]];
  sheet.getRange("A3").format.font = { name: "Arial", size: 10, italic: true, color: "#5B6573" };
}

function styleHeader(range) {
  range.format.fill = "#1F4E78";
  range.format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
  range.format.horizontalAlignment = "center";
  range.format.verticalAlignment = "center";
  range.format.rowHeight = 25;
  range.format.borders = { insideVertical: { style: "thin", color: "#FFFFFF" } };
}

function writeTableSheet(sheet, title, note, headers, rows, widths, tableName) {
  styleSheet(sheet);
  const lastCol = String.fromCharCode(64 + headers.length);
  styleTitle(sheet, title, note, lastCol);
  const endRow = 4 + rows.length;
  sheet.getRange(`A4:${lastCol}${endRow}`).values = [headers, ...rows];
  styleHeader(sheet.getRange(`A4:${lastCol}4`));
  if (rows.length && rows.length <= 100000) sheet.tables.add(`A4:${lastCol}${endRow}`, true, tableName);
  sheet.freezePanes.freezeRows(4);
  for (let i = 0; i < widths.length; i++) {
    const column = String.fromCharCode(65 + i);
    sheet.getRange(`${column}:${column}`).format.columnWidth = widths[i];
  }
  if (rows.length <= 100000) sheet.getRange(`A5:${lastCol}${endRow}`).format.verticalAlignment = "top";
  return endRow;
}

const formattedSource = await fs.readFile(formattedSourcePath, "utf8");
const { config: configClasses, failures: classFailures } = parseConfigClasses(formattedSource);
const localOrder = parserOrder(formattedSource, "LocalDataParser");
const preloadOrder = parserOrder(formattedSource, "PreloadLocalDataParser");
const [localParsed, preloadParsed] = await Promise.all([
  parseBinary(localBinPath, "localdata_49784.bin", localOrder, configClasses),
  parseBinary(preloadBinPath, "preload_localdata_49784.bin", preloadOrder, configClasses),
]);
const allTables = [...preloadParsed.tables, ...localParsed.tables];

const [currentConfig, runtimeCatalog, currentSave, currentHtml, currentUi, fileStats] = await Promise.all([
  fs.readFile(currentConfigPath, "utf8").then(JSON.parse),
  fs.readFile(runtimeCatalogPath, "utf8").then(JSON.parse),
  fs.readFile(currentSavePath, "utf8").then(JSON.parse),
  fs.readFile(currentHtmlPath, "utf8"),
  fs.readFile(currentUiPath, "utf8"),
  Promise.all([originalApkPath, currentApkPath, localBinPath, preloadBinPath, currentConfigPath, runtimeCatalogPath].map(statFile)),
]);
const currentRules = extractCurrentRules(currentHtml, currentUi);
const runtimeRows = [];
for (const [type, values] of Object.entries(runtimeCatalog)) {
  if (!Array.isArray(values)) continue;
  values.forEach((value, index) => runtimeRows.push([type, index + 1, guessKey(value, index), guessName(value), sanitizeJson(value)]));
}

const extractionSummary = {
  localVersion: localParsed.version,
  preloadVersion: preloadParsed.version,
  branch: localParsed.branch,
  tables: allTables.length,
  parsedTables: allTables.filter((t) => t.status === "已解析").length,
  records: allTables.reduce((sum, table) => sum + table.rows.length, 0),
  classFailures: classFailures.length,
  tableErrors: allTables.filter((t) => t.status !== "已解析").map((t) => ({ table: t.tableName, error: t.status })),
  categories: Object.fromEntries([...new Set(allTables.map((t) => t.category))].sort().map((c) => [c, allTables.filter((t) => t.category === c).reduce((sum, t) => sum + t.rowCount, 0)])),
};
console.log(JSON.stringify(extractionSummary, null, 2));
if (extractOnly) process.exit(0);

const allRecords = allTables.flatMap((table) => table.rows.map((row, index) => ({
  category: table.category,
  tableName: table.tableName,
  sourceName: table.sourceName,
  index: index + 1,
  key: guessKey(row, index),
  name: guessName(row),
  json: sanitizeJson(row),
})));

if (dumpData) {
  const stagingDir = path.join(outputDir, "staging");
  await fs.mkdir(stagingDir, { recursive: true });
  const metadata = {
    extractionSummary,
    tables: allTables.map(({ rows: _rows, ...table }) => table),
    currentConfig,
    runtimeCatalog,
    currentRules,
    currentSaveSummary: {
      version: currentSave.version,
      heroes: currentSave.heroes?.length || 0,
      formation: currentSave.formation?.length || 0,
      progress: currentSave.progress || {},
    },
    fileStats,
  };
  await fs.writeFile(path.join(stagingDir, "metadata.json"), JSON.stringify(metadata), "utf8");
  const handle = await fs.open(path.join(stagingDir, "records.ndjson"), "w");
  try {
    const batchSize = 5000;
    for (let i = 0; i < allRecords.length; i += batchSize) {
      const text = allRecords.slice(i, i + batchSize).map((row) => JSON.stringify(row)).join("\n") + "\n";
      await handle.write(text);
    }
  } finally {
    await handle.close();
  }
  console.log(`STAGING=${stagingDir}`);
  process.exit(0);
}

const workbook = Workbook.create();
const overview = workbook.worksheets.add("配置总览");
const catalog = workbook.worksheets.add("配置表目录");
const records = workbook.worksheets.add("全部配置记录");
const current = workbook.worksheets.add("当前离线规则");
const runtime = workbook.worksheets.add("当前可用目录");
const heroes = workbook.worksheets.add("英雄配置");
const skills = workbook.worksheets.add("技能配置");
const items = workbook.worksheets.add("装备物品配置");
const sources = workbook.worksheets.add("来源与说明");

styleSheet(overview);
overview.tabColor = "#17365D";
overview.getRange("A2:H24").format.font = { name: "Arial", size: 10, color: "#1F2937" };
styleTitle(overview, "原包与当前包体游戏配置总表", "原始数值表来自恢复出的 localdata 二进制；当前包体部分包含离线覆盖、当前运行目录与本地玩法规则。", "H");
overview.getRange("A5:H7").values = [
  ["原始配置表", allTables.length, "原始配置记录", allRecords.length, "当前英雄目录", runtimeCatalog.heroes?.length || 0, "当前技能目录", runtimeCatalog.skills?.length || 0],
  ["成功解析表", allTables.filter((t) => t.status === "已解析").length, "解析异常表", allTables.filter((t) => t.status !== "已解析").length, "当前皮肤目录", runtimeCatalog.skins?.length || 0, "当前美人技能", runtimeCatalog.beautySkills?.length || 0],
  ["数据版本", localParsed.version, "分支", localParsed.branch, "当前存档英雄", currentSave.heroes?.length || 0, "当前上阵人数", currentSave.formation?.length || 0],
];
overview.getRange("A5:H7").format.borders = { preset: "all", style: "thin", color: "#CBD5E1" };
for (const col of ["A", "C", "E", "G"]) {
  overview.getRange(`${col}5:${col}7`).format.fill = "#D9EAF7";
  overview.getRange(`${col}5:${col}7`).format.font = { name: "Arial", bold: true, color: "#17365D" };
}
overview.getRange("B5:H7").format.numberFormat = "#,##0";
const categoryRows = Object.entries(extractionSummary.categories).sort((a, b) => b[1] - a[1]);
overview.getRange(`A10:B${10 + categoryRows.length}`).values = [["系统分类", "配置记录数"], ...categoryRows];
styleHeader(overview.getRange("A10:B10"));
overview.tables.add(`A10:B${10 + categoryRows.length}`, true, "CategorySummary");
overview.getRange(`B11:B${10 + categoryRows.length}`).format.numberFormat = "#,##0";
overview.getRange("A:A").format.columnWidth = 18;
overview.getRange("B:H").format.columnWidth = 16;
overview.getRange("D10:H15").values = [
  ["口径说明", null, null, null, null],
  ["原包配置", "恢复缓存内的 preload/localdata 配置表，代表原游戏客户端数值底表。", null, null, null],
  ["当前包体", "v0.18 离线覆盖配置、当前运行时目录、本地玩法入口及规则。", null, null, null],
  ["完整记录", "每行保存一条配置记录的完整 JSON；复杂数组和嵌套字段不会被丢弃。", null, null, null],
  ["差异判断", "当前 heroes/skills/skins 覆盖为空，核心原始数值未被后台覆盖；离线玩法规则为新增层。", null, null, null],
  ["限制", "法律协议文本、玩家即时进度不作为玩法配置明细；存档仅用于统计当前可用范围。", null, null, null],
];
overview.getRange("D10:H10").format.fill = "#E2E8F0";
overview.getRange("D10").format.font = { name: "Arial", bold: true, color: "#17365D" };
overview.getRange("D11:H15").format.wrapText = true;
overview.getRange("D:D").format.columnWidth = 16;
overview.getRange("E:H").format.columnWidth = 20;

const sourceUseText = `${currentHtml}\n${currentUi}`;
const catalogRows = allTables.map((table) => [
  table.category, table.tableName, table.sourceName, table.rowCount, table.fields.length,
  table.fields.join(", "), (sourceUseText.match(new RegExp(`config\\.${table.tableName}`, "g")) || []).length,
  table.status,
]);
const catalogEnd = writeTableSheet(catalog, "原包配置表目录", "目录覆盖 preload 与完整 localdata；“当前离线引用次数”仅统计当前离线补丁源码中的直接引用。", ["系统", "配置表", "源文件", "记录数", "字段数", "字段列表", "当前离线引用次数", "解析状态"], catalogRows, [14, 30, 28, 12, 10, 72, 18, 16], "ConfigCatalog");
catalog.getRange(`D5:E${catalogEnd}`).format.numberFormat = "#,##0";
catalog.getRange(`G5:G${catalogEnd}`).format.numberFormat = "#,##0";
catalog.getRange(`F5:F${catalogEnd}`).format.wrapText = true;

const recordRows = allRecords.map((r) => [r.category, r.tableName, r.sourceName, r.index, r.key, r.name, r.json]);
const recordEnd = writeTableSheet(records, "全部原始配置记录", "每行对应原包配置表的一条记录；完整 JSON 保留嵌套数组、奖励、条件与属性结构。", ["系统", "配置表", "源文件", "序号", "主键", "名称/说明", "完整配置 JSON"], recordRows, [14, 28, 28, 10, 18, 28, 110], "AllConfigRecords");
records.freezePanes.freezeColumns(2);
records.getRange(`D5:D${recordEnd}`).format.numberFormat = "#,##0";
records.getRange(`G5:G${recordEnd}`).format.wrapText = false;

const configRows = flattenObject(currentConfig).map(([p, v, t]) => ["后台覆盖配置", p, v, t, currentConfigPath]);
const currentRuleRows = currentRules.map((r) => [r[0], `${r[1]}.${r[3]}`, r[2], typeof r[3], `${r[4]}；${r[5]}`]);
const currentEnd = writeTableSheet(current, "当前离线包新增与覆盖规则", "包含 v0.18 后台配置以及当前源码中的历练入口和战斗场景。heroes/skills/skins/equips/assetAliases 当前均为空。", ["类型", "配置路径/标识", "当前值/名称", "值类型/编号", "来源/说明"], [...configRows, ...currentRuleRows], [18, 40, 30, 18, 72], "CurrentOfflineRules");
current.getRange(`C5:E${currentEnd}`).format.wrapText = true;

const runtimeEnd = writeTableSheet(runtime, "当前包体可用对象目录", "由当前客户端运行后导出的英雄、技能、皮肤、装备、美人和美人技能目录；用于确认离线包实际可选择范围。", ["对象类型", "序号", "主键", "名称", "完整配置 JSON"], runtimeRows, [18, 10, 20, 26, 110], "RuntimeCatalog");
runtime.getRange(`B5:B${runtimeEnd}`).format.numberFormat = "#,##0";

function rowsForTables(regex) {
  return allRecords.filter((r) => regex.test(r.tableName)).map((r) => [r.tableName, r.index, r.key, r.name, r.json]);
}
const heroEnd = writeTableSheet(heroes, "英雄及主角配置", "汇总 Hero、Summoner、皮肤、图鉴、羁绊、升阶、升级、升星及阵容相关原始配置。", ["配置表", "序号", "主键", "名称/说明", "完整配置 JSON"], rowsForTables(/^(Hero|Summoner|Handbook|LineUp|Altar)/i), [30, 10, 18, 28, 110], "HeroConfigRecords");
heroes.getRange(`B5:B${heroEnd}`).format.numberFormat = "#,##0";
const skillEnd = writeTableSheet(skills, "技能、Buff与战斗配置", "汇总技能、Buff、属性、战斗帮助、兵种与敌方单位相关原始配置。", ["配置表", "序号", "主键", "名称/说明", "完整配置 JSON"], rowsForTables(/Skill|Buff|Battle|Attribute|Property|Creep|Abstract|Halo/i), [30, 10, 18, 28, 110], "SkillConfigRecords");
skills.getRange(`B5:B${skillEnd}`).format.numberFormat = "#,##0";
const itemEnd = writeTableSheet(items, "装备、物品与养成载体配置", "汇总装备、物品、宝物、神兵、符石、锦囊、坐骑及虎符相关原始配置。", ["配置表", "序号", "主键", "名称/说明", "完整配置 JSON"], rowsForTables(/Item|Equip|Treasure|Magical|Runestone|Chaks|Kit|Mount|Artifact|Catilla|Jewel/i), [30, 10, 18, 28, 110], "ItemConfigRecords");
items.getRange(`B5:B${itemEnd}`).format.numberFormat = "#,##0";

const sourceRows = fileStats.map((s) => [path.relative(root, s.path), s.bytes, s.modified, s.path === originalApkPath ? "原始安装包" : s.path === currentApkPath ? "当前发布 APK" : "配置来源"]);
sourceRows.push(["recovered_runtime/main.formatted.js", (await fs.stat(formattedSourcePath)).size, (await fs.stat(formattedSourcePath)).mtime, "配置字段定义与二进制解析顺序"]);
sourceRows.push(["local_game/resource/config/g_skill_96a92798.json", (await fs.stat(path.join(root, "local_game", "resource", "config", "g_skill_96a92798.json"))).size, (await fs.stat(path.join(root, "local_game", "resource", "config", "g_skill_96a92798.json"))).mtime, "技能表现映射，233 个顶级键；未重复展开到数值表"]);
sourceRows.push(["local_game/resource/config/g_help_7c756b4f.json", (await fs.stat(path.join(root, "local_game", "resource", "config", "g_help_7c756b4f.json"))).size, (await fs.stat(path.join(root, "local_game", "resource", "config", "g_help_7c756b4f.json"))).mtime, "协议与帮助文本，非玩法数值表"]);
const sourceEnd = writeTableSheet(sources, "来源、口径与限制", "文件时间均来自当前工作区；本工作簿不把玩家即时存档值当作游戏设计配置。", ["来源文件", "字节数", "修改时间", "用途/口径"], sourceRows, [58, 16, 22, 72], "SourceFiles");
sources.getRange(`B5:B${sourceEnd}`).format.numberFormat = "#,##0";
sources.getRange(`C5:C${sourceEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
sources.getRange(`D5:D${sourceEnd}`).format.wrapText = true;

workbook.recalculate();
await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, fileName] of [
  ["配置总览", "A1:H24", "01-overview.png"],
  ["配置表目录", "A1:H22", "02-catalog.png"],
  ["当前离线规则", "A1:E24", "03-current.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1.1, format: "png" });
  await fs.writeFile(path.join(previewDir, fileName), new Uint8Array(await preview.arrayBuffer()));
}
console.log((await workbook.inspect({ kind: "table", range: "配置总览!A1:H20", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 8, maxChars: 6000 })).ndjson);
console.log((await workbook.inspect({ kind: "table", range: "配置表目录!A1:H12", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 8, maxChars: 6000 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" })).ndjson);

await fs.mkdir(outputDir, { recursive: true });
const out = await SpreadsheetFile.exportXlsx(workbook);
await out.save(outputPath);
console.log(`OUTPUT=${outputPath}`);
