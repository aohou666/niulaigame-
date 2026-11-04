import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const [key,url,outDir,maxFramesArg]=process.argv.slice(2); const maxFrames=Number(maxFramesArg||0);
await fs.mkdir(outDir,{recursive:true});
const b=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:900,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8794/index_bh_lite3zbtest_andr.html?mode=heroes',{waitUntil:'domcontentloaded'});
await p.waitForFunction(()=>window.egret?.MainContext?.instance?.stage && window.Utils?.MsgUtils?.getSimpleEffect,null,{timeout:60000});
await p.waitForFunction(()=>{try{return RES.hasRes('common_skill_zhaoyun_01_bin')}catch(e){return false}},null,{timeout:60000});
const info=await p.evaluate(async ({key,url})=>{
  if(url!=='ORIG'){
    RES.config.addResourceData({name:'pilot_'+key+'_bin',url,type:'bin',root:''});
    window.StreetFXRedirect[key+'_bin']='pilot_'+key+'_bin';
  }
  const stage=egret.MainContext.instance.stage;for(let i=0;i<stage.numChildren;i++)stage.getChildAt(i).visible=false;
  const box=new egret.DisplayObjectContainer();const bg=new egret.Shape();bg.graphics.beginFill(0x10141a);bg.graphics.drawRect(-1200,-1200,2400,2400);bg.graphics.endFill();box.addChild(bg);box.x=stage.stageWidth/2;box.y=stage.stageHeight/2;stage.addChild(box);
  const e=Utils.MsgUtils.getSimpleEffect(key,box);e.x=0;e.y=0;e.scaleX=e.scaleY=0.75;window.__e=e;
  e.playEffect(1,()=>{},true);const t0=Date.now();while(!(e._armature&&e.width>0)&&Date.now()-t0<6000)await new Promise(r=>setTimeout(r,30));
  const st=e._armature?.animation?.lastAnimationState;return {loaded:!!e._armature,total:st?st.totalTime:0,fps:(e._armature?.armature?.armatureData?.frameRate)||24,action:e._action};
},{key,url});
const total=Math.max(1,Math.round(info.total*info.fps)); const n=maxFrames?Math.min(maxFrames,total):total;
for(let f=0;f<n;f++){
  const b64=await p.evaluate(({f,action})=>{const e=window.__e;e._armature.animation.gotoAndPlayByFrame(action,f,1);e._armature.armature.advanceTime(1e-7);e._armature.animation.stop(action);const rt=new egret.RenderTexture();rt.drawToTexture(egret.MainContext.instance.stage,new egret.Rectangle(0,0,900,900),1);const d=rt.toDataURL('image/png').split(',')[1];rt.dispose();return d;},{f,action:info.action});
  await fs.writeFile(`${outDir}/f${String(f).padStart(2,'0')}.png`,Buffer.from(b64,'base64'));
}
console.log(JSON.stringify({key,total,n,info,errs:errs.slice(0,2)}));await b.close();
