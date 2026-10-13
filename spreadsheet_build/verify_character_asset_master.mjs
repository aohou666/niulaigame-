import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const workbookPath = String.raw`C:\Users\admin\Documents\ChatGPT\安装\outputs\character-asset-master\角色资产总表.xlsx`;
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(workbookPath));
console.log((await workbook.inspect({ kind: "sheet,table", maxChars: 12000, tableMaxRows: 3, tableMaxCols: 8 })).ndjson);
console.log((await workbook.inspect({ kind: "table", range: "角色资产总表!A5:Y12", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 25, maxChars: 12000 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 300 }, summary: "saved workbook formula error scan" })).ndjson);
