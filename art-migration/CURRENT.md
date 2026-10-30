# 游戏换皮接续：只先读此文件，历史按需读WORKLOG和版本报告

## 最新快照：v0.90全量回归通过，待本次提交，v0.89已推送
GitHub delivery/main=d01b1193ca978489171b6094ef2803d4daa48af6，87/88/89三版已推送，HEAD1915依赖已核；push-089.json记录远端一致。原下文v88/v86状态为历史，不据此回退。
当前100201两个原生容器累计各20区域替换：effect1十纹理alpha0.4、effect2新独立十纹理alpha0.5；effect2原生19@30帧普通/EZ和真实BattleAI52样本/全部10纹理通过，源generation/skin100201-effect2-official-slots-v1。v90两套85/1876动作/14特效/125属性/受击21帧/第一组特效保留复播及1917依赖通过。v90普通/EZ其他127区域及骨架/图集块未变，原effect1十区域逐像素保留；继承审计未删除。
替身idle/hurt隐藏原生骨架时子特效不可见仍open；effect3、gongji/jineng/paobu身体仍缺，完整角色0/85、独立皮肤0/125不变。下一推送v92（90/91/92）。实际Comfy队列空，无在跑生成；generation-worker.json是旧状态，不能称活动任务。

## 授权、范围与真实完成
用户授权自主继续，不重复询问。85目标角色、125独立额外皮肤、全部UI/地图/建筑/文字/道具/特效，2.5D半写实半卡通离谱街区风；官方ImageGen/本地Qwen2.1及MiniMax H3。原Oct29十小时窗口已结束，Oct30用户明确继续。不得以姿势/共享人物图/原作回退冒充完整新动作/独立皮肤，不宣称零bug/全设备不卡。每实质版本全台账+两套85详情复查，每三版推GitHub核对完整SHA。无关dirty不清理、禁止git add .。
完整角色0/85；完整独立皮肤0/125。连续攻技批准10/85：2、3、46、52、63、73、79、80、84、85；76动作映射、34隔离。2号独立跑动24源图映射原生10帧，受击仍缺，自主战斗跑动触发未证明。100201有4独立静态绑定+124源待机/7WebP，原生198@30的6.6秒保持；现已新增21@30受击并有隔离真实装备/战斗受击证明；仍缺gongji/jineng/paobu、effect_1/2/3及全皮肤验证。其余资产大量未完成。

## 仓库与交付
cwd C:/Users/dongdong/Documents/ChatGPT/安装，branch codex/street-reskin-20261029，delivery=https://github.com/aohou666/oldniulai.git，保留origin。
最新本地v0.88（本次提交后以git rev-parse为准）；v87为4463ab9c。delivery/main仍v0.86完整75849ddce72158771c0fdf4e87853a3d09683f90，push-086.json及ls-remote已核。下一推送v89（87/88/89），push delivery HEAD:main后ls-remote核完整SHA。v87 HEAD1911依赖通过，原resource包仍独立Release依赖。
保留无关Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复、大量旧collector job/qa等dirty。原始拒收视频帧大部分仅本地保留，Git保存工作流/QA/关键接触图/参考，拒收图不是运行依赖。

## v87新增地图与限制
bycc_img_ditu_png -> assets/street/environments/community-courtyard.png，960x898保留alpha。宫殿庭院改为青棚铜管社区站、修车棚/面摊/花箱/路锥/混凝土空场；独立官方源generation/city-community-courtyard-official-v1。实际skins.SlgCityView.img_bg隔离渲染别名/尺寸/原九宫格通过，native及720x898截图已看。不是城市服务器玩法证明。机械路由pass不能代替视觉批准。
额外1098高拉伸导致装饰拉长，拒收该扩展布局，CITY-MAP-087-VERTICAL-STRETCH open。生产SlgCityView所读代码不设置img_bg宽高，目前仅批准原生固定960x898；不要虚报纵向可任意伸长。若需要变高，应拆固定边饰+可重复空场，不能伸长树和路锥。
v87两套85/1876动作/14原特效/125属性4卡台面/6副骨架idle缓存复用回收/1911依赖及全台账通过，证据art-migration/versions/0.87.0。

## 当前生成与最新身体动作
实际Comfy队列空，MiniMax受击v3已collect39帧拒收（多出飞行道具/停姿），不是活动任务。100201官方21帧受击已接入，源generation/skin100201-shouji-strip-0-official-v2、strip-1/2-official-v3；不可共享给基础2或其他皮肤。candidate/alpha-qa/assembly在generation/skin100201-shouji-official21-v1，普通/EZ原生42映射/双21帧实播、实际装备BattleAI受击及挂机穿脱证据在versions/0.88.0。新图集3.6MB解码共享1份。完整皮肤仍0/125，完整基础角色仍0/85。

