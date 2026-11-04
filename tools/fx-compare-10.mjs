/* Capture 10 characters' effects in ORIGINAL and RESKIN variants at the same animation frames.
 * Original variant = street-fx-table.js served with an empty StreetFXRedirect map.
 * Reskin variant  = production table (pattern normal / single-key recolour containers).
 */
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ENTRIES = [
  {hero: '懂子', key: 'common_skill_caocao_02_1'},
  {hero: '马宝果', key: 'common_skill_guanyu_1_01'},
  {hero: '鸡', key: 'common_skill_pangtong_01_1'},
  {hero: '锤王', key: 'common_skill_pangde_02'},
  {hero: '丧尸牛', key: 'common_skill_zhangbao_02'},
  {hero: '蓝色妖姬', key: 'common_skill_xiahouyuan_01_1'},
  {hero: '机器牛', key: 'common_skill_huangyueying_01'},
  {hero: '驱鬼道长', key: 'common_skill_zhangjiao_baguazhen'},
  {hero: '金龙', key: 'common_shenzhaoyun_2_1'},
  {hero: '虎', key: 'common_skill_zhangliao_1_03'}
];
const FRAMES = Number(process.argv[2] || 10);
const ONLY = process.argv[3] ? process.argv[3].split(',') : null;
const OUT = 'art-migration/generation/fx-compare-20261103';
const STAGE = 720;
const entries = ONLY ? ENTRIES.filter(e => ONLY.includes(e.hero)) : ENTRIES;
await fs.mkdir(OUT, {recursive: true});

async function run(variant) {
  const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
  const context = await browser.newContext({viewport: {width: 900, height: 900}});
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  if (variant === 'original') {
    await page.route('**/street-fx-table.js*', async route => {
      const text = await fs.readFile('local_game/street-fx-table.js', 'utf8');
      const body = text.replace(/window\.StreetFXRedirect\s*=\s*\{[^\n]*?\};/, 'window.StreetFXRedirect = {};');
      await route.fulfill({contentType: 'text/javascript', body});
    });
  }
  await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=heroes&cmp=' + variant,
    {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.egret?.MainContext?.instance?.stage && window.Utils?.MsgUtils?.getSimpleEffect, null, {timeout: 60000});
  await page.waitForFunction(() => { try { return RES.hasRes('common_skill_zhaoyun_01_bin'); } catch (e) { return false; } }, null, {timeout: 60000});
  await page.waitForTimeout(1500);
  await page.evaluate(() => {
    const stage = egret.MainContext.instance.stage;
    for (let i = 0; i < stage.numChildren; i++) stage.getChildAt(i).visible = false;
    const box = new egret.DisplayObjectContainer();
    const bg = new egret.Shape();
    bg.graphics.beginFill(0x10141a); bg.graphics.drawRect(0, 0, 720, 720); bg.graphics.endFill();
    box.addChild(bg);
    stage.addChild(box);
    window.__cmp = {box};
  });
  const meta = [];
  for (const entry of entries) {
    const info = await page.evaluate(async ({key, stage}) => {
      const box = window.__cmp.box;
      box.removeChildren();
      const bg = new egret.Shape();
      bg.graphics.beginFill(0x10141a); bg.graphics.drawRect(0, 0, stage, stage); bg.graphics.endFill();
      box.addChild(bg);
      const e = Utils.MsgUtils.getSimpleEffect(key, box);
      e.x = stage / 2; e.y = stage / 2; e.scaleX = e.scaleY = 0.75;
      window.__cmp.e = e;
      e.playEffect(1, () => {}, true);
      const t0 = Date.now();
      while (!(e._armature && e.width > 0) && Date.now() - t0 < 6000) await new Promise(r => setTimeout(r, 30));
      const state = e._armature && e._armature.animation.lastAnimationState;
      const fps = (e._armature?.armature?.armatureData?.frameRate) || 24;
      return {loaded: !!(e._armature && e.width > 0), total: state ? state.totalTime : 0, action: e._action, fps};
    }, {key: entry.key, stage: STAGE});
    meta.push({...entry, ...info});
    if (!info.loaded) { console.log('NOT LOADED', entry.key); continue; }
    const totalFrames = Math.max(1, Math.round((info.total || 1) * info.fps));
    for (let i = 0; i < FRAMES; i++) {
      const frame = Math.min(totalFrames - 1, Math.round((i + 1) / (FRAMES + 1) * totalFrames));
      const b64 = await page.evaluate(({stage, action, frame}) => {
        const e = window.__cmp.e;
        e._armature.animation.gotoAndPlayByFrame(action, frame, 1);
        e._armature.armature.advanceTime(1e-7);
        e._armature.animation.stop(action);
        const rt = new egret.RenderTexture();
        rt.drawToTexture(egret.MainContext.instance.stage, new egret.Rectangle(0, 0, stage, stage), 1);
        const data = rt.toDataURL('image/png').split(',')[1];
        rt.dispose();
        return data;
      }, {stage: STAGE, action: info.action, frame});
      await fs.writeFile(`${OUT}/${variant}-${entry.key}-f${i}.png`, Buffer.from(b64, 'base64'));
    }
    await page.evaluate(() => { const e = window.__cmp.e; if (e) { e.stop(); if (e.parent) e.parent.removeChild(e); } });
  }
  console.log(JSON.stringify({variant, meta, errors: errors.slice(0, 5)}, null, 1));
  await browser.close();
}

await run('original');
await run('reskin');
