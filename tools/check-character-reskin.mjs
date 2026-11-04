import fs from 'node:fs/promises';
import readline from 'node:readline';
import vm from 'node:vm';
const root='C:/Users/admin/Documents/ChatGPT/安装';
const tables={HeroLO:{},SkillBaseLO:{}};
const stream=(await fs.open(`${root}/outputs/game-config-summary/staging/records.ndjson`)).createReadStream();
for await(const line of readline.createInterface({input:stream,crlfDelay:Infinity})){
 if(!line)continue;const r=JSON.parse(line);if(!tables[r.tableName])continue;
 const row=JSON.parse(r.json);tables[r.tableName][row.code||row.id]=row;
}
const elements=[];
const sandbox={console,URLSearchParams,location:{search:''},setTimeout:()=>{},
 document:{documentElement:{style:{}},head:{appendChild(){}},body:{style:{},appendChild(e){elements.push(e);}},createElement(){return {style:{}};}},
 game:{Config:{pack:{t_hero:tables.HeroLO,t_skill_base:tables.SkillBaseLO}}},
 config:{HeroLO:{Get(id){return tables.HeroLO[id];}},SkillBaseLO:{Get(id){return tables.SkillBaseLO[id];}}},
 RES:{addResourceData(){}},Object,JSON};sandbox.window=sandbox;
vm.createContext(sandbox);
vm.runInContext(await fs.readFile(`${root}/local_game/character-reskin-data.js`,'utf8'),sandbox);
const beforeSkills=JSON.parse(JSON.stringify(tables.SkillBaseLO));
vm.runInContext(await fs.readFile(`${root}/local_game/character-reskin.js`,'utf8'),sandbox);
sandbox.CharacterReskin.apply();
const audit=sandbox.CharacterReskinAudit;if(!audit)throw Error('未完成展示补丁');
if(tables.HeroLO[41000040].name!=='掌契·包租牛')throw Error('未应用鲁肃替换');
if(tables.HeroLO[41000013].name!=='于禁')throw Error('缺口不应覆盖原角色');
if(tables.SkillBaseLO[550690210].name!==beforeSkills[550690210].name)throw Error('共用技能发生全局覆盖');
const scoped=sandbox.CharacterReskin.withHero(41000078,()=>sandbox.config.SkillBaseLO.Get(550690210));
if(scoped.name!=='夜羽直言')throw Error('共用技能没有按当前角色展示');
const descNumbers=s=>String(s||'').match(/\d+(?:\.\d+)?/g)||[];
for(const [id,row] of Object.entries(tables.SkillBaseLO)){
 if(JSON.stringify(descNumbers(row.desc))!==JSON.stringify(descNumbers(beforeSkills[id].desc)))throw Error('技能文案数值改变：'+id);
}
await fs.writeFile(`${root}/outputs/reskin-v020/config-check.json`,JSON.stringify({...audit,sharedSkillScopeVerified:true,skillDescriptionNumbersVerified:true,sourceHeroRows:Object.keys(tables.HeroLO).length,sourceSkillRows:Object.keys(tables.SkillBaseLO).length},null,2));
console.log('RESKIN_CONFIG_CHECK_OK');
