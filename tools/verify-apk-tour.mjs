/* Screen tour inside the packaged APK: main, heroes and a demo battle.
 * Records missing-resource console noise and the ultimate overlay counters. */
import fs from 'node:fs/promises';

const out = 'outputs/apk-build';
const list = await (await fetch('http://127.0.0.1:9222/json')).json();
const page = list.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pend = new Map();
const consoleMsgs = [];
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); return; }
  if (m.method === 'Runtime.consoleAPICalled') {
    const text = (m.params.args || []).map(a => a.value ?? a.description ?? '').join(' ');
    if (/找不到|not found|404|Uncaught|failed/i.test(text) && consoleMsgs.length < 60) consoleMsgs.push(text.slice(0, 220));
  }
});
await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
const send = (method, params = {}) => { const i = ++id; ws.send(JSON.stringify({id: i, method, params})); return new Promise((resolve, reject) => pend.set(i, {resolve, reject})); };
await send('Runtime.enable');
await send('Page.enable');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ev = async expr => {
  const r = await send('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) return {err: r.exceptionDetails.text};
  return r.result.value;
};
const report = {pass: false, screens: []};
const shot = async name => {
  const r = await send('Page.captureScreenshot', {format: 'png'});
  await fs.writeFile(`${out}/slim-${name}.png`, Buffer.from(r.data, 'base64'));
};

for (const mode of ['main', 'heroes', 'demo']) {
  consoleMsgs.length = 0;
  await send('Page.navigate', {url: `http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=${mode}`});
  await sleep(mode === 'demo' ? 26000 : 16000);
  if (mode === 'demo') await sleep(18000);
  const state = await ev(`({url: location.href,
    ultimate: window.StreetUltimate ? StreetUltimate.snapshot() : null,
    body: window.StreetBody ? StreetBody.snapshot() : null,
    payload: window.OfflineLastBattlePayload ? {engine: OfflineLastBattlePayload.offlineCombatEngine} : null,
    errs: (window.__streetErrors||[]).slice(0,5)})`);
  await shot(mode);
  report.screens.push({mode, ultimate: state.ultimate ? {
    matched: state.ultimate.matched, overlays: state.ultimate.overlays, frames: state.ultimate.frames,
    finished: state.ultimate.finished, errors: state.ultimate.errors} : null,
    bodyFrames: state.body ? state.body.framesPresented : null,
    bodyErrors: state.body ? state.body.errors : null,
    payload: state.payload, pageErrors: state.errs, missing: consoleMsgs.slice(-8)});
}
report.pass = report.screens.every(s => (s.missing || []).length === 0) &&
  report.screens[2].ultimate && report.screens[2].ultimate.frames > 10;
await fs.writeFile(`${out}/slim-verify.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify({pass: report.pass, screens: report.screens.map(s => ({mode: s.mode, frames: s.ultimate?.frames || 0, matched: s.ultimate?.matched || 0, missing: (s.missing || []).length}))}));
ws.close();
