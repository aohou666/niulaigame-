/* H018 (肘击牛) shared-effect dispatch trial on the isolated 8794 save.
 * Proves: (1) new containers load under the new key, (2) hero 18 gets the new art,
 * (3) the original shared key is untouched for other casters, (4) main save unaffected.
 */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const BASE = 'http://127.0.0.1:8794';
const BASELINE = process.argv.includes('--baseline');   // empty dispatch table -> original shared effect
const SAVE = 'outputs/street-reskin/stress/8794-save.json';
const MAIN = 'pc_server_data/offline-replica-save.json';
const OUT = BASELINE ? 'art-migration/generation/street-fx-h018-baseline'
                     : 'art-migration/generation/street-fx-h018-atk-v01-l01-s01-trial';
const NEW_KEY = 'street_fx_h018_atk_v01_l01_s01';
const sha = b => crypto.createHash('sha256').update(b).digest('hex');

// Page errors that also occur with the ORIGINAL shared effect (proven by the --baseline run),
// so they are engine/offline-shell noise, not something this change introduced.
const KNOWN_ERRORS = ['getFile', 'playerInfo'];

await fs.mkdir(OUT, {recursive: true});
const backup = await fs.readFile(SAVE);
const mainBefore = sha(await fs.readFile(MAIN));
const save = JSON.parse(backup.toString('utf8'));
const hero = save.heroes.find(h => h.code === 41010018);
assert(hero, 'hero 18 missing from isolated save');
save.formation = [{uuid: hero.uuid, pos: 1}];
save.progress.stage = 1;
save.progress.battles = 0;
save.progress.wins = 0;
save.battleConfig = {scenario: 'wei', difficulty: 'normal', enemyCount: 1, enemySubTypes: [1], enemyRaces: [1]};
save.battleEntities = [];
delete save.pendingBattle;

const report = {pass: false, jobId: 'H018-ATK-V01-L01-S01', newKey: NEW_KEY,
                scope: 'Real offline BattleAI battle on isolated 8794; hero 18 attacks; new shared-effect override only for hero 18.'};
