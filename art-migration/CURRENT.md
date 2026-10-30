# 游戏换皮接续：以本页为准，历史按需读WORKLOG及版本报告

## 范围与真实进度
用户已授权自主继续；Oct29十小时结束后Oct30明确续作，不重复询问。85目标角色、125独立额外皮肤及所有UI/地图/建筑/文字/道具/VFX，2.5D半写实半卡通离谱街区风，官方ImageGen/本地Qwen2.1/MiniMax H3。每实质版全台账+两套85；每3版推指定GitHub并核完整SHA。关键姿势、重复持帧、共用人物图、原作回退不能充完整独立皮肤；不承诺全设备零bug不卡。
完整角色0/85、完整独立皮肤0/125。单原始资源complete63（v96：61→63，两个共享命中包各13纹理；普通/EZ不是两皮肤）。连续攻技批准10目标2/3/46/52/63/73/79/80/84/85，76映射/34隔离；2号跑动24源→原生10帧，受击缺。当前装备85=83新base待机+20穿102002/77穿107701原作未换皮肤；base85临时浏览器卸装恢复。85检查通过不是全美术完成。

## Git交付/当前版本
cwd C:/Users/dongdong/Documents/ChatGPT/安装；codex/street-reskin-20261029；delivery=https://github.com/aohou666/oldniulai.git，保留origin。
v95 HEAD与远端main已核4eb1604c21b2e1a62d3289e21cefb272f77a3322（93/94/95批次），push-095.json/HEAD1924依赖报告在versions/0.95.0。v94=a141ea66；v93=2a7b531fafa087301da4be96b6599b1e78d0cc4d。v96工作区完成命中13纹理普通/EZ，双85/1876动作/14FX/125属性/6副骨架/FX叠加/100202保留已通过；1926依赖/verify通过，review待终态核对或已通过。准备记录肖像SHA、提交v96，下一推v98（96/97/98）。提交后tracking --tree HEAD。
无关dirty必须保留（Android、README/offline-launcher、disabled技能修复、旧collector job/QA等）；禁止git add .、宽泛reset。批准源PNG可能被忽略，精确git add -f，运行资源须index/HEAD核验。原resource包是独立Release依赖。

## 100201已接入/缺口
独立4静态、124源待机/7WebP原生198@30、21独立受击@30、45独立普攻@30，精确主骨架hero_skin_002_01普通/EZ，不绑副effect骨架。受击+普攻66格lossless图集shouji-gongji-f1393faddd871997.webp，旧21格逐像素保持，解码12430080字节。普攻保留zd18；v94原v1回收核桃过晚，v2原生33完成取回、38..44为新增7独立尾帧。v94实际36帧0..35，完整45普通/EZ实播/90暂停另证。source gongji-official45-v2及strip-0..5-v1/6-v2、recovery-neutral8-v1；失败/草稿不覆盖。PC Chrome warm双角色15秒各66帧、共享1bitmap、P95约16.8ms/0>100ms/销毁0；非手机全场景承诺。
三组原生子FX40纹理全部换（effect1/2各10→19@30，effect3 20→39@30）；两个主容器各147中40换，107原生身体region仍未换，骨架/图集字节保留。战斗overlay只隐藏旧身体槽位、保留新子FX，未映射动作恢复；UI详情/编队尚无FX。技能46@30/跑动16@30仍旧身体，完整皮肤不成立。
v95共用司马懿qiu普通/EZ各唯一纹理换深沟核桃：本地Qwen efa367d9...成功+官方透明编辑，source qiu-hybrid-alpha-v1/official-alpha.png；普通1/30秒/EZ0静态原钟不动。实际BattleAI EZ弹丸8可见采样，普通另原生播放器；两包SHA、主存档不变/隔离恢复。作用所有原共享消费者，非skin独占。
v96共用命中common_newskill_simayi_02普通/EZ各13纹理已换官方新核桃碎壳；13独立源，统一缩放normal1.14/EZ.57，原纹理逻辑中心/13@24及count,pia,pia每圈保持。普通/EZ全部26暂停图已看、两圈实播各13纹理/回调完成各1、SHA/slot/events原作对照通过。真实BattleAI EZ命中21采样、12不同纹理（frame3采样跳过），原生完整13另证；实际截图已看，主存档不变/隔离恢复。source impact-official13-v1、native-packed-v1；versions/0.96.0/impact-candidate/production及skin-body-gongji-battle-impact-visible.json。不要声称实际一场观察了全部13或普通+EZ都在场。

## 生成队列与下一步
Comfy http://127.0.0.1:8188；G:/comfylight/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI；generation-worker.json旧Oct29，不当作活任务。实际queue/history为准，不因超时重启。最新MiniMax impact-v1 prompt b59a3aa1...已成功collect124但虹彩/首帧突变拒收，全contact和effect-qa保留；没有生成任务在跑（继续时重查）。官方865已完成，13帧源已入项目。
研究后续原生107身体部件重绘/重绑覆盖，保留原连续动画，避免只覆盖几个整帧动作后残留大量旧部件。原107区域清单及3接触图在art-migration/skin-migration/100201/native-body-parts（未更换，非批准）。只有5原生动作：gongji45、jineng46、shouji21、daiji198、paobu16。必须逐部件真实新绘/语义对应，不能重着色/空白/共用人物图冒充；先证明原生连续外观及接缝可行再推广。不要把原生旧动作算新皮肤。

## 其他守卫/未结问题
v88 dermaCode DTO真实穿脱/挂机修复；offline-battle-attributes仅明确离线UI整数百分数AI深拷贝43→.43，不动存档/显示/核心属性/未标原敌方/幂等。100202原生hero_087_03保留，详情固定420×270+20%裕量，普通/EZ双9秒因子稳定，禁止套base新图。
v93 46竖向持竿pictureDraw132×257已修，完整人物/桶/鱼竿/线/饵，其他头像/额外皮肤未据此算新绘。v87庭院map960×898批准，1098拉伸拒收，CITY-MAP-087-VERTICAL-STRETCH open。DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL未全面关闭。v92受击实际八敌10不同帧，完整21另播放器；三个早停失败报告保留。

## 工具/检查
Python .tools/python/python.exe，PYTHONUTF8=1；Node24/Playwright Chrome路径见现有mjs。8787主存档pc_server_data/offline-replica-save.json测试禁止修改；8794隔离outputs/street-reskin/stress/8794-save.json，每场finally恢复+核主SHA，不并行两场写同隔离存档。
两套85：street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立目录；第二套加--base-heroes。equipped三JSON复制版本及outputs/street-reskin全局，base三份另存。body-roster目标2 3 46 52 63 73 79 80 84 85；effects-roster/skin-effect-cache/skin-attribute完整断言；改动再测FX overlay/独立皮肤保留/原生/实际BattleAI。stage精确资产后street_art_verify.py、street_runtime_tracking.py --report、street_review.py --version，检查JSON而非只看shell退出码。全85肖像4页每版看，未变可比已看版SHA。上下文只读此页和当前证据，历史WORKLOG/Git按需查；不删失败审计或聊天、不声称已压缩系统上下文。