## 已拒收，勿重收冒充合格
100201普攻v1/v2及技能v1全部124帧+16放大已看，停姿/弱动作/双抛等拒收，无接入。
effect3-v1/v2全部124+16、v3全部56+16已看。v1暗网/形变/末尾静态guide跳变；v2长停姿/碎片化；v3时长对齐仍0..10停姿、12..24只局部旋转、26..55碎裂，均effect-qa.manualReview=rejected，无完整圈/alpha/运行接入。
shouji-v2(ref2va+原生完整运动视频)全部39+16已看，侧倒有但结束没回正、13脸模糊，body-qa.manualVideoReview=rejected，未接入。effect-qa仅早期接触工具记录，body-qa为动作权威。
不要仅反复做基础设施，继续完整动作/3独立特效及其他85/全部资源。

## 关键运行守卫（勿回归）
character-idle.js显式skinCode优先；无批准独立序列恢复真实原生，不套基础新待机。100202真实hero_087_03，切换100201→100202→100201普通/EZ/编队通过。20实际穿102002、77穿107701，两者原生回退正确，标original-unreplaced-skin不是换皮完成。baseaudit临时浏览器卸皮肤逐项恢复，不做装备交易。
100201脚底台面global[363,878]，bodytop608/属性底446/激活底502。未换100202首次真实bounds+20%裕量固定420x270，循环factor稳定，init/reset/destroy/切回恢复原变换；普通/EZ各2×9秒已验。
明确effect_*副骨架不绑定人物idle，普通/EZ6项0idle请求、复用/销毁active/cache/loading/queued0。street-effects.js可精确model+armature；hero模型必须指定armature，重复冲突保留原生；生产数据未新增独立皮肤特效。浏览器复用旧图集的路由fixture绝非新美术。
125属性按真实AttrConfig，4卡135x82→159x96.58；末项点击正常→禁选→正常计数1→1→2。正常hero2 AppFacade皮肤面板14资源失败已修；不等于历史DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL全部关闭。

## 环境与验证
Python .tools/python/python.exe，PYTHONUTF8=1；Node24/Playwright可用。主8787存档pc_server_data/offline-replica-save.json禁止重置或战斗修改；8794/8796隔离先查在线，战斗finally恢复隔离存档。
Comfy http://127.0.0.1:8188，安装G:/comfylight/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI。官方图生成用imagegen技能；PIL仅裁切缩放alpha/图集技术适配，不创作替代。
node tools/street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立equipped目录；第二次加--base-heroes另目录。equipped三JSON复制版本和global，base的all-heroes-runtime.json另存版本/base-heroes-runtime.json。两套均85，不混淆当前装备和基础。
node tools/street-body-roster-test.mjs 2 3 46 52 63 73 79 80 84 85 --version=版本；另street-effects-roster-test、street-skin-attribute-test完整断言、street-skin-effect-cache-test按更改复查。
新图精确stage后street_art_verify.py、street_runtime_tracking.py --report ...、street_review.py --version ...；提交后tracking --tree HEAD。查看JSON实际范围，勿仅看最后PowerShell exit0。资源计数和台账并非完整美术验收。
保持对话简洁，重要完成/失败通知；历史按需从WORKLOG和git旧CURRENT查，不重复载入巨量minified JS或全量脏文件名。不能用删除失败审计制造完成。