let page;
try {
  await fs.writeFile(SAVE, JSON.stringify(save, null, 2));
  const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
  page = await browser.newPage({viewport: {width: 720, height: 1100}});
  const errors = [], failures = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) failures.push({status: r.status(), url: r.url()}); });
  page.on('requestfailed', r => failures.push({url: r.url(), failure: r.failure()}));

  await page.addInitScript(([newKey, baseline]) => {
    if (baseline) window.StreetFXDispatchTable = {};   // A/B: let the original shared effect play
    window.__h018 = {effects: [], samples: [], png: null, calls: [], dispatch: null, matrix: null};
    // Instrument every plausible battle effect entry point so we can see which one is real.
    const hookMethods = () => {
      const FT = window.game?.FightTools;
      if (!FT || !FT.prototype) return false;
      ['handleOnPia', 'handleFlyEff', 'handleTargetEffect', 'playOnceEffect', 'getSimpleEffect'].forEach((name) => {
        const fn = FT.prototype[name];
        if (typeof fn !== 'function' || fn.__h018Hooked) return;
        const wrapped = function () {
          const srcs = [];
          const cfg = arguments[2];
          const first = arguments[0];
          if (typeof first === 'string') srcs.push(first);
          if (cfg && Array.isArray(cfg.effectsPiaEnemy)) cfg.effectsPiaEnemy.forEach(r => r?.src?.[0] && srcs.push(r.src[0]));
          if (cfg && Array.isArray(cfg.effectsPiaUs)) cfg.effectsPiaUs.forEach(r => r?.src?.[0] && srcs.push(r.src[0]));
          if (srcs.some(s => /zhaoyun_01|street_fx_h018/.test(String(s)))) {
            window.__h018.calls.push({method: name, srcs});
          }
          return fn.apply(this, arguments);
        };
        wrapped.__h018Hooked = true;
        FT.prototype[name] = wrapped;
      });
      return true;
    };
    const timer = setInterval(() => {
      if (!window.DBPlayer) return;
      if (!hookMethods()) return;
      clearInterval(timer);
      const init = DBPlayer.prototype.init;
      DBPlayer.prototype.init = function (dbName, armatureName) {
        const result = init.apply(this, arguments);
        const db = String(dbName), arm = String(armatureName || '');
        if (/zhaoyun_01|street_fx_h018/.test(db)) {
          window.__h018.effects.push({db, arm, at: performance.now()});
          if (!this.__h018Tick) {
            this.__h018Tick = () => {
              const armature = this._armature;
              if (!this.stage || !this.visible || !armature?.visible) return;
              if (window.__h018.samples.length >= 400) return;
              const state = armature.animation.lastAnimationState;
              const slots = armature.armature.getSlots().filter(s => s.displayIndex >= 0 && s.visible);
              const row = {db, action: state?.name, frame: Math.floor((state?.currentTime || 0) * 24 + 0.0001),
                          textures: slots.map(s => s._textureData?.name).filter(Boolean),
                          slotCount: slots.length,
                          slotDebug: slots.map(s => ({n: s.name, i: s.displayIndex, v: s.visible,
                                                     tex: !!s._textureData, dv: s.display?.visible})),
                          render: {
                            x: Math.round(this.x), y: Math.round(this.y),
                            sx: Number(this.scaleX.toFixed(3)), sy: Number(this.scaleY.toFixed(3)),
                            alpha: this.alpha, visible: this.visible,
                            armVisible: armature.visible, armAlpha: armature.alpha,
                            ax: Math.round(armature.x), ay: Math.round(armature.y),
                            batching: !!armature._batchEnabled,
                            drawData: armature.$renderNode?.drawData?.length ?? null,
                            slotDisplay: slots.length ? (slots[0].display && slots[0].display.constructor && slots[0].display.constructor.name) || null : null,
                            slotTex: slots.length && slots[0].display && slots[0].display.texture ? slots[0].display.texture.name : null,
                            bounds: (() => { try { const b = armature.getBounds(new egret.Rectangle()); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; } catch (e) { return null; } })()
                          }};
              window.__h018.samples.push(row);
              if (row.frame >= 3 && !window.__h018.png) {
                const stage = egret.MainContext.instance.stage;
                const tex = new egret.RenderTexture();
                tex.drawToTexture(stage, new egret.Rectangle(0, 0, stage.stageWidth, stage.stageHeight), 1);
                window.__h018.png = tex.toDataURL('image/png').split(',')[1];
                tex.dispose();
              }
            };
            this.addEventListener(egret.Event.ENTER_FRAME, this.__h018Tick, this);
          }
        }
        return result;
      };
    }, 10);
  }, [NEW_KEY, BASELINE]);

  await page.goto(`${BASE}/index_bh_lite3zbtest_andr.html?mode=demo`, {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.OfflineLastBattlePayload, null, {timeout: 90000});

  report.dispatch = await page.evaluate(() => window.StreetFXDispatch?.snapshot() ?? null);

  // Matrix proof: the same shared config must stay untouched for every other hero.
  report.matrix = await page.evaluate((newKey) => {
    const cfg = {effectsPiaEnemy: [{posType: 0, src: ['common_skill_zhaoyun_01']}], effectsPiaUs: []};
    const fake = {heroId: 18};
    const probe = window.StreetFXDispatch?.probe;
    if (!probe) return {supported: false};
    const forHero18 = probe(cfg, 18);
    const forHero9 = probe(cfg, 9);
    const untouched = cfg.effectsPiaEnemy[0].src[0];
    return {
      supported: true,
      hero18src: forHero18.effectsPiaEnemy[0].src[0],
      hero9src: forHero9.effectsPiaEnemy[0].src[0],
      originalMutated: untouched !== 'common_skill_zhaoyun_01',
      sameCfgObjectHero9: forHero9 === cfg,
      expected: newKey
    };
  }, NEW_KEY);

  await page.waitForFunction(() => window.__h018.samples.length > 0, null, {timeout: 45000}).catch(() => {});
  // Capture the effect across its whole life: one screenshot per ~70ms while it is on stage.
  const shots = [];
  const deadline = Date.now() + 40000;
  let lastFrame = -1;
  while (Date.now() < deadline && shots.length < 10) {
    const state = await page.evaluate(() => {
      const rows = window.__h018.samples;
      const last = rows[rows.length - 1];
      return last ? {frame: last.frame, count: rows.length} : null;
    });
    if (!state) { await page.waitForTimeout(50); continue; }
    if (state.frame !== lastFrame) {
      lastFrame = state.frame;
      const file = `${OUT}/shot-${String(shots.length).padStart(2, '0')}.png`;
      await page.screenshot({path: file});
      shots.push({frame: state.frame, file});
    }
    if (state.count > 18 && shots.length >= 6) break;
    await page.waitForTimeout(40);
  }
  report.shots = shots;
  await page.waitForTimeout(2500);
  report.dispatch = await page.evaluate(() => window.StreetFXDispatch?.snapshot() ?? null);
  report.effects = await page.evaluate(() => window.__h018.effects);
  report.calls = await page.evaluate(() => window.__h018.calls);
  report.samples = await page.evaluate(() => window.__h018.samples.slice(0, 12));
  report.sampleCount = await page.evaluate(() => window.__h018.samples.length);
  const png = await page.evaluate(() => window.__h018.png);
  if (png) await fs.writeFile(`${OUT}/battle-effect.png`, Buffer.from(png, 'base64'));
  await page.screenshot({path: `${OUT}/battle-screen.png`});

  report.payload = await page.evaluate(() => ({
    engine: OfflineLastBattlePayload.offlineCombatEngine,
    allies: OfflineLastBattlePayload.teams[0].entities.map(e => ({code: e.code, skillIds: e.skillIds})),
    rounds: OfflineLastBattlePayload.battleInfo.rounds.length,
    attacks: OfflineLastBattlePayload.battleInfo.rounds.flatMap(r => (r.seqAttack || []).map(a => ({entityId: a.entityId, skillId: a.skillId})))
  }));

  report.errors = errors; report.failures = failures;

  const newKeyUsed = report.effects.some(e => e.db.startsWith('street_fx_h018'));
  const armatureKept = report.effects.filter(e => e.db.startsWith('street_fx_h018')).every(e => e.arm === NEW_KEY);
  report.assertions = {
    dispatchInstalled: !!report.dispatch?.installed,
    resourcesRegistered: (report.dispatch?.resources || []).every(r => r.present),
    newKeyLoaded: newKeyUsed,
    armatureIsBaseKey: armatureKept,
    framesObserved: report.sampleCount > 0,
    matrixIsolated: report.matrix?.supported && report.matrix.hero18src === NEW_KEY &&
                    report.matrix.hero9src === 'common_skill_zhaoyun_01' && !report.matrix.originalMutated,
    battlePlayedEffects: (report.payload?.engine?.effects || 0) > 0,
    noNewPageErrors: errors.filter(e => !KNOWN_ERRORS.some(k => e.includes(k))).length === 0,
    noFailedRequests: failures.length === 0
  };
  report.pass = Object.values(report.assertions).every(Boolean);
  await fs.writeFile(`${OUT}/trial-runtime.json`, JSON.stringify(report, null, 2));
  console.log(JSON.stringify({pass: report.pass, assertions: report.assertions,
    effects: report.effects.slice(0, 6), samples: report.sampleCount,
    dispatch: {installed: report.dispatch?.installed, resources: report.dispatch?.resources,
               calls: report.dispatch?.calls, overridden: report.dispatch?.overridden,
               caster: report.dispatch?.casterProbe, debug: report.dispatch?.debug?.slice(0, 4)},
    matrix: report.matrix}, null, 1));
  await browser.close();
  if (!report.pass) process.exitCode = 1;
} catch (e) {
  report.error = e.stack;
  await fs.writeFile(`${OUT}/trial-runtime.json`, JSON.stringify(report, null, 2));
  if (page) await page.screenshot({path: `${OUT}/battle-failure.png`}).catch(() => {});
  console.error(e.stack);
  process.exitCode = 1;
} finally {
  await fs.writeFile(SAVE, backup);               // isolated save restored
  const mainAfter = sha(await fs.readFile(MAIN));
  console.log(JSON.stringify({isolatedSaveRestored: sha(await fs.readFile(SAVE)) === sha(backup),
                             mainSaveUnchanged: mainBefore === mainAfter}));
}
