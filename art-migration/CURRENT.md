# 游戏换皮接续：先读此页，历史按需查WORKLOG和版本报告

## 授权与事实
用户已授权自主继续，不重复询问；Oct29十小时窗口结束后，Oct30明确续作。85目标角色、125独立额外皮肤及全部UI/地图/建筑/文字/道具/VFX，2.5D半写实半卡通离谱街区风。可官方ImageGen/本地Qwen2.1/MiniMax H3；每实质版全台账+两套85复查，每3版推指定GitHub核完整SHA。不以关键姿势/共用人物图/原作回退冒充完整动作或独立皮肤，不承诺全设备零bug不卡。
完整角色0/85，完整独立皮肤0/125。连续攻技批准10目标：2、3、46、52、63、73、79、80、84、85；76动作映射、34隔离。2号独立跑动24源→原生10帧，受击仍缺，自主战斗跑动未证明。
当前装备85=83新base待机+20穿102002/77穿107701原作未换皮肤；基础85审计临时浏览器卸皮肤逐项恢复，不做装备交易。85通过不等于85完整换皮。

## 仓库与交付
cwd C:/Users/dongdong/Documents/ChatGPT/安装，分支codex/street-reskin-20261029。delivery=https://github.com/aohou666/oldniulai.git，保留origin。
远端main已核d01b1193ca978489171b6094ef2803d4daa48af6（v89，87/88/89批次）；push-089.json和HEAD1915依赖核验存versions/0.89.0。v90本地586f01b214fbcaf83e0f25a26b9a2403a6f924f4，HEAD1917依赖通过。v91本次提交以git rev-parse为准。下一推v92，批次90/91/92，push delivery HEAD:main后ls-remote核完整SHA。
无关dirty保留：Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复、大量旧collector job/qa等。禁止git add .或宽泛reset。生成PNG可能被忽略，批准的源图需精确git add -f；运行资源须Git index/HEAD检查。原resource包是独立Release依赖。

## 100201已接入与v91修复
独立4静态绑定、124源待机/7WebP（原生198@30=6.6秒）、官方21独立源受击逐一映射原生21@30=.7秒。StreetBodyData.skins精确hero_skin_002_01主骨架、普通/EZ；effect_*不得绑人物idle/body。来源generation/skin100201-shouji-official21-v1及strip0-v2/strip1/2-v3；原生42暂停映射/21实播/真实装备与原生BattleAI受击在v88及v91报告。攻技跑动身体仍原作未替换。
v89 effect1：官方10纹理、19原生帧（前9各2帧/末1），alpha0.4；v90 effect2：另外独立10纹理、19帧、alpha0.5。两容器各147区域累计20替换，其余127与骨架/图集压缩块不变；继承旧包十区域逐像素一致，原生循环及战斗证明SHA递归保留。不是完整容器换皮；MiniMax仅材质参考，拒收视频未接入。
v91 street-native-fx.js修复战斗idle/hurt栅格替身隐藏整个骨架连带隐藏新特效：只隐藏原生身体槽位，保留已批准原生子特效与原时钟/事件，按110px身体适配；state owner隔离idle/body，未映射攻技跑动、init/reset/destroy恢复槽位和原变换。只战斗路径；UI预览仍未叠加特效。普通/EZ六动作/21受击/实际BattleAI受击已见effect1/2各7纹理（非声称每次战斗都完整loop），主存档不变/隔离恢复。完整循环另有19帧实播。15秒双角色P95约16.8ms、0帧>100ms、销毁owner0；仅本机Chrome。

## 下一项：第三组特效候选，尚未接入
20纹理/39@30原生帧，与前两组不同。原生基线v91/packed-fx-original.json，来源旧包，39截图仅审计。
新官方v1近环粒子相位跳变/重复，generation/skin100201-effect3-official-slots-v1/qa.json=rejected，不接入。
v2根据放大的原生20纹理逐格重绘，generation/skin100201-effect3-official-slots-v2已prepare20源；qa pending，未接入。需先看浅/深底20格，原生39帧普通/EZ/实播/真实BattleAI/资源SHA与旧effect1/2保留验证，再批准。构建须--base当前containers，不能从原包抹掉先前替换。工具street_packed_fx.py支持--effect effect_3；native-test支持--effect/--version/--baseline/--candidate。发布前native proof manualReview批准；发布后battle proof只核本次纹理，不把继承effect1/2混计。
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
