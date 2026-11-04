## 2026-11-04 大招视频抠图并按原作帧率替换原皮（未发布）

85 条大招视频（`outputs/street-reskin/ultimate-keys-86/videos`）已全部抠幕并按原作容器帧数／帧率接入 `local_game`，83 个角色可映射（6 刀盾牛、18 肘击牛无对应大招容器，保留原样）。

- 素材：`local_game/assets/street/ultimate/<id>/`，83 个角色、2914 帧、约 70MB WebP（同内容 PNG 约 1.1GB）。生成脚本 `tools/street_ultimate_mat.py`，QA `tools/street_ultimate_qa.py`（`fringeTop` 已从 812‰ 降到最高 69‰）。
- 数据：`local_game/street-ultimate-data.js`（83 角色、159 个唯一触发键；6 个共享键角色靠施法者判定）。
- 运行时：`local_game/street-ultimate.js`，包装 `DBEffect.prototype.trigger`，隐藏原骨骼、在战场层中心播新序列，帧率 = 原作 fps × 原 timeScale，帧数与时长不变；前后 10 帧预取、即时释放；异常回退原效果。
- 验证：`tools/street-ultimate-test.mjs`（夹具，53/53 帧、2217ms、原画隐藏）；`tools/street-ultimate-battle-test.mjs`（真实 demo 战斗 + 8794 隔离存档，pass，主存档 SHA 不变）。真实战斗中角色 1 的 53 帧全呈现、1650ms，AI 实放的角色 3／22／45 大招同样接管。
- 待补：85 条中仅 83 条有原作容器映射；6／18 需先定位其大招容器。
- 提交与远端：`e107d5fd` 已推 https://github.com/aohou666/niulaigame-.git 的 `main`（新仓库为空，历史 `4a8edea3` 先推、特性提交后推），本地 HEAD 与远端 SHA 一致。
- 本地清理：删除 `local_game` 根 65 张截图（157.9MB，打包脚本会把它们塞进 APK）、旧 640 pilot 中间帧 215MB、临时探针 9.7MB、`outputs/migration smoke portable` 890MB，并对 `.git` 做 `gc --prune=now`（5.5GB → 1.73GB），合计释放约 5.1GB；明细 `outputs/street-reskin/CLEANUP-20261104.md`。`art-migration/`、`outputs/` 其余大件属交付/证据，未擅自删除。
- 复核：真实战斗（demo + 8794 隔离存档）复跑通过——角色 1 53/53 帧 1650ms、角色 84 共享键 40/40 帧、角色 83 62/62 帧，原画隐藏、主存档 SHA 不变、无报错；数据完整性 83 角色 / 2914 帧 / 0 缺文件。
- APK：`tools/package-full-apk.py` 复用旧 shell + 当前 `local_game` 资产 + 自写 4 字节对齐 + `apksigner` 签名。默认 `--slim`：删掉引擎取不到的 781.7MB（未注册街景 FX 433.2MB / 有 `_ez` 孪生的 HD 特效 348.5MB），再把街景角色/皮肤 WebP 以 q92 重压、大 PNG 无损重压，产物 `outputs/原创角色换皮-大招版-精简.apk` **1.21 GiB**（原 2.05 GiB，−41%）。Android 16 模拟器实测：安装成功，main/heroes/demo 三屏无新增缺资源（只剩原包既有的 ETC1 回退提示），demo 战大招 overlay matched 20 / frames 174、StreetBody 284 帧，战斗截图 `outputs/apk-build/slim-battle-1.png`。打包约束与进一步可压缩项记在 `local_game/README.md`。

## v0.98（当前）：100201 共享主动技能 FX 31 纹理接入

