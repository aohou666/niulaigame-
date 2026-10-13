"use strict";
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const root = __dirname;
const port = Number(process.env.PORT || 8791);
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json", ".png": "image/png" };
http.createServer((req, res) => {
  let relative;
  try { relative = decodeURIComponent(new URL(req.url, "http://localhost").pathname); }
  catch { res.writeHead(400); return res.end(); }
  const file = path.resolve(root, "." + (relative === "/" ? "/index.html" : relative));
  if (!file.startsWith(root + path.sep) || relative.includes("/runtime/") || !types[path.extname(file)]) {
    res.writeHead(404); return res.end("Not found");
  }
  fs.readFile(file, (error, data) => {
    if (error) { res.writeHead(404); return res.end("Not found"); }
    res.writeHead(200, { "Content-Type": types[path.extname(file)], "Cache-Control": "no-store" });
    res.end(data);
  });
}).listen(port, "127.0.0.1", () => console.log(`绿幕导帧工作台 http://127.0.0.1:${port}/ （Ctrl+C 关闭）`))
  .on("error", error => { console.error(error.code === "EADDRINUSE" ? `端口 ${port} 已被占用，请先关闭旧窗口。` : error.message); process.exitCode = 1; });
