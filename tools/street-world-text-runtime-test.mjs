import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createRequire} from 'node:module';const require=createRequire(import.meta.url),{chromium}=require('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const version=process.argv.find(v=>v.startsWith('--version='))?.slice(10)||'0.30.0',profiles={},titles={};for(const file of await fs.readdir('art-migration/stories')){if(/^stories-.*\.json$/.test(file))for(const r of JSON.parse(await fs.readFile('art-migration/stories/'+file,'utf8')))profiles[r.id]=r;if(/^skills-.*\.json$/.test(file))Object.assign(titles,JSON.parse(await fs.readFile('art-migration/stories/'+file,'utf8')));}
await fs.mkdir('art-migration/versions/'+version,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:480,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes&heroaudit=1');await page.waitForFunction(()=>window.CharacterReskinAudit&&window.CharacterIdle?.snapshot().installed);
 const report=await page.evaluate(({profiles,titles})=>{
  const checks=[],slotIndex={'普通技能':0,'怒气技能':1,'被动技能1':2,'被动技能2':3,'被动技能3':4},fields=['normalSkill','actSkill','posSkill1','posSkill2','posSkill3'];let nativeRows=0,skillReferences=0;
  for(const id of Object.keys(profiles)){
   const h=CharacterReskinData.heroes[id],p=profiles[id],failures=[];if(!h.matched)failures.push('not matched');if(h.portrait!==CharacterArtData.heroes[id].portrait)failures.push('portrait mismatch');if(h.definition!==p.definition)failures.push('definition mismatch');
   for(const [skillId,s] of Object.entries(h.skills))if(s.name!==titles[id][slotIndex[s.slot]])failures.push('display title mismatch '+skillId);
   const rows=Object.values(game.Config.pack.t_hero).filter(r=>Number(r.subType)===Number(id));if(!rows.length)failures.push('no native rows');
   for(const row of rows){nativeRows++;const native=config.HeroLO.Get(row.code);if(native.definition!==p.definition||native.name!==h.name)failures.push('native identity mismatch '+row.code);
    for(let i=0;i<3;i++)if(native['storyTitle'+(i+1)]!==p.chapters[i][0]||native['storyDesc'+(i+1)]!==p.chapters[i][1])failures.push('native chapter mismatch '+row.code+'/'+i);
    for(const field of fields){const key=row[field];if(!key)continue;skillReferences++;const expected=h.skills[String(key)];if(!expected){failures.push('missing display '+field+'/'+key);continue;}const display=CharacterReskin.withHero(row.code,()=>config.SkillBaseLO.Get(key),null,[]);if(!display){failures.push('missing native skill '+field+'/'+key+' pack='+!!game.Config.pack.t_skill_base[key]);continue;}if(display.name!==expected.name||display.desc!==expected.desc)failures.push('native skill mismatch '+key);}
   }
   checks.push({id:Number(id),name:h.name,nativeRows:rows.length,skillDisplays:Object.keys(h.skills).length,pass:failures.length===0,failures});
  }
  return {checks,nativeRows,skillReferences,protectedAudit:CharacterReskinAudit,skillReferenceRepair:window.OfflineSkillReferences?.audit};
 },{profiles,titles});
 if(!report.checks.every(r=>r.pass))await fs.writeFile('art-migration/versions/'+version+'/world-text-failure.json',JSON.stringify({pass:false,errors,...report},null,2));
 assert.equal(report.checks.length,85);assert(report.checks.every(r=>r.pass),JSON.stringify(report.checks.filter(r=>!r.pass)));assert.deepEqual(report.protectedAudit.protectedHeroDifferences,[]);assert.deepEqual(report.protectedAudit.protectedSkillDifferences,[]);assert.equal(errors.length,0);assert.equal(report.skillReferenceRepair.skillDefinitionsChanged,false);assert.deepEqual(report.skillReferenceRepair.unresolved,[]);
 await page.getByLabel('核对角色').selectOption('82');await page.getByRole('button',{name:'打开详情',exact:true}).click();await page.waitForFunction(()=>window.CharacterReskin?.activeView()?.info?.config?.subType===82);await page.waitForTimeout(500);await page.screenshot({path:'outputs/street-reskin/world-text-native-82.png'});
 await page.getByRole('button',{name:'角色图鉴',exact:true}).click();await page.locator('.rc-card[data-hero="82"]').click();await page.screenshot({path:'outputs/street-reskin/world-text-catalogue-82.png'});const content=await page.locator('.rc-detail').innerText();assert(content.includes(profiles[82].definition));for(const [title,text] of profiles[82].chapters)assert(content.includes(title)&&content.includes(text));
 await fs.writeFile('art-migration/versions/'+version+'/world-text-runtime.json',JSON.stringify({pass:true,errors,stories:255,displayTitles:425,...report},null,2));console.log(JSON.stringify({pass:true,characters:report.checks.length,nativeRows:report.nativeRows,skillReferences:report.skillReferences}));
}finally{await browser.close();}