2026-11-02 用户恢复续作。v98 已把 `common_newskill_simayi_01_1`（15 纹理 / 62@24）与 `01_2`（16 纹理 / 16@24）的 normal/EZ 共 4 个容器接入生产 `street-art-data.js`（容器 6→10，version 0.98.0），目标 bin 逐字节 SHA 与候选一致。`common_newskill_simayi_01_3` 的 2 个 ground 纹理仍为候选（actualBattleDependencyProven=false），未接入。

生产实例验证无 route 覆盖：4 alias/digest 通过，四容器各跑完整原生循环 62/62/16/16 帧、24fps、回调/完成各 1、纹理 15/15/16/16；证据 `versions/0.98.0/active-fx-production.json` + `active-fx-instantiation.json`。

全量门禁：双85 各 85/85、1876 base 动作、14FX、125 属性、6 缓存、100202 fidelity 全通过；artverify errors[]；review bindingErrors[]/artErrors[]；generatedRuntimeGitTracking pass（1802，missing/binaryDiff 0）；verifiedPhysicalRegions 384、verifiedPhysicalAnimations 24（较 v97 +62/+2）。单资源 complete 69→73；完整角色 0/85、独立皮肤 0/125 不变。

ground 01_3 依赖审计已完成（2026-11-02）：`g_skill` 的司马懿组只有 `common_newskill_simayi_01_jn` 引用 01_1/01_2；`common_newskill_simayi_01_3` 只出现在 `default.res` 清单登记，无任何技能组/代码引用 → 孤儿资源，不接入，候选保留，不计入必需美术。证据：`skin-migration/100201/active-skill-native/dependency-audit.json`。下一步：剩余共享技能横幅；按 85 角色拆批推进。v98 提交 `980eab63`，交付记录 `f2ca7cb5`，远端 main/工作分支同 SHA。以下为 v97 历史入口，数字冲突以本节为准。

## 2026-11-03 工作区新增（未发布，不算 v0.99）

批量技能特效换皮已接入 `local_game`（245 键：202 图案 + 24 键回退换色 + 19 共享键按角色 66 引用）。
关键修复 1：`street-fx-dispatch.js` 原先在启动时注册的容器会被随后加载的 `default.res.json` 清掉，
导致单角色键 redirect 后运行时报缺资源；已改为 hook `RES.loadConfig` + 60 秒复核补注册
（HTML 版本 `?v=0.98.0-h018-2`）。关键修复 2：战斗优先加载 `<key>_ez_bin`，图案批量原先只有
normal，实战仍显示原版 EZ；已用 `tools/street_pattern_ez.py` 补 244 个 EZ 图案容器并在表中重定向
（`?v=20261103-batch-ez`，635 资源 / 451 重定向）。验证：EZ 图案在 smoke hero 12/24 与实战截图
（`battle/hero024-f3.png`）中生效，主存档 SHA 未变。边界：buff（护盾/治疗）、主角/美人技能、
宠物/UI 不在这一批，所以蓝球护盾、绿圈治疗、芙蓉出水保持原样；不等于 85 角色 / 125 皮肤完成。
预览入口 `start-fx-preview.cmd` → 8794 的 `fx-preview.html`（292 条）/ `offline-launcher.html`；
说明见 `outputs/street-reskin/preview-20261103/预览说明.md` 与 H018 笔记第 18 节。

## v97 历史入口（以下数字以 v0.98 节为准）
2026-10-30北京时间20:32核对到超过20:00截止，未及时执行截止，已停止新生成/代码/美术改动。只做保留、核队列和暂停续作。详见CUTOFF-20261030.json。v97 dc0867ab已推工作分支并远端SHA核对；main仍v95，v98未发布。新31FX候选实际验证和过亮失败证据均保留，不算已接入。Comfy本任务running0/pending0、worker0；原automation已不存在，将按截止暂停当前goal，不归档聊天。

# 当前接续入口（详细历史见 WORKLOG.md）

