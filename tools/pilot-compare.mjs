/* Original vs motif-container comparison for one key (frame-stepped, normal resolution). */
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const KEY = process.argv[2];
const LABEL = process.argv[3] || KEY;
const frameArg = process.argv[4] || '6';
const exactFrames = frameArg.includes(',') ? frameArg.split(',').map(Number) : null;
const FRAMES = exactFrames ? exactFrames.length : Number(frameArg);
const OUT = `outputs/street-reskin/pilot/compare/${KEY}`;
await fs.mkdir(OUT, {recursive: true});

async function capture(variant) {
  const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--enable-webgl', '--ignore-gpu-blocklist']});
  const page = await browser.newPage({viewport: {width: 900, height: 900}});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  if (variant === 'original') {
    await page.route('**/street-fx-table.js*', async route => {
      const text = await fs.readFile('local_game/street-fx-table.js', 'utf8');
      await route.fulfill({contentType: 'text/javascript', body: text.replace(/window\.StreetFXRedirect\s*=\s*\{[^\n]*?\};/, 'window.StreetFXRedirect = {};')});
    });
  }
  await page.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=heroes&pilot=' + variant, {waitUntil: 'domcontentloaded'});
  await page.waitForFunction(() => window.egret?.MainContext?.instance?.stage && window.Utils?.MsgUtils?.getSimpleEffect, null, {timeout: 60000});
  await page.waitForFunction(() => { try { return RES.hasRes('common_skill_zhaoyun_01_bin'); } catch (e) { return false; } }, null, {timeout: 60000});
  await page.waitForTimeout(1200);
  const info = await page.evaluate(async ({key, variant}) => {
    if (variant === 'motif') {
      RES.config.addResourceData({name: 'pilot_' + key + '_bin', url: '/assets/street/fx/pilot/' + key + '_motif.bin', type: 'bin', root: ''});
      window.StreetFXRedirect[key + '_bin'] = 'pilot_' + key + '_bin';
    }
    const stage = egret.MainContext.instance.stage;
    for (let i = 0; i < stage.numChildren; i++) stage.getChildAt(i).visible = false;
    const box = new egret.DisplayObjectContainer();
    const bg = new egret.Shape(); bg.graphics.beginFill(0x10141a); bg.graphics.drawRect(0, 0, 900, 900); bg.graphics.endFill();
    box.addChild(bg); stage.addChild(box);
    const e = Utils.MsgUtils.getSimpleEffect(key, box);
    e.x = 450; e.y = 450; e.scaleX = e.scaleY = 0.75;
    window.__p = {e, box};
    e.playEffect(1, () => {}, true);
    const t0 = Date.now();
    while (!(e._armature && e.width > 0) && Date.now() - t0 < 6000) await new Promise(r => setTimeout(r, 30));
    const state = e._armature && e._armature.animation.lastAnimationState;
    return {loaded: !!(e._armature && e.width > 0), total: state ? state.totalTime : 0, fps: (e._armature?.armature?.armatureData?.frameRate) || 24, action: e._action};
  }, {key: KEY, variant});
  if (!info.loaded) throw new Error('effect did not load');
  const totalFrames = Math.max(1, Math.round(info.total * info.fps));
  for (let i = 0; i < FRAMES; i++) {
    const frame = exactFrames
      ? Math.min(totalFrames - 1, exactFrames[i])
      : Math.min(totalFrames - 1, Math.round((i + 1) / (FRAMES + 1) * totalFrames));
    const b64 = await page.evaluate(({frame, action}) => {
      const e = window.__p.e;
      e._armature.animation.gotoAndPlayByFrame(action, frame, 1);
      e._armature.armature.advanceTime(1e-7);
      e._armature.animation.stop(action);
      const rt = new egret.RenderTexture();
      rt.drawToTexture(egret.MainContext.instance.stage, new egret.Rectangle(0, 0, 900, 900), 1);
      const data = rt.toDataURL('image/png').split(',')[1]; rt.dispose(); return data;
    }, {frame, action: info.action});
    await fs.writeFile(`${OUT}/${variant}-${i}.png`, Buffer.from(b64, 'base64'));
  }
  console.log(JSON.stringify({variant, info, errors: errors.slice(0, 3)}));
  await browser.close();
}

await capture('original');
await capture('motif');
