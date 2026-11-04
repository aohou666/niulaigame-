/* Capture one in-battle frame per hero, to show the palette actually differs per character. */
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const HEROES = process.argv.slice(2).map(Number);
const SAVE = 'outputs/street-reskin/stress/8794-save.json';
const OUT = 'art-migration/generation/fx-batch-recolor-20261103/shots';
const backup = await fs.readFile(SAVE);
await fs.mkdir(OUT, {recursive: true});
const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
const shots = [];
try {
  for (const heroId of HEROES) {
    const save = JSON.parse(backup.toString('utf8'));
    const hero = save.heroes.find(h => h.code === 41010000 + heroId);
    save.formation = [{uuid: hero.uuid, pos: 1}];
    save.progress.stage = 1; save.progress.battles = 0; save.progress.wins = 0;
    save.battleConfig = {scenario: 'wei', difficulty: 'normal', enemyCount: 2, enemySubTypes: [1, 3], enemyRaces: [1, 2]};
    save.battleEntities = []; delete save.pendingBattle;
    await fs.writeFile(SAVE, JSON.stringify(save, null, 2));

    const page = await browser.newPage({viewport: {width: 720, height: 1100}});
    await page.addInitScript(() => {
      window.__shot = {hit: false, db: null};
      const t = setInterval(() => {
        if (!window.DBPlayer) return;
        clearInterval(t);
        const init = DBPlayer.prototype.init;
        DBPlayer.prototype.init = function (db) {
          const name = String(db);
          if ((name.indexOf('street_fx_') === 0 || name.indexOf('_streetfx') >= 0 || name.indexOf('_pattern') >= 0) && !window.__shot.hit) {
            window.__shot.hit = true; window.__shot.db = name;
            setTimeout(() => { window.__shot.ready = true; }, 260);
          }
          return init.apply(this, arguments);
        };
      }, 80);
    });
    await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=demo', {waitUntil: 'domcontentloaded'});
    await page.waitForFunction(() => window.OfflineLastBattlePayload, null, {timeout: 90000}).catch(() => {});
    await page.waitForFunction(() => window.__shot?.ready, null, {timeout: 45000}).catch(() => {});
    await page.waitForTimeout(150);
    const file = `${OUT}/hero${String(heroId).padStart(3, '0')}.png`;
    await page.screenshot({path: file});
    const db = await page.evaluate(() => window.__shot.db);
    shots.push({heroId, db, file});
    console.log(JSON.stringify({heroId, db, file}));
    await page.close();
  }
} finally {
  await browser.close().catch(() => {});
  await fs.writeFile(SAVE, backup);
  await fs.writeFile(`${OUT}/shots.json`, JSON.stringify(shots, null, 2));
}