## 目标与规则
85目标角色+125额外独立皮肤+全UI/地图/建筑/道具/文字/VFX，2.5D半写实半卡通离谱街区；用户已续准，无需重复问授权。实质版本全量台账/双85复查，每3版推delivery/main并核SHA。完整角色0/85、完整额外皮肤0/125；不得把共享人物、关键姿势、原作fallback或候选当完成。当前原资产complete69，ledger其余以真实台账为准。无子代理授权。不得承诺全设备零bug/零卡顿。

## Git/环境
cwd C:/Users/dongdong/Documents/ChatGPT/安装；branch codex/street-reskin-20261029；delivery=https://github.com/aohou666/oldniulai.git，保留origin。
HEAD v97=dc0867ab7135327099900254d3f71d0263879c53；旧v96=3a7b47c0794c99db7f7eb63dc06007d2a3b30ac4；远端main v95=4eb1604c21b2e1a62d3289e21cefb272f77a3322已核；下次推v98（96/97/98），v97已commit并全量复查通过，HEAD1798依赖通过。v97启用1798依赖index通过（旧raster退出后减少，不是漏资源）；旧HEAD1926依赖通过，原resource包独立Release依赖。禁止git add .；精确暂存，忽略的合格PNG需add -f；保留无关dirty（Android/MainActivity/README/offline-launcher/disabled技能/旧collector等）。
Python .tools/python/python.exe，PYTHONUTF8=1、read_text('utf8')；Node24/Playwright位置见mjs。8787主存档pc_server_data/offline-replica-save.json禁止测试改写；8794隔离outputs/street-reskin/stress/8794-save.json，每场backup/finally恢复+主SHA，不并行两场写入测试。Comfy8188实时queue上次running0/pending0，generation-worker.json旧Oct29不当作活队列。官方imagegen句柄1078/1085/1094均终态；继续先核实际队列/句柄。

## 历史生产v96与基础缺口（v97已替换下述100201身体/UI）
100201生产仍为旧现代牛静态4张+124源待机(198@30)+21受击+45普攻，66格图集f1393faddd871997；zd18保持，v94回收核桃33前完成。原生主容器147区只40子FX已换，107身体仍原作；技能46/跑动16身体未换。v95共用qiu唯一纹理新核桃；v96共用impact13纹理normal/EZ全换，13@24及count/pia事件保持。完整皮肤未成立。
基础连续动作已批准10目标2,3,46,52,63,73,79,80,84,85；76映射/34隔离以台账为准。equipped85含20穿102002、77穿107701未独立换皮；base85另清derma浏览器fixture不改存档。未批准100202为原hero_087_03，不得套base新图。

## 100201原生资源证据（v97已接入原生身体、静态、gallery、preview、banner；共享主动FX仍未完）
总文件夹art-migration/generation/skin100201-native-body107-packed-trial-v2。107独立部件分组head3/clothing18/right15/left15/props7/ornaments25+24，精确无漏；原作107全部实际使用，不能称未用。新主容器107+继承40FX=147全换；骨架/atlas压缩块逐字节保持，normal1024x727/EZ512x371，无所属背景只清透明padding。normalSHA601ccab34885774377e922543625b1b52422cbacf03229f8f322636fab777498；EZ6e99ca52477642f8d27f239720b4f634b695bd3655af7b883e119cb44057c3f5。
body107-groups/native-use-all326在skin-migration/100201/native-body-parts；trial-body-regions-audit.json验证107源/ROI/147覆盖。所有源部件已看，左手v1/泡泡孔洞编辑v1拒收；props7-fit-v2只对新泡泡alphaScale.65。不是旧图重色/整帧持姿。
native-motion/motion-candidate.json：normal/EZ五动作198/45/46/21/16全部652帧实时采样，回调/完成各1，与baseline事件相同；event-frame-comparison核zd18。修复完成回调后已再跑全652通过。native-trial/trial-runtime.json不宜重写，native-preview-fit.json绑定它的SHA。先前“部件重叠是seek累积”假说已撤回，原作也有夸张配饰，失败证据保留，不得宣称引擎修复。
原生UI fit新可选CharacterIdleData.nativePreviews（带skin/hero/model/armature/containerSHA守卫），whole-idle-envelope修原首帧fit310>270越界；420x270不放宽。普通/EZ双6.6秒循环max160x234/161x231，3FX均见；100202原默认fit仍314x237。native-ui/runtime/review和3截图已看。
真实native-battle/runtime.json：实际穿戴持久化/原BattleAI981样本，daiji/shouji/gongji/zd18，通过主SHA/隔离恢复；gongji截图已看，shouji被敌旧FX遮挡，daiji截图是加载页不算外观证据。
native-battle-skill-scenario/runtime.json：只改隔离普通stage1，hero属性未改，原AI4回合34effects/41buffs，真实550020210/550020315，jineng21样本16不同原生帧0..15(漏6)，全46另motion证明；总2655样本。jineng截图已看；原作横幅与额外FX尚遗留。hell耐久场90秒超时为失败，已恢复存档，不算技能功能故障结论。
native-performance.json：双normal/EZ同步回调五动作20秒循环，各326不同状态，P95~16.8ms/0>100ms，destroy后无stage/armature；仅本PC暖Chrome。先前同步链只完成首gongji失败报告保留。

