# 游戏换皮接续：先读此页，历史按需查WORKLOG和版本报告

## 授权与事实
用户已授权自主继续，不重复询问；Oct29十小时窗口结束后，Oct30明确续作。85目标角色、125独立额外皮肤及全部UI/地图/建筑/文字/道具/VFX，2.5D半写实半卡通离谱街区风。可官方ImageGen/本地Qwen2.1/MiniMax H3；每实质版全台账+两套85复查，每3版推指定GitHub核完整SHA。不以关键姿势/共用人物图/原作回退冒充完整动作或独立皮肤，不承诺全设备零bug不卡。
完整角色0/85，完整独立皮肤0/125。连续攻技批准10目标：2、3、46、52、63、73、79、80、84、85；76动作映射、34隔离。2号独立跑动24源→原生10帧，受击仍缺，自主战斗跑动未证明。
当前装备85=83新base待机+20穿102002/77穿107701原作未换皮肤；基础85审计临时浏览器卸皮肤逐项恢复，不做装备交易。85通过不等于85完整换皮。

## 仓库与交付
cwd C:/Users/dongdong/Documents/ChatGPT/安装，分支codex/street-reskin-20261029。delivery=https://github.com/aohou666/oldniulai.git，保留origin。
远端main已核d01b1193ca978489171b6094ef2803d4daa48af6（v89，87/88/89批次）；push-089.json和HEAD1915依赖核验存versions/0.89.0。v90本地586f01b214fbcaf83e0f25a26b9a2403a6f924f4，HEAD1917依赖通过。v91=2bf7f86ef32603e9cda01c4b4a41c87af7e14292。v92本次提交以git rev-parse为准，1920依赖与全台账通过。下一推v92，批次90/91/92，push delivery HEAD:main后ls-remote核完整SHA。
无关dirty保留：Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复、大量旧collector job/qa等。禁止git add .或宽泛reset。生成PNG可能被忽略，批准的源图需精确git add -f；运行资源须Git index/HEAD检查。原resource包是独立Release依赖。

## 100201已接入与v91修复
独立4静态绑定、124源待机/7WebP（原生198@30=6.6秒）、官方21独立源受击逐一映射原生21@30=.7秒。StreetBodyData.skins精确hero_skin_002_01主骨架、普通/EZ；effect_*不得绑人物idle/body。来源generation/skin100201-shouji-official21-v1及strip0-v2/strip1/2-v3；原生42暂停映射/21实播/真实装备与原生BattleAI受击在v88及v91报告。攻技跑动身体仍原作未替换。
v89 effect1：官方10纹理、19原生帧（前9各2帧/末1），alpha0.4；v90 effect2：另外独立10纹理、19帧、alpha0.5。两容器各147区域累计20替换，其余127与骨架/图集压缩块不变；继承旧包十区域逐像素一致，原生循环及战斗证明SHA递归保留。不是完整容器换皮；MiniMax仅材质参考，拒收视频未接入。
v91 street-native-fx.js修复战斗idle/hurt栅格替身隐藏整个骨架连带隐藏新特效：只隐藏原生身体槽位，保留已批准原生子特效与原时钟/事件，按110px身体适配；state owner隔离idle/body，未映射攻技跑动、init/reset/destroy恢复槽位和原变换。只战斗路径；UI预览仍未叠加特效。普通/EZ六动作/21受击/实际BattleAI受击已见effect1/2各7纹理（非声称每次战斗都完整loop），主存档不变/隔离恢复。完整循环另有19帧实播。15秒双角色P95约16.8ms、0帧>100ms、销毁owner0；仅本机Chrome。

## v92第三组已接入，下一项是身体动作/UI特效与46肖像
第三组20独立官方纹理替换原生39@30=1.3秒（前19各2帧/末1）；来源generation/skin100201-effect3-official-slots-v2，native-packed-v1。普通/EZ39帧全部看过、两圈实播各20纹理、生产资源SHA、effect1/2保留复播通过。实际隔离BattleAI338样本含234待机/104普攻，合计全部20纹理，主存档不变/隔离恢复。
当前两容器累计各40区域（三组全部纹理）替换，其余107身体区域与原生骨架/图集压缩块不变；普通/EZ仅算同皮肤的两个版本，不能算两独立皮肤。v91战斗overlay自动保留三组已批准childFX；UI仍不显示FX。v92双85各85/1876动作/14特效/125属性/6副骨架/21受击通过，双角色15秒P95约16.8ms/0帧>100ms/销毁owner0；85肖像4页已看并存SHA。
完整角色0/85、完整皮肤0/125不变，人物gongji/jineng/paobu未换。下一可修UI详情/编队FX独立坐标适配及补人物动作。85静态复查看到46钓鱼佬因鱼竿union体型偏小，先检查实际小卡crop/fit，不要盲裁道具；记static-roster-visual-review.json open note。
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