## v0.88：独立受击21帧接入与真实装备战斗修复
100201新增shouji：官方21个独立绘制源帧逐帧映射原生21@30=0.7秒，图集1162x780、RGBA解码3625440字节；新StreetBodyData.skins独立注册，不覆盖基础2。明确主armature hero_skin_002_01，只作用普通/EZ主骨架，effect_1/2/3不绑定人物body/idle。错误id/缺armature/重复模型骨架配置保留原生，不污染base2缓存，三负面fixture通过。
原生42项暂停帧映射、普通/EZ实播均观察21不同帧、约0.7秒、原生完成回调1次/无 authored frame events，全部21×2接触图及放大峰值已看，连续一次侧倒回正和道具数正确；切回独立idle、未替换攻技跑步原生回退、6特效骨架、复用/销毁0body缓存通过。首次暂停切动作测试发现旧idle.hidden保留会让未映射gongji立即采样时native也隐藏；render显式清理未映射非idle状态，已修并保留before-fix证据。
真实HeroDermaPutOn代理/服务器存档保存已装备100201后，demo构造实体仍dermaCode0，before报告复现。configureOriginalBattleEntity现在带入有效同subType皮肤；applyLocalHangUpEntity也从硬编码0修复。实际主入口打开HangUpSystemMed.MAIN，原生挂机载荷携带100201；真实PutDown后reload载荷归0，通过且隔离存档恢复/主存档不变。
最初数次真实战斗受击测试超时（before/after/slow-fixture/native-stage10均保留）；原战报113个指向该角色的结果没有负伤害，多次敌方攻击均标MISS。local fillLocalAdvancedAttrs以整数百分数生成Miss43，原生BattleAIAttrData直接用value，isHit公式max(0,1+Hit-Miss)，误读为43而非0.43。新增offline-battle-attributes.js只将明确标记的离线英雄/支援UI百分数在深拷贝AI输入中转比率，保留存档/展示实体/Atk Life Defence Speed Anger及未标记原生敌方属性；marker阻止重复转换。单元和实际AI审计43→0.43，真实负伤害出现。八敌/单敌两真实BattleAI战斗均触发新受击（分别10/9不同源帧在战斗打断前观察到，非声称实际每次战斗都完整21帧；完整21@0.7秒另有原生播放器实播证明），截图已看，原作未换特效仍可遮挡人物。不人工trigger命中、不改战报。
本机15秒普通/EZ双循环图集共享1份/users2，均21不同帧，P95约16.8ms，>100ms帧0；销毁0body缓存。只本机Chrome预热播放，不是APK/手机/所有战斗无卡顿保证。
两套85最终复查均85/85（当前83新base+2原作未换独立皮肤，基础85新idle），1876原有动作/14特效/125属性4卡台面/6副骨架/100202双9秒原生fit与独立切换/1913依赖全台账通过，85静态肖像4页已实际看并保存SHA。没有绑定错/缺原包文件。完整角色0/85、完整独立皮肤0/125不变；100201只有4独立静态、连续idle、这1个受击动作，攻技跑步和3特效仍缺。历史DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL、地图纵向拉伸issue不据此关闭。
Comfy实际队列空，无活动生成。下一实质版本v89，届时推87/88/89并核远端；远端仍v86 SHA75849ddce72158771c0fdf4e87853a3d09683f90。拒收MiniMax片段保留，不再称运行。

## 下一步v89（做真实美术进展，不只扩基础设施）
优先推进基础2仍缺的受击（与100201完全不同皮肤源，禁止共用），或100201缺失攻技/跑步和3独立特效。可先审计原生DragonBones slot纹理及完整动画，研究保留完整原生骨骼运动、逐slot替换新设计的方式；所有新组件必须真实生成/审批，一一映射，完整原生时钟和事件保持。不要以单个好姿势或坏MiniMax片段凑完成；若动画由骨骼/代码驱动必须明示，不冒充MiniMax整片批准。v89完成全量复查后推87/88/89并核GitHub完整SHA。


## v0.89：100201原生effect_1十张独立纹理替换
普通/EZ原容器各147区域，仅替换effect_1的10区域；其余137区域与骨架/图集压缩块逐字节保持。官方独立10源纹理按原生19@30时间线播放（前9张各2帧、末张1帧），不声称19独立源帧。MiniMax仅材质参考，拒收视频未接入。两个原生叠层下不透明v1遮挡身体，保留拒收证据；v2技术alpha0.4已在真实BattleAI战斗查看，104样本覆盖全部10纹理。原生19帧普通/EZ、完成回调/槽位时间线、父骨架攻技跑动子特效与RES别名/SHA通过。
范围限制：本版只完成effect_1纹理资源及原生播放器时间线替换。待机/受击栅格替身隐藏原生主骨架也会隐藏子特效，该上下文可见性仍待修复；effect_2/3、人物攻技跑动及其余皮肤仍缺。完整角色0/85、完整独立皮肤0/125不变，不把整个容器算全部换皮。
回归：两套85均85/85、1876原动作、14特效、6副骨架缓存、100201受击普通/EZ各21帧与125属性/4卡布局通过；主存档不变、隔离存档已恢复。运行依赖1915通过。不能据此声称APK/手机或全场景零bug不卡。报告在versions/0.89.0，按87/88/89批次推送并核对远端。