## 本轮真实功能修复（未发布）
local_game/js/main.min_6fea25ed.js只在DBPlayer trigger/gotoAndPlayByFrame两处COMPLETE注册once→addEventListener，ActionDoneHandler原先就先remove再callTrigger。修复Egret once分发结束清理误删回调内同步重注册监听器的问题。同步五动作链已验证成功，源码前后SHA在completion-reentrancy-source.json；未改其他once/时钟/reset/destroy。生产artverify outputs/street-reskin/v096-post-completion-fix-artverify.json errors[]。
v97已启用JS与配置：character-idle.js的nativePreviews全循环fit；character-art.js的skinText仅name/desc。两表已填100201，属性/费用未动。

## 静态/预览/横幅候选及新遗留
skin100201-native-static-fit-v1/candidate.json：5独立目标(4旧字段+gallery mjl_img_simayi)，新avatar/half/fullbody/frame官方源；角色名夜市杂耍掌柜/新desc，旧框旧字未拷贝。实际4控件+skinlist+gallery验证通过，截图已看；属性仍[[10001,100],[10002,100]]，baseavatar及100202独立原图保留。mjl_img_simayi2属于100202别动。
skin100201-native-activity-preview-v1：原common_activity_simayi_new01为19旧战斗截图/38帧24fps，已用新rig技能19曝光+批准新庭院图合成候选，无旧UI像素，非BattleAI录像。协议res/offset/labels/events保持；MovieClip实播1..38全见/complete1/1591ms通过，contact已看；未生产绑定。
技能额外原包common_newskill_simayi_01_1(15区62帧)/01_2(16区16帧)由g_skill主动引用；01_3 sibling2区normal30/EZ29@24，实际依赖使用待核。共6包33区设计范围已在active-skill-native/inventory.json，不被已换qiu/impact覆盖。
新active-ground2-official-v1透明核桃壳环/地裂两层，native-v1两包2/2候选通过。采样失败已定位为测具误用Bitmap.visible：EgretArmatureDisplay._batchEnabled模式直接GroupNode.drawData渲染，EgretSlot._updateVisible写node.alpha而不写Bitmap.visible。保留旧失败，改查真实GroupNode节点归属/alpha，原作及新候选同断言均通过(normal30/EZ29@24，各两纹理和1完成)。768x768捕获59暂停帧两张contact已看；normal连续淡出，EZ原本硬消失仍保留，不宣称优化了时钟。native-review.json仅批准原生纹理候选，不是实际BattleAI依赖证明或生产接入。
新增active15-official-v1/official-source.png（exec41eb2411），15独立格：flight+impact1..13+glow，深沟核桃/象牙粉尘/铜火花；原15map/guide在active-skill-native。均已保存分格source-qa.json，alpha>16各格边距9..154像素，无跨格。原图整体已看，仍待逐格/native尺寸及统一时间尺度适配，勿放大尾帧/按帧bbox归一。官方1126已终态，无生成活动句柄。
旧技能横幅zd_jn_002_skin_01_png598x316、zd_txt_002_skin_01_png271x110（糖衣炮弹）待换。新skill-banner-official-v1帽/手出界拒收；v2实际alpha>16bbox49,10,1711,888 in1726x911，轮廓在内；native-v1适配留6px安全边，新标题核桃开场重新字体排版已看。skill-banner-native-v1/candidate.json及assets/street/skins/100201/skill-banner-trial-v1保存。26381已终态无主动技能超时，失败报告no-active-skill-failure.json保留。75314重测已终态PASS：只在隔离场attack x10/life x100促主动技能，未改AI战报/手动trigger；native-battle-skill-banner/runtime.json含两图RES alias/尺寸/SHA断言，真实jineng横幅截图已看(新牛+核桃开场)，candidate仅批准横幅，不是整皮肤。所有本轮进程均已终态。

