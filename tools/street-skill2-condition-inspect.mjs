import fs from 'node:fs/promises';import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('C:/Users/dongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const browser=await chromium.launch({channel:'chrome',headless:true});
try{const p=await browser.newPage();await p.goto('http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes');await p.waitForFunction(()=>window.StreetBody?.snapshot().installed&&game.GameMVC.heroPy?.heroBag);
const report=await p.evaluate(()=>{const hero=config.HeroLO.Get(41010002),rows={},skinTables={};for(const id of [hero.normalSkill,hero.actSkill,hero.posSkill1,hero.posSkill2,hero.posSkill3])if(id)rows[id]=config.SkillBaseLO.Get(Number(id));for(const [key,value] of Object.entries(game.Config.pack))if(/derma/i.test(key)){skinTables[key]=Object.values(value||{}).filter(row=>JSON.stringify(row).includes('100201'));}return {hero,skills:rows,skinTables};});
await fs.writeFile('art-migration/skin-migration/100201/skill-condition-inspection.json',JSON.stringify(report,null,2));console.log(JSON.stringify({hero:{normalSkill:report.hero.normalSkill,actSkill:report.hero.actSkill,initEnergy:report.hero.initEnergy,maxEnergy:report.hero.maxEnergy},skinTables:report.skinTables}));
}finally{await browser.close();}
