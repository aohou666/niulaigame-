import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const production=process.argv.includes('--production');const out=production?'art-migration/versions/0.97.0/activity':'art-migration/generation/skin100201-native-activity-preview-v1';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});let report={pass:false,productionConfiguration:production};
try{
 const p=await browser.newPage();
 if(!production)await p.route('**/__activity-preview.png',r=>r.fulfill({path:out+'/common_activity_simayi_new01_tex.png',contentType:'image/png'}));
 await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.DBPlayer&&StreetBody.snapshot().installed&&CharacterIdle.snapshot().installed);
 const protocol=JSON.parse(await fs.readFile('art-migration/generation/skin100201-native-activity-preview-v1/common_activity_simayi_new01_mc.json','utf8'));
 report.runtime=await p.evaluate(async({protocol,production})=>{
  const texture=production?await RES.getResAsync('common_activity_simayi_new01_tex_png'):await Promise.race([new Promise(resolve=>RES.getResByUrl(location.origin+'/__activity-preview.png',resolve,null,'image')),new Promise((_,reject)=>setTimeout(()=>reject(Error('Candidate image load timeout')),10000))]);
  if(production){const loaded=await RES.getResAsync('common_activity_simayi_new01_mc_json');if(JSON.stringify(loaded)!==JSON.stringify(protocol))throw Error('Production native MC protocol differs');protocol=loaded;if(texture!==RES.getRes('street_skin100201_native_activity_tex_png'))throw Error('Production activity texture alias failed');}
  if(!texture)throw Error('No candidate texture');
  const factory=new egret.MovieClipDataFactory(protocol,texture),data=factory.generateMovieClipData('common_activity_simayi_new01'),clip=new egret.MovieClip(data);
  egret.MainContext.instance.stage.addChild(clip);clip.x=210;clip.y=240;
  let complete=0;const frames=new Set();clip.addEventListener(egret.Event.COMPLETE,()=>complete++,null);
  const began=performance.now();clip.gotoAndPlay(1,1);
  while(performance.now()-began<2500&&complete===0){frames.add(clip.currentFrame);await new Promise(r=>requestAnimationFrame(r));}
  frames.add(clip.currentFrame);
  const result={totalFrames:clip.totalFrames,frameRate:clip.frameRate,complete,observedFrames:[...frames],elapsedMs:performance.now()-began,lastFrame:clip.currentFrame};
  const image=new egret.RenderTexture();image.drawToTexture(clip,new egret.Rectangle(-102,-128,206,257),1);result.png=image.toDataURL('image/png').split(',')[1];image.dispose();clip.stop();clip.parent.removeChild(clip);return result;
 },{protocol,production});
 await fs.writeFile(out+'/movieclip-last.png',Buffer.from(report.runtime.png,'base64'));delete report.runtime.png;
 assert.equal(report.runtime.totalFrames,38);assert.equal(report.runtime.frameRate,24);assert.equal(report.runtime.complete,1);assert.equal(report.runtime.lastFrame,38);assert(report.runtime.observedFrames.length>=30);report.pass=true;
}finally{await browser.close();await fs.writeFile(out+'/movieclip-runtime.json',JSON.stringify(report,null,2));}
console.log(JSON.stringify(report));
