import fs from 'node:fs/promises';
const out='C:/Users/admin/Documents/ChatGPT/安装/outputs/reskin-v020';
const targets=await (await fetch('http://127.0.0.1:9222/json')).json();
const target=targets.find(t=>t.type==='page' && t.url.includes('127.0.0.1'));
if(!target)throw Error('未找到游戏WebView');
const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let counter=0;const pending=new Map();
ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id&&pending.has(msg.id)){const p=pending.get(msg.id);pending.delete(msg.id);msg.error?p.reject(msg.error):p.resolve(msg.result);}};
function cmd(method,params={}){return new Promise((resolve,reject)=>{const id=++counter;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
await cmd('Runtime.enable');await cmd('Page.enable');
const expression=process.argv[2]?.startsWith('@')?await fs.readFile(process.argv[2].slice(1),'utf8'):process.argv[2]||'JSON.stringify({audit:window.CharacterReskinAudit,url:location.href,text:document.body.innerText.slice(0,1000),width:innerWidth,height:innerHeight})';
const result=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
console.log(JSON.stringify(result));
if(process.argv[3]){
 const shot=await cmd('Page.captureScreenshot',{format:'png'});
 await fs.writeFile(`${out}/${process.argv[3]}.png`,Buffer.from(shot.data,'base64'));
}
ws.close();
