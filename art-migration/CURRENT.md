# 游戏换皮接续：先读此页，历史按需查WORKLOG和版本报告

## 授权与事实
用户已授权自主继续，不重复询问；Oct29十小时窗口结束后，Oct30明确续作。85目标角色、125独立额外皮肤及全部UI/地图/建筑/文字/道具/VFX，2.5D半写实半卡通离谱街区风。可官方ImageGen/本地Qwen2.1/MiniMax H3；每实质版全台账+两套85复查，每3版推指定GitHub核完整SHA。不以关键姿势/共用人物图/原作回退冒充完整动作或独立皮肤，不承诺全设备零bug不卡。
完整角色0/85，完整独立皮肤0/125。连续攻技批准10目标：2、3、46、52、63、73、79、80、84、85；76动作映射、34隔离。2号独立跑动24源→原生10帧，受击仍缺，自主战斗跑动未证明。
当前装备85=83新base待机+20穿102002/77穿107701原作未换皮肤；基础85审计临时浏览器卸皮肤逐项恢复，不做装备交易。85通过不等于85完整换皮。

## 仓库与交付
cwd C:/Users/dongdong/Documents/ChatGPT/安装，分支codex/street-reskin-20261029。delivery=https://github.com/aohou666/oldniulai.git，保留origin。
远端main已核8155b279b6fe4b522b4f2e5e894c834fc4689e11（v92，90/91/92批次）；push-092.json记录一致。此前v89=d01b1193ca978489171b6094ef2803d4daa48af6；push-089.json和HEAD1915依赖核验存versions/0.89.0。v90本地586f01b214fbcaf83e0f25a26b9a2403a6f924f4，HEAD1917依赖通过。v91=2bf7f86ef32603e9cda01c4b4a41c87af7e14292。v92本次提交以git rev-parse为准，1920依赖与全台账通过。v92=8155b279b6fe4b522b4f2e5e894c834fc4689e11，HEAD1920依赖通过。下一推v95（93/94/95）。
无关dirty保留：Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复、大量旧collector job/qa等。禁止git add .或宽泛reset。生成PNG可能被忽略，批准的源图需精确git add -f；运行资源须Git index/HEAD检查。原resource包是独立Release依赖。

## 100201已接入与v91修复
独立4静态绑定、124源待机/7WebP（原生198@30=6.6秒）、官方21独立源受击逐一映射原生21@30=.7秒。StreetBodyData.skins精确hero_skin_002_01主骨架、普通/EZ；effect_*不得绑人物idle/body。来源generation/skin100201-shouji-official21-v1及strip0-v2/strip1/2-v3；原生42暂停映射/21实播/真实装备与原生BattleAI受击在v88及v91报告。攻技跑动身体仍原作未替换。
v89 effect1：官方10纹理、19原生帧（前9各2帧/末1），alpha0.4；v90 effect2：另外独立10纹理、19帧、alpha0.5。两容器各147区域累计20替换，其余127与骨架/图集压缩块不变；继承旧包十区域逐像素一致，原生循环及战斗证明SHA递归保留。不是完整容器换皮；MiniMax仅材质参考，拒收视频未接入。
v91 street-native-fx.js修复战斗idle/hurt栅格替身隐藏整个骨架连带隐藏新特效：只隐藏原生身体槽位，保留已批准原生子特效与原时钟/事件，按110px身体适配；state owner隔离idle/body，未映射攻技跑动、init/reset/destroy恢复槽位和原变换。只战斗路径；UI预览仍未叠加特效。普通/EZ六动作/21受击/实际BattleAI受击已见effect1/2各7纹理（非声称每次战斗都完整loop），主存档不变/隔离恢复。完整循环另有19帧实播。15秒双角色P95约16.8ms、0帧>100ms、销毁owner0；仅本机Chrome。

