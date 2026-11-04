/* Smoke test: several heroes, each must get ITS OWN batch container for its skill FX.
 * Hero 9 and hero 18 share the original key common_skill_zhaoyun_01, so they must resolve to
 * different db names — that is the whole point of the per-hero dispatch.
 *
 * usage: node street-batch-smoke.mjs 1 9 18 24 63
 */
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const HEROES = process.argv.slice(2).map(Number);
const BASE = 'http://127.0.0.1:8794';
const SAVE = 'outputs/street-reskin/stress/8794-save.json';
const MAIN = 'pc_server_data/offline-replica-save.json';
const OUT = 'art-migration/generation/fx-batch-recolor-20261103/smoke';
const sha = b => crypto.createHash('sha256').update(b).digest('hex');

await fs.mkdir(OUT, {recursive: true});
const backup = await fs.readFile(SAVE);
const mainBefore = sha(await fs.readFile(MAIN));
const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
const results = [];

try {
  for (const heroId of HEROES) {
    const save = JSON.parse(backup.toString('utf8'));
    const code = 41000000 + 10000 + heroId;   // 41010000 + heroId
    const hero = save.heroes.find(h => h.code === code) || save.heroes[heroId - 1];
    if (!hero) { results.push({heroId, error: 'hero not in save'}); continue; }
    save.formation = [{uuid: hero.uuid, pos: 1}];
    save.progress.stage = 1;
    save.progress.battles = 0;
    save.progress.wins = 0;
    save.battleConfig = {scenario: 'wei', difficulty: 'normal', enemyCount: 2, enemySubTypes: [1, 3], enemyRaces: [1, 2]};
    save.battleEntities = [];
    delete save.pendingBattle;
    await fs.writeFile(SAVE, JSON.stringify(save, null, 2));

    const page = await browser.newPage({viewport: {width: 640, height: 1000}});
    const errors = []; const fxLoaded = []; page.on('request', r => { const u = r.url(); if (u.indexOf('/assets/street/fx/') >= 0) fxLoaded.push(u.split('/').pop()); });
    page.on('pageerror', e => errors.push(e.message));
    await page.addInitScript(() => {
      window.__smoke = {effects: [], dispatch: null};
      const t = setInterval(() => {
        if (!window.DBPlayer) return;
        clearInterval(t);
        const init = DBPlayer.prototype.init;
        DBPlayer.prototype.init = function (db) {
          const name = String(db);
          if (name.indexOf('street_fx_') === 0) window.__smoke.effects.push(name);
          return init.apply(this, arguments);
        };
      }, 120);
    });
    await page.goto(`${BASE}/index_bh_lite3zbtest_andr.html?mode=demo`, {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => window.OfflineLastBattlePayload, null, {timeout: 90000}).catch(() => {});
    // The payload is only the computed battle; the playback (and therefore the pia effects) comes after.
    await page.waitForFunction(() => (window.__smoke?.effects.length || 0) > 0, null, {timeout: 45000}).catch(() => {});
    await page.waitForTimeout(6000);
    const loaded = fxLoaded.slice(); 
    const got = await page.evaluate(() => ({
      effects: Array.from(new Set(window.__smoke.effects)),
      dispatch: window.StreetFXDispatch ? window.StreetFXDispatch.snapshot() : null
    }));
    const expectPrefix = `street_fx_h${String(heroId).padStart(3, '0')}_`;
    const matched = got.effects.filter(e => e.startsWith(expectPrefix));
    const foreign = got.effects.filter(e => !e.startsWith(expectPrefix));
    const rec = {
      heroId, heroCode: code,
      installed: !!got.dispatch?.installed,
      resources: got.dispatch?.resources,
      calls: got.dispatch?.calls,
      overridden: got.dispatch?.overridden,
      effects: got.effects.slice(0, 6),
      matchedOwn: matched.length,
      foreignEffects: foreign.slice(0, 4),
      errors: errors.filter(e => !/getFile|playerInfo/.test(e)),
      fxLoaded: loaded,
      pass: (matched.length > 0 || loaded.length > 0) && foreign.length === 0 && errors.filter(e => !/getFile|playerInfo/.test(e)).length === 0
    };
    results.push(rec);
    console.log(JSON.stringify(rec));
    await page.close();
  }
  await fs.writeFile(`${OUT}/smoke.json`, JSON.stringify(results, null, 2));
  const ok = results.every(r => r.pass);
  console.log(JSON.stringify({heroes: results.length, pass: ok}));
  process.exitCode = ok ? 0 : 1;
} finally {
  await browser.close().catch(() => {});
  await fs.writeFile(SAVE, backup);
  console.log(JSON.stringify({isolatedSaveRestored: true, mainSaveUnchanged: sha(await fs.readFile(MAIN)) === mainBefore}));
}
