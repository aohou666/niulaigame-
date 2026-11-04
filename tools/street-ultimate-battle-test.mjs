/* Real-battle verification for the ultimate overlay.
 *
 * Runs the offline demo battle on the isolated 8794 save, captures the live
 * battle layers through the game's own handleEffectQP, then plays two heroes'
 * ultimate containers exactly the way handleEffectQP would (same offset,
 * z-order, timeScale) so the overlay can be judged on the real battlefield.
 * The save is backed up and restored; the main save is verified unchanged. */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out = 'outputs/street-reskin/ultimate-verify/battle';
await fs.mkdir(out, {recursive: true});
const savePath = 'outputs/street-reskin/stress/8794-save.json';
const before = await fs.readFile(savePath);
const main = 'pc_server_data/offline-replica-save.json';
const mainSha = crypto.createHash('sha256').update(await fs.readFile(main)).digest('hex');
const heroes = (process.argv.find(x => x.startsWith('--heroes='))?.slice(9) || '1,83,45').split(',').map(Number);
const b = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
const page = await b.newPage({viewport: {width: 720, height: 1280}, deviceScaleFactor: 1});
const errors = []; page.on('pageerror', e => errors.push(e.message));
const report = {pass: false, heroes, shots: []};
try {
  await page.addInitScript(() => {
    window.__layers = null;
    const timer = setInterval(() => {
      if (!window.game || !game.FightTools) return;
      clearInterval(timer);
      const proto = game.FightTools.prototype;
      const orig = proto.handleEffectQP;
      proto.handleEffectQP = function () {
        if (!window.__layers) {
          window.__layers = {battleLayer: this.battleLayer, effLayer: this.effLayer,
            timeScale: this.timeScale, flowScaleX: this.fightFlowMgr && this.fightFlowMgr.scaleX};
        }
        return orig.apply(this, arguments);
      };
    }, 10);
  });
  await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo', {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.OfflineLastBattlePayload && window.__layers, null, {timeout: 120000});
  await page.waitForTimeout(2500);
  const layers = await page.evaluate(() => ({battle: {w: window.__layers.battleLayer.width, h: window.__layers.battleLayer.height},
    eff: {w: window.__layers.effLayer.width, h: window.__layers.effLayer.height}, timeScale: window.__layers.timeScale, flowScaleX: window.__layers.flowScaleX}));
  report.layers = layers;
  const played = [];
  for (const id of heroes) {
    const res = await page.evaluate(async (heroId) => {
      const hero = StreetUltimateData.heroes[String(heroId)];
      if (!hero) return {heroId, error: 'no data'};
      const key = (hero.keys.length ? hero.keys : hero.allKeys)[0];
      if (!hero.keys.length) {
        StreetUltimate.noteCast({effectsTarEnemy: [{src: [key]}]}, {config: {code: 41010000 + heroId}});
      }
      const eff = window.__layers.effLayer;
      const layer = window.__layers.battleLayer;
      const e = Utils.MsgUtils.getSimpleEffect(key, eff);
      if (!e) return {heroId, error: 'no effect'};
      e.autoRemove = true;
      e.timeScale = (window.__layers.timeScale || 1) * 1.0;
      e.scaleX = (window.__layers.flowScaleX || 1);
      e.scaleY = 1;
      e.x = layer.width / 2;
      e.y = layer.height / 2;
      e.zIndex = 10000;
      window.__last = e;
      const t0 = performance.now();
      e.trigger(key, () => {}, 1, null, null, false);
      return {heroId, key, x: e.x, y: e.y, scaleX: e.scaleX, timeScale: e.timeScale, t0};
    }, id);
    played.push(res);
    const shots = [];
    for (const ms of [260, 420, 420]) {
      await page.waitForTimeout(ms);
      const snap = await page.evaluate(() => ({s: StreetUltimate.snapshot(),
        fxVisible: window.__last ? window.__last.visible : null, onStage: window.__last ? !!window.__last.stage : null}));
      const name = `${String(id).padStart(3, '0')}-${shots.length}`;
      await page.screenshot({path: `${out}/${name}.png`});
      shots.push({name, frames: snap.s.frames, overlays: snap.s.overlays, active: snap.s.active.length,
        fxVisible: snap.fxVisible, onStage: snap.onStage, errors: snap.s.errors});
    }
    await page.waitForTimeout(3200);
    const end = await page.evaluate(() => ({s: StreetUltimate.snapshot(), fxOnStage: window.__last ? !!window.__last.stage : null}));
    const own = (end.s.finished || []).filter(x => x.heroId === id).pop();
    const ownActive = (end.s.active || []).some(x => x.heroId === id);
    report.shots.push({heroId: id, shots, end: {ownActive, own: own || null, finished: end.s.finished.slice(-1), fxOnStage: end.fxOnStage}});
  }
  report.played = played;
  report.errors = errors;
  const lastSnap = await page.evaluate(() => StreetUltimate.snapshot());
  report.final = lastSnap;
  report.pass = errors.length === 0 && report.shots.every(s => s.end.own &&
    s.shots.every(x => x.fxVisible === false) && s.shots.some(x => x.active >= 1) && !s.end.ownActive);
  console.log(JSON.stringify({pass: report.pass, shots: report.shots.map(s => ({hero: s.heroId, frames: s.shots.map(x => x.frames), end: s.end})), errors}, null, 1));
} catch (e) {
  report.error = e.stack;
  await page.screenshot({path: `${out}/failure.png`}).catch(() => {});
  console.log(JSON.stringify({pass: false, error: e.message}));
} finally {
  await b.close();
  await fs.writeFile(savePath, before);
  report.isolatedSaveRestored = Buffer.compare(await fs.readFile(savePath), before) === 0;
  report.mainSaveUnchanged = crypto.createHash('sha256').update(await fs.readFile(main)).digest('hex') === mainSha;
  await fs.writeFile(`${out}/report.json`, JSON.stringify(report, null, 2));
  console.log(JSON.stringify({saved: true, restored: report.isolatedSaveRestored, main: report.mainSaveUnchanged}));
}