## v92第三组已接入，下一项是身体动作/UI特效与46肖像
第三组20独立官方纹理替换原生39@30=1.3秒（前19各2帧/末1）；来源generation/skin100201-effect3-official-slots-v2，native-packed-v1。普通/EZ39帧全部看过、两圈实播各20纹理、生产资源SHA、effect1/2保留复播通过。实际隔离BattleAI338样本含234待机/104普攻，合计全部20纹理，主存档不变/隔离恢复。
当前两容器累计各40区域（三组全部纹理）替换，其余107身体区域与原生骨架/图集压缩块不变；普通/EZ仅算同皮肤的两个版本，不能算两独立皮肤。v91战斗overlay自动保留三组已批准childFX；UI仍不显示FX。v92双85各85/1876动作/14特效/125属性/6副骨架/21受击通过，双角色15秒P95约16.8ms/0帧>100ms/销毁owner0；85肖像4页已看并存SHA。
完整角色0/85、完整皮肤0/125不变，人物gongji/jineng/paobu未换。下一可修UI详情/编队FX独立坐标适配及补人物动作。v93已用官方独立竖向持竿全身图修复46原生pictureDraw132x257人物过小，未裁掉鱼竿/线/饵/水桶；完整原生控件前后图已看，59个原始独立资源标complete（不是59完整角色）。
第三组官方v1近环相位跳变/重复拒收，qa=rejected并保留原图；v2按原生20格逐一重绘获准，不是把v1改标批准。MiniMax仍只材质参考。
构建新FX包须--base当前containers，继承旧区域逐像素与QA/证明SHA；不能从原包抹掉先前替换。native-test支持--effect/--version/--baseline/--candidate；第三组原生基线versions/0.91.0/packed-fx-original.json（未换原包，仅审计）。
其余MiniMax拒收：100201普攻v1/v2、技能v1、effect3-v1/v2/v3、受击v2/v3均停姿/额外道具/碎裂等，不得改称合格或运行任务。

## 运行守卫与未结问题
真实装备载荷曾dermaCode0，v88已修configureOriginalBattleEntity与applyLocalHangUpEntity，穿脱/挂机原生载荷证据。百分数Miss43被原生AI当43导致全MISS；offline-battle-attributes.js仅转换明确离线UI整数百分数的AI深拷贝43→.43，保留存档/显示/核心属性/未标原生敌方及幂等。不要扩大到所有来源。
100201详情脚底global[363,878]；未换100202=hero_087_03，原生bounds+20%裕量固定420×270，普通/EZ双9秒因子稳定，切换/销毁恢复。不要给未批准独立皮肤套base新图。
v87社区庭院地图bycc_img_ditu_png原生960×898已批准；纵向1098拉伸装饰拒收，CITY-MAP-087-VERTICAL-STRETCH open。历史DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL未全面关闭。
125属性真实AttrConfig、四卡135×82→159×96.58、正常→禁选→正常点击计数1→1→2。6副骨架无idle/body请求、复用/销毁0缓存。正常HeroDermaPanel原14资源失败修复不代表所有历史问题关闭。

## 环境与检查
Python .tools/python/python.exe，PYTHONUTF8=1；Node24/Playwright Chrome。主8787存档pc_server_data/offline-replica-save.json禁止测试修改；8794隔离outputs/street-reskin/stress/8794-save.json，finally恢复且核主SHA。不要并行两场修改同隔离存档的战斗测试。
Comfy http://127.0.0.1:8188；G:/comfylight/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI。最近实际queue空，无活动任务。generation-worker.json旧状态不可冒称正在生成。官方创作按imagegen技能；PIL只裁切/缩放/alpha/图集适配。
两套85：street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立目录；第二次加--base-heroes。equipped三JSON复制版本及outputs/street-reskin全局，base另存版本/base-heroes-runtime.json和base-browser-log。
全量：street-body-roster-test.mjs 2 3 46 52 63 73 79 80 84 85 --version=版本；effects-roster、skin-effect-cache、skin-attribute完整断言；按改动加skin-hit-native、native-fx-overlay、skin-hit-battle、independent-skin-fidelity。合格运行资产精确stage，再street_art_verify.py、street_runtime_tracking.py --report、street_review.py --version；提交后tracking --tree HEAD。读JSON真实结果，不只看PowerShell末行exit0。
保持上下文简短：先读此页，历史按需；不载入全dirty文件名/minified代码。不删失败审计制造完成，不把基础设施当全部美术完成。

补充v92实际受击覆盖：单敌3的hell10/normal10两场均致死，只有0..2帧，等第5帧超时；normal1无负伤害，触发检查失败。三份失败原报告保留。八种敌人真实BattleAI补测通过，80样本/10不同受击帧，effect1/2/3均实际可见，主存档不变/隔离恢复。不能把被战斗打断的10帧称为实际完整21帧；21帧完整循环另有原生播放器证明。详见v92/battle-coverage-limitations.json。

