/* Raw CDP client for the APK's WebView (Android WebView exposes a page-level
 * devtools socket, not a browser one, so Playwright's connectOverCDP cannot be
 * used). Verifies the ultimate overlay inside the packaged app. */
import fs from 'node:fs/promises';

const out = 'outputs/apk-build';
const base = 'http://127.0.0.1:9222';

async function targets() {
  const res = await fetch(`${base}/json`);
  return res.json();
}

function client(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const {resolve, reject} = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  });
  const ready = new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve);
    ws.addEventListener('error', reject);
  });
  return {
    ready,
    send(method, params = {}) {
      const mid = ++id;
      ws.send(JSON.stringify({id: mid, method, params}));
      return new Promise((resolve, reject) => pending.set(mid, {resolve, reject}));
    },
    close() { ws.close(); },
  };
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
const report = {pass: false};
const list = await targets();
const page = list.find(t => t.type === 'page');
if (!page) { console.log(JSON.stringify({pass: false, error: 'no page'})); process.exit(1); }
const c = client(page.webSocketDebuggerUrl);
await c.ready;
await c.send('Runtime.enable');
await c.send('Page.enable');

const evaluate = async expr => {
  const r = await c.send('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) return {error: r.exceptionDetails.text};
  return r.result.value;
};

try {
  report.before = await evaluate(`({url: location.href,
    ultimate: window.StreetUltimate ? StreetUltimate.snapshot() : null,
    heroes: window.StreetUltimateData ? Object.keys(StreetUltimateData.heroes).length : 0})`);
  await c.send('Page.navigate', {url: 'http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=demo'});
  let payload = null;
  for (let i = 0; i < 40; i++) {
    await sleep(3000);
    payload = await evaluate(`window.OfflineLastBattlePayload ? {engine: OfflineLastBattlePayload.offlineCombatEngine, allies: OfflineLastBattlePayload.teams[0].entities.length} : null`);
    const snap = await evaluate(`window.StreetUltimate ? StreetUltimate.snapshot() : null`);
    if (snap && (snap.matched || 0) >= 1 && (snap.frames || 0) > 10) break;
  }
  await sleep(6000);
  report.after = await evaluate(`({payload: window.OfflineLastBattlePayload ? {engine: OfflineLastBattlePayload.offlineCombatEngine, allies: OfflineLastBattlePayload.teams[0].entities.length} : null,
    ultimate: window.StreetUltimate ? StreetUltimate.snapshot() : null,
    consoleErrors: (window.__streetErrors || []).slice(0, 5)})`);
  const shot = await c.send('Page.captureScreenshot', {format: 'png'});
  await fs.writeFile(`${out}/apk-battle.png`, Buffer.from(shot.data, 'base64'));
  const s = report.after.ultimate || {};
  report.pass = !!report.after.payload && (s.matched || 0) >= 1 && (s.frames || 0) > 10;
  console.log(JSON.stringify({pass: report.pass, matched: s.matched, overlays: s.overlays, frames: s.frames,
    finished: s.finished, errors: s.errors, before: report.before.heroes}));
} catch (e) {
  report.error = String(e && e.stack || e);
  console.log(JSON.stringify({pass: false, error: String(e && e.message || e)}));
}
await fs.writeFile(`${out}/apk-verify.json`, JSON.stringify(report, null, 2));
c.close();
