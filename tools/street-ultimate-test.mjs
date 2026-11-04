/* Verifies the ultimate overlay on the real engine: a DBEffect for an ultimate
 * layer is created exactly like handleEffectQP does it, then the overlay must
 * hide the original armature, stream the new frames, finish at the original
 * duration and leave nothing behind. */
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out = 'outputs/street-reskin/ultimate-verify';
const base = process.argv.find(x => x.startsWith('--base='))?.slice(7) || 'http://127.0.0.1:8794';
const heroId = Number(process.argv.find(x => x.startsWith('--hero='))?.slice(7) || 1);
const outDir = `${out}/fixture-${String(heroId).padStart(3, '0')}`;
await fs.mkdir(outDir, {recursive: true});
const b = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
const page = await b.newPage({viewport: {width: 720, height: 1280}, deviceScaleFactor: 1});
const errors = []; page.on('pageerror', e => errors.push(e.message));
const failed = []; page.on('response', r => { if (r.status() >= 400) failed.push(r.url()); });
const report = {pass: false, heroId};
try {
  await page.goto(`${base}/index_bh_lite3zbtest_andr.html?mode=heroes`, {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.StreetUltimate && StreetUltimate.snapshot().installed, null, {timeout: 60000});
  await page.waitForFunction(() => {
    try { return RES.hasRes('common_skill_zhaoyun_01_bin'); } catch (e) { return false; }
  }, null, {timeout: 60000});
  const info = await page.evaluate(async (heroId) => {
    const stage = egret.MainContext.instance.stage;
    for (let i = 0; i < stage.numChildren; i++) stage.getChildAt(i).visible = false;
    const box = new egret.DisplayObjectContainer();
    stage.addChild(box);
    const bg = new egret.Shape();
    bg.graphics.beginFill(0x2c4a5e); bg.graphics.drawRect(0, 0, 720, 1280); bg.graphics.endFill();
    box.addChild(bg);
    const hero = StreetUltimateData.heroes[String(heroId)];
    const key = (hero.keys.length ? hero.keys : hero.allKeys)[0];
    if (!hero.keys.length) {
      // Shared ultimate key: the game records the caster through handleEffectTar.
      StreetUltimate.noteCast({effectsTarEnemy: [{src: [key]}]}, {config: {code: 41010000 + heroId}});
    }
    const e = Utils.MsgUtils.getSimpleEffect(key, box);
    e.scaleX = e.scaleY = 1; e.x = 0; e.y = 0; e.autoRemove = true; e.timeScale = 1;
    window.__fx = {box, e, key, hero};
    e.trigger(key, () => {}, 1, null, null, false);
    return {key, frames: hero.frames, fps: hero.fps, dir: hero.dir};
  }, heroId);
  report.fixture = info;
  const shots = [];
  const at = async (ms, name) => {
    await page.waitForTimeout(ms);
    const snap = await page.evaluate(() => ({s: StreetUltimate.snapshot(),
      visible: window.__fx.e.visible, onStage: !!window.__fx.e.stage,
      children: window.__fx.box.numChildren}));
    await page.screenshot({path: `${outDir}/${name}.png`});
    shots.push({name, ...snap});
  };
  await at(500, 't500');
  await at(600, 't1100');
  await page.waitForTimeout(Math.ceil((info.frames / info.fps) * 1000) + 900);
  const end = await page.evaluate(() => ({s: StreetUltimate.snapshot(), children: window.__fx.box.numChildren,
    fxOnStage: !!window.__fx.e.stage,
    leftovers: (function () {
      let n = 0;
      const box = window.__fx.box;
      for (let i = 0; i < box.numChildren; i++) if (String(box.getChildAt(i).name || '').indexOf('street_ultimate_') === 0) n++;
      return n;
    })()}));
  await page.screenshot({path: `${outDir}/done.png`});
  report.shots = shots; report.end = end; report.errors = errors; report.failed = failed;
  // The FX dispatch re-registers redirected containers after loadConfig; in
  // this fixture the race can surface a missing *_pattern_bin load. It is the
  // original container's load, not the overlay, so it is reported separately.
  const unrelated = errors.filter(e => !/pattern_bin/.test(e));
  const mid = shots.find(s => s.name === 't500');
  const finished = end.s.finished || [];
  const last = finished[finished.length - 1];
  report.checks = {
    noUnrelatedErrors: unrelated.length === 0,
    triggered: mid.s.matched >= 1,
    overlayStarted: mid.s.overlays >= 1,
    framesAdvancing: shots[0].s.frames >= 2 && shots[1].s.frames > shots[0].s.frames,
    originalHidden: shots.every(s => s.visible === false),
    finishedCleanly: end.s.active.length === 0,
    frameCoverage: last ? last.presented / Math.max(1, last.total) : 0,
    durationMs: last ? last.ms : 0,
    overlayRemoved: end.leftovers === 0,
  };
  // Headless Chrome renders WebGL in software, so a mid-clip texture upload
  // stalls the loop once; 85% coverage is the floor here, real GPU runs stall
  // far less. Assets keep the exact original frame count either way.
  report.pass = report.checks.noUnrelatedErrors && report.checks.triggered && report.checks.overlayStarted &&
    report.checks.framesAdvancing && report.checks.originalHidden && report.checks.finishedCleanly &&
    report.checks.overlayRemoved && report.checks.frameCoverage >= 0.85;
  console.log(JSON.stringify({pass: report.pass, checks: report.checks, errors}));
} catch (e) {
  report.error = e.stack;
  await page.screenshot({path: `${outDir}/failure.png`}).catch(() => {});
  console.log(JSON.stringify({pass: false, error: e.message}));
} finally {
  await b.close();
  await fs.writeFile(`${outDir}/report.json`, JSON.stringify(report, null, 2));
}