## 最新：v93已提交，v94最终回归中，v95弹丸/命中特效
HEAD v93=2a7b531fafa087301da4be96b6599b1e78d0cc4d，远端仍v92。下一推v95（93/94/95）。v93两套85/1876动作/14特效/125属性/6副骨架/1920依赖通过，46竖向持竿portrait-v093及native pictureDraw完整道具已验证，单文件资源complete58→59；其它avatar/halfPic/额外皮肤不冒称新绘。
v94工作区已发布100201独立gongji45+原shouji21（66总atlas帧），主骨架普通/EZ精确绑定。最终候选generation/skin100201-gongji-official45-v2，图集shouji-gongji-f1393faddd871997.webp，RGBA解码12430080字节，旧21受击tile逐像素不变。新45源独立无复用填时长，native45@30=1.5秒/zd18一次保持。
原v1末尾取核桃在实际BattleAI约native35切idle前未完成，优化v2重排收势/取核桃并新增7个独立呼吸/平衡帧，33已取回核桃，native38..44为新绘尾段。实际场景观察36不同帧0..35，zd18一次，33回收手持核桃snapshot已看；不把实际36称完整45。完整45另有普通/EZ实播各45、90暂停映射；shouji21/42映射也通过。没有修改AI/控制器/原生时间线。普通/EZ源45与native90接触图均已看，人工逐帧+时序遥测，未虚称观看视频。
最终证明在versions/0.94.0/recovery-v2/skin-body-native-runtime.json；实际战斗同目录skin-body-gongji-battle-natural-normal-recovery.json，主存档不变/隔离恢复。root0.94原native-v1及单次harness action闭包错误失败报告均保留，不覆写。最终数据.actions.gongji绑定battle证明SHA，verifier核actual atlas SHA/33恢复。新frame-map按计划frameSources显式选45源，排除原21/23/25/27/29/31/33，新增neutral8中选7；不是复制持帧。source folders strip0..5-v1、strip6-v2和gongji-recovery-neutral8-v1；raw多余格明确不用。
15秒双角色原生回调交替45普攻/21受击：各66不同帧、P95约16.8ms、0帧>100ms、共享1bitmap、销毁0body缓存通过（PC Chrome warm，仅此范围）。完整角色0/85、完整独立皮肤0/125不变，技能/跑动、UI FX、107原生身体纹理等仍未全换。
v94全量运行的handles：base85 exec86645已完成属于v93；当前v94 base85 exec32260已完成或待确认；v94 worn85 exec95660已完成，body/14FX/属性/6副骨架 exec49792已完成；legacy hit+overlay+fidelity exec80869正在/终态待poll。直接查reports/实际handle，不重复启动已通过测试。需要复制两套85JSON到版本/全局，stage合格source/atlas后review/tracking、提交v94，再做v95。
无活动官方imagegen（801已完成；825为Qwen核桃去白底alpha编辑，若当前handle仍活用wait确认）。Comfy Qwen v1成功但核桃壳过平滑拒收design-qa；Qwen v2成功深沟壳设计已看，原图generation/skin100201-qiu-qwen-v2/skin100201-qiu-qwen-v2_00001_.png，prompt efa367d9-f83f-4672-afe1-2b4ffb7264fb已terminal并collect。alpha官方编辑cell825需确认结果。v1 9e19685b...也terminal，不重启。
v95目标：真实发射仍旧红白球，init已定位common_newskill_simayi_02_qiu普通/EZ（各1region qiu，1@30静态），命中common_newskill_simayi_02普通/EZ（各13region，13@24）。原包inventory/atlas/skeleton在outputs/street-reskin/skin100201-projectile-audit-v95，普通128²/EZ64²的palette透明别误认绿背景，convert RGBA后alpha0是透明。将Qwen深纹核桃制合格alpha后逐纹理替换qiu；还需命中13帧新效果，拟本地MiniMax参照原native13节奏+铜白青材质。当前这些4原包未替换，不能把普攻全部美术算完成。
后续可研究107原生身体region逐部件重绘/重绑，保持原动画，减少每动作整帧重绘并覆盖残留材质；不能用重着色/空白/共用人物图冒充独立新皮肤。

### v94终态复核
v94双85/1876/14FX/125属性/6副骨架/1922依赖与全台账通过；4肖像页SHA同v93。v94即将/已经提交，实际SHA以git为准。v95 MiniMax prompt b59a3aa1-dce4-49ca-a827-dba7ea246169正在运行，queue/history为准，不重复提交。Qwen核桃透明源已在skin100201-qiu-hybrid-alpha-v1/official-alpha.png，官方去背景源SHA/provenance齐备；尚未替换弹丸包。