## 必须完成的下一步
1. 横幅候选验证已齐，后续合格资源正式接入时一起纳入全量账和依赖。
2. ground原作基线诊断；补主动FX31区新绘/原生及实战、33区依赖审计，避免仅rig完整就算全皮肤。
3. v97已完成full147 schema/provenance/motion/UI/battle/perf校验并接入2容器、4静态字段+gallery/preview/banner2图+name/desc；旧100201 raster退出配置、源图和配置存档保留。nativeSkins显式登记，completeSkin=false。后续继续共享主动FX31区，2区ground实际使用审查。
4. v97全账/双85/1876动作/14FX/125attr/6cache/100202fidelity/4肖像页SHA/index1798依赖全部通过，已精确commit并HEAD1798依赖核验；v98后推96/97/98，不造空版本。

## 既有守卫/验证
v88 dermaCode DTO真实穿脱/挂机；OfflineBattleAttributes只标记percent-points的离线AI深拷贝43→.43，不改显示/存档/未标原敌人。v93 46portrait132x257竖杆全道具保留；v87城市庭院960x898已准，1098拉伸拒收；CITY-MAP-087-VERTICAL-STRETCH/DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL仍未全结。
双85命令street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立目录，第二套加--base-heroes；body/effects-roster、skin-effect-cache、skin-attribute/fidelity按实质改动跑。stage后street_art_verify.py、street_runtime_tracking.py、street_review.py核JSON非只看shell。上下文只读此入口和当前证据，旧过程查WORKLOG/Git，不删失败/聊天，不声称系统上下文已手动压缩。


## 留待下一次明确续作的候选
active15-native-v3：飞行/碰撞13/光晕共15纹理，normal/EZ62@24均通过；统一碰撞scale.98，glow alpha.18。v1 EZ碰撞12裁切失败；v2实际过亮拒收，均保留。active16-native-v2：飞行/砸击14/曝光共16纹理，normal/EZ16@24均通过；统一scale1.3，impact alpha.28/exposure alpha.12；v1过亮拒收。两者native-review.json已记录候选批准范围、原作baseline和实际focused BattleAI证据SHA，非整skin完成。实际BattleAI使用EZ1_1+EZ1_2，各15/16纹理均记录，normal单独native；native-battle-active31-focused在body107-packed-trial-v2内，主不变/隔离恢复。ground2-native-v1也仅候选，实际消费关系未核。MiniMax e23c2392已成功收124帧、只接受作材料/衰减参考；official active16源实际引用其contact，无生成活句柄。下一次若获续作，再正式接入候选、更新台账、全量v98复查并推96/97/98批次；本次不再做这些新改动。
