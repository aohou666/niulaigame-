# 本轮续作入口

授权窗口：2026-10-29 10:00–20:00，Asia/Shanghai。不要提前声称十小时已完成，也不要把仍未完成的换皮目标标为完成。用户明确要求自主推进，无需重复询问授权。

## 已发布

- 工作目录：`C:/Users/dongdong/Documents/ChatGPT/安装`。
- 分支：`codex/street-reskin-20261029`。
- 交付远程 `delivery`：`https://github.com/aohou666/oldniulai.git`；旧 `origin` 保留。
- v0.21 commit `78445b0`，v0.22 `2043921`，v0.23 `ba58f3405eefebe48ddfbd570bfcf315f071ae04`，已核对远端 `main`。
- Release `street-v0.23.0` 已发布 784,222,148 字节原始运行资源包和 SHA 清单；GitHub 远端 digest 与本地一致，见 `release-manifest/github-release.json`。
- 下一次约定推送是实际完成 v0.24、v0.25、v0.26 后，不用空版本凑数。

## 当前生成和后台

- ComfyUI：`127.0.0.1:8188`，模型根目录见 `tools/street_comfy.py`，RTX 4060 Ti 16 GB。
- 本轮 169 项 Qwen 普攻/技能关键姿势在串行生成，ID1 普攻另有补做 v3。输出不等于完整动作。
- 后台 `tools/street_generation_worker.py` 每 45 秒采集真实结果并做结构检查，到 `2026-10-29T12:00:00Z` 停止本任务剩余队列。PID 记录在 `outputs/street-reskin/generation-worker.pid`。状态、日志和候选联系表都在 `outputs/street-reskin/`。
- 本聊天 heartbeat 续作已创建，id 为 `automation`，每 15 分钟到北京时间 20:00 截止。不要创建重复定时任务；20:00 时停用该 heartbeat。
- 另有当天 20:00 的一次性收尾 heartbeat，id `20`，防止季度小时续作的最后一次不恰好落在截止点。到时停用两项。
- 角色 1 技能、角色 2–6 普攻/技能的 11 张姿势已看联系表并批准为视频引导。ID1 旧普攻右拳贴边已拒绝，方形画布重做 v3 已逐图检查通过。其他姿势待逐项人工检查；QA 的 automatic pass 不能冒充人工批准。
- `hero001-body-actions-minimax-v1` 是首个真正身体运动样片：124 帧，首尾待机，中间分别引导普攻、回到待机、技能、回到待机。脚本 `tools/street_body_pilot.py`，生成后须检查全部运动、身体身份和脚底稳定，再抠像、切片并按原 pia 事件打点重采样。尚未接入，不算完成动作。
- 上述124帧样片已逐帧联系表检查，74–75帧拳头出画，已拒绝。`hero001-body-actions-minimax-v2-short-sage` 的73帧样片已查看全部帧及16张放大图，动作和身份通过到抠像阶段（不是最终验收）；普攻0–35帧，技能36–72帧。抠像作业 `hero001-body-actions-matte-v1` 已插到本任务队列前部，等待/检查输出。
- 加速编译故障已定位并修复：嵌入式Python3.13.14缺开发头文件、链接库；从Python官方同版本dev.msi提取266个缺失开发文件，未覆盖任何已有文件，Triton设备编译验证通过。为兼容活进程已缓存的链接库搜索路径，复制匹配python313.lib到该环境的Triton nvidia/lib；细节记录 `outputs/street-reskin/triton-dev-repair.json`。73帧SageAttention作业成功，实际242秒；124帧标准注意力288秒。后续批次必须先修正短片提示词中仍继承的124帧/五秒描述，与73帧、16/36/54/72锚点保持一致。

## v0.24 已本地提交，接下来制作 v0.25

- 已将 MiniMax 成功生成的牛角音波 VFX 接入 `common_skill_caocao_02_1` 及 `_ez`。保持原生 53 帧/24fps 动画时钟与回调；只替换显示。模型输入来自实际原效果回放视频，失败的 SageAttention 编译作业与成功重试都保留了记录。
- `tools/street-effects-runtime-test.mjs` 已通过：两次完成各一次回调、约 2.2 秒；销毁后新缓存为零；输出在 `art-migration/versions/0.24.0/effect-runtime.json`。
- `tools/street-effects-battle-test.mjs` 使用 8791 端口的隔离存档，不能修改玩家的 `pc_server_data` 存档。继承高关卡或仅一个敌人的尝试中，战斗胜利前未触发目标技能，90 秒等待超时，诊断保留。正确可复现场景要同时清零 `progress.battles` 和 `progress.stage=1`，ID1 单独出战、四个普通曹魏敌人、无支援实体，已在实际战斗触发新 VFX。
- 第一次实战发现 VFX 过大过亮，已把显示范围由 512 调为 256、alpha 0.72，已查看缩小后的实战截图并通过复查。后续两次完成回调约2261/2270ms、销毁缓存0。
- 修正 DBPlayer.reset/destroy 中 COMPLETE 与 FRAME_EVENT 移除监听函数写反的两处代码；85/85 角色详情在此修正后通过，0 异常、0 失败资源。
- v0.24 已完成上述复查，本地提交 `eed59fc`，未提前推送；待 v0.25/v0.26 实质完成后一并按每三版规则推送。下一个主要工作是把已验收运动、抠像后的身体帧接入ID1原生普攻/技能，验证后再铺开85人，不能把姿势图算完成。
- 身体渲染对齐建议：原视频512×512，准备参考时脚底约[256,466.7]、身体高度约413.3。取整段固定裁切，不能每帧重新缩放造成呼吸。ID1普攻原42帧/30fps，pia在第12帧（400ms）；技能原48帧/30fps。视频姿势最接近引导的帧是长时间伸拳保持中段，应找首次接近该姿势的时点对齐pia，而非机械用距离最小的中间帧。
- 抠像后可用原始RGB加抠像alpha重新组合，避免把抠像结果的预乘RGB再乘一次造成黑边。新身体层使用原生动画时钟，保留原技能事件和回调。返回待机时须尊重 CharacterIdle 的隐藏标志，不能恢复原模型造成两层人物同时显示。未生成的走路/受击/死亡仍标为未完成。
- `hero001-body-actions-minimax-v3-fastdecode` 已提交：正确73帧/三秒提示词、16/36/54锚点；解码改为512空间块、32时间块，并通过可传递的SaveLatent先保存视频latent再解码。若解码OOM，`tools/street_comfy.py` 会保存已输出latent，可重试解码而不重新采样。须比较真实耗时和画质后再选择批量参数，不能只凭猜测。
- ID1 的73帧抠像作业已成功生成全部73张PNG（文件在 `hero001-body-actions-matte-v1`），下一轮可直接检查alpha和边缘，制作原生42/48帧动作图集并接入，不要重复提交相同抠像。
- 生成的 UI 主按钮底图已复制到 `local_game/assets/street/ui/primary-button-source.png`，提示词已保存。还未接入，不能宣称 UI 完成。后续逐键替换时注意原按钮可能含文字，不能直接用空白底图覆盖掉标签；图集子键需要防止被后加载的 sheet 覆盖。

## 不可遗漏的后续目标

85 人普通/技能/受击/移动/死亡及 125 条独立皮肤；所有 UI、字图、按钮、返回、道具、地图、建筑；尚未完善的玩法。已有图片身份绑定和待机不能冒充全部角色完成。全量清单约 19,063 文件，打包内容含 81,620 区域、7,239 动画。原始输入和用户未提交修改保留，禁止为了清单好看改成假完成。

继续使用原项目修复和实际浏览器验证；不要仅做独立展示页。每个实质版本全面复查台账和 85 角色，保留失败；每三版推送并核对 GitHub。到 20:00 如未全部完成，必须如实报告缺口，不得仅因截止就把完整换皮目标标记为达成。

每轮续作先核对实际北京时间，避免长采样期间越过授权窗口后仍新增工作。

## 最新0.25完成
- 首个ID1身体动作已接入并验证，脚本street_body_atlas.py / street-body-runtime-test.mjs / street-body-battle-test.mjs，证据versions/0.25.0。源完整伸拳是10帧（放大6–11确认），对应pia12，不能再用源8帧。
- 人物动作73帧压成1600×1552、1,619,346字节WebP，按原RGB加alpha防暗边。真实8791战斗查看通过，85详情/841绑定复查通过，待推送规则依然为0.26完成后。
- 新street_body_batch.py只接受人工批准的姿势；2–6已front排队，按各自原计划bodyDesign/weaponObservation生成73帧身体。7–32姿势50张联系表看过并批准为guide，未生成身体。下一步可扩展批次，但先审2–6全帧和抠像，不自动批准。
- v3-fastdecode实际241.999秒，与v2的242.162秒相近，无明显加速，不要误报。

## 最新0.26远端与0.27
- v0.26 commit31def49e311779676bac277de0f4866a8a154bee已push delivery HEAD:main并ls-remote核对一致；本轮0.24–0.26三版同步完成。下一次按0.27–0.29三版后推送。
- 0.26实际替换21通用控件，官方新8图标+新按钮源8语义颜色变体，测试证据versions/0.26.0；原尺寸/九宫格/后加载图集不覆盖/真实游戏页面通过。
- 0.27维修队长3资源含真正当前可见`_hero_m_json.wujiang_img_renwu`（只改独立main_img_zhujue_png并不影响这个页面，已纠正）。查看调整后的实际页面完整。资产street-art-data/js与UI子区域2304完整清单已增加。0.27复查已生成，待本地提交。
- 新UI控件专项工具支持--version=0.27.0，避免覆盖已提交0.26证据；主角专项street-protagonist-runtime-test.mjs确证实际eui纹理，页面属性点击仅出现tooltip，这是预期行为。
- ID3身体全帧/放大复查通过、matte73已完成；ID8同样通过、matte已排队。下一步用通用打包/原时钟映射接入。当前street_body_atlas.py仍只硬编码ID1，需泛化而不覆盖已有数据。
- ID2 body被拒绝：核桃在idle右手和旧guide左手间切换。2攻/技v2批准已撤回，新的2攻/技v3实际已输出、qa pending，尚需看图，勿直接批准。之后要用body_batch --revision=2重做。
- 并排参考对照9/14/15/24/25/30/31发现道具/皮肤错误，全部14张v2 guide退回，v3正在队列，实际修正规则art-migration/prop-continuity-overrides.json；street_pose_continuity.py可复用，body_batch已读取override。
- ID7 bodyv1白刀光13/14、45–47越出画面，已拒绝；v2 height500而非620、紧凑刺剑，不要误用v1。body_batch新增--revision、--height，并使用版本化输入文件和参考文件夹，保留旧输入。
- 7/8/10/11/12 bodyv1已排队，7/8完成；4/5/6仍后部排队。其余有批准guide的16/17/18/19/20/21/22/23/26/27/28/29/32尚未提交body，可适度扩展，但必须全帧看完后再matte/接入。
- 0.27源prompts/repair-captain.txt保存原生成、裁切修订、独立全身生成三次prompt。全身source有光晕，最终PNG使用原RGB+RMBGalpha，原源保留。

## 最新0.28完成待提交
- ID3/8身体已通过新通用street-body-roster-test.mjs（--version=0.28.0；ID1/3/8两种模型474帧位+严格native totalTime+时点+缓存生命周期）和street-body-battle-roster-test.mjs实际隔离战斗。真实截图已看。ID3 pia6源16、ID8 pia17源18。新版测试传DBPlayer.init(name,name.replace(/_ez$/,''))，EZ payload armature名不带ez；早期错误诊断已存。
- street_body_promote.py已泛化，接受matte作业、--attack-anchor、--version，保留已有其他人物数据，使用metadata中各自原生动作长度/事件；多重命中需明确源锚点，不允许自动当成单击。
- street_art_verify.py现进入street_review.py，验证全部新图片digest/尺寸、每个身体tile非空/边界/不同帧及命中map。一共26张新图+219 body帧，0错误；0.28复查85/85通过。
- 新菜单背景已接入wujiang_bg_js_jpg；源workshop-courtyard-source.png、目标workshop-courtyard-menu.jpg、prompt已保存。独立street_environment.py能逐个背景按精确key处理，不批量覆盖语义不同场景。
- ID2新攻/技v3逐原图查看核桃手持一致并批准，bodyv2已排队；ID7 bodyv2更小身高和紧凑刺剑排队/已生成待查；ID8matte完成并接入。10/11/12已body_review结构检查，其中11的13/46/47边缘可疑，必须看全帧；尚未人工批准10/11/12。
- 已额外提交16/17/18/19/20/21/22/23/26/27/28/29/32身体v1，当前串行生成。这些guide已看过与idle并排图。9/14/15/24/25/30/31修正guide仍排队，勿用旧已拒绝图。
- 连续同模型实测body8为51.649秒、body10为52.488秒；首个/冷切换body7为241.928秒。只能报告具体样本，不承诺整批固定时间。
- 0.27已本地提交1025f20；0.28完后下一个0.29再按三版push。当前GitHub main仍31def49。session-control已更新。

## 最新0.29已验收待提交/推送
- 新8货币道具映射15资源（含tongbi实际顶部/升级按钮），官方source=assets/street/ui/currency-source.png，组定义ui-groups/currency.json、reference、cells，prompt/currency.txt。新通用street_ui_group_reference.py和street_ui_group_promote.py显式逐键裁切/原尺寸/变体，不把8图案说成15独创图案。
- ID10身体接入，原gongji/jineng各36帧，pia24→source16。四名1/3/8/10 body-roster 618帧位通过，实际10战斗图已看；0.29版本证据齐全，85详情通过。
- StreetArt/Body/Effects加载现在使用内容hash查询参数，防同名新文件沿用旧缓存；Android AssetHttpServer第118行已剥query。street_art_verify检查atlasSha；旧street_body_atlas.py现在保留其他人物而非覆盖整个data。
- 新street-resource-runtime-test.mjs验证全部RES/AssetAdapter/变体/额外别名及原生可见纹理；41bindings、13visible通过。效果专项测试已支持--version；主角专项和UI专项也支持，勿覆盖早版本证据。
- body2v2、7v2、11v1已看全部73及16放大图退回；12v1同样退回灰白→棕色漂移。10v1已看全帧/alpha并接入。2/7v3、11v2加入中途hold和回idle锚点并更小560/480归一化、无光效排练提示，已排队/生成待查。
- body_batch现在以实际override替换错误bodyDesign/weaponObservation，不再仅把override附在矛盾旧描述之后；每组guide共用安全高度和560最大宽度，参考输入版本化。更密锚点8idle/16attack/24attack/30idle/36idle/44idle/54skill/62skill/68idle/72idle；所有帧仍真正MiniMax生成，不是拼静帧。
- street_prioritize_jobs.py只取消尚未开始的本任务job并front重新排入，记录queueRevisions，已把默认6角色12姿势提升。其他角色未漏删。当前角色76实际手持白色饭团，旧plan说无手持武器但遗漏饭团；82手里是眼镜、79左手握背上大刃且无盾、77手捧莲花、94右手手机。后续guide复查须按真实图，不盲信旧plan。
- 待做明显文本问题：character-reskin-data.js中的definition/story仍混原作历史和旧别名（例82杰哥讲狐主转生，77佛系牛讲汉末军师），下一版应将85人的definition+三故事+synopsis逐人重写成现代离谱街区；不要只做搜索替换换名字。heroFields已有保护逻辑允许改这些文案，数值/技能机制不许动。
- 0.28 commitad07d4a，0.27commit1025f20。0.29提交后马上按三版规则push delivery HEAD:main并ls-remote核对。当前远端仍31def49，推完更新session-control。截止仍20:00，当前约12:28。

## 最新0.30已验收准备提交（本地13:18）
- 已push0.27/28/29，远端main=38a6a2e1c198e800650fd0ee58358e9e9ea66e2f，nextPush=0.32。
- v30新增85人255章独立现代街区故事、425独特技能标题、968有效显示记录；70/71/72 matched修复。source-mapping保留旧称与初始22孤儿显示记录；numericDescriptionChanges=[]。
- offline-skill-references.js修复294缺失等级引用并包装lookup，缺失rank3回落同家族已有rank2，不创造属性。normalizeSave只处理hero.skillList[].code；备份outputs/street-reskin/save-before-skill-reference-normalization.json，哈希save-repair-scope.json。不要触碰原用户untracked character-skill-repair.js（禁用stub）。
- world-text-runtime85/5085/20094通过，保护差异空；高阶41420014实际jineng和旧保存invalidcode兼容通过。85详情/所有新图资源复查通过。v30源码、stories、baseline、2runtime-test与exporter单独提交，不git add用户文件或未完成动作队列。
- body11v2全部73帧和16放大看完，无前版灰trail/出界，红T恤方格短裤及空手保留，已批准抠像，job hero011-body-actions-matte-v2 front排入。需看alpha并接入v31。
- 2v3/7v3及默认77/76/82/94v2身体73帧现已生成，尚未看全帧；不能直接批准。其他队列继续生成。当前本地约13:18，10小时截止20:00。

## 最新0.31验收准备提交（本地13:24）
- 0.30已提交5a598eb，尚未push，按规则0.32结束再统一push30/31/32。v31已接入2v3/7v3/11v2，七名1268frameChecks全通过，实际三名战斗通过，七名511frame图集。
- street_body_promote.py新增--event-anchors JSON：多normal事件及任何skill事件需要每个原生eventframe明确对应源frame。2normal16/17=>16/17；7skill5/11/13/32/47=>54/56/58/62/64（持续施技姿势，原生伤害/VFX事件不改）。street_art_verify核对全部eventAnchors，roster-test同名事件按次数/顺序逐时点检查。
- 77/82/94v2全部73帧+放大已看，通过待matte77/82/94；76v2饭团消失13-15/49-52退回，已更严格手球连体约束生成76v3，当前worker正在运行，不能当作完成。
- 官方新生成六种品质list底板source: assets/street/ui/hero-list-cards-source.png（6竖排，绿色/蓝/紫/橙/红/金），已看source，还未裁切接入，计划v32。原尺寸690x134，_hero_m_json.common_img_liebiao_1至6，bare同名_png。源边缘有一些alpha浮点，处理前需检查深浅底；不能直接说验收。参考outputs/street-reskin/hero-list-cards-reference.jpg。

## 最新0.32验收准备提交与三版推送（本地13:36）
- 0.31commit448a891。0.32新增77/82/94 bodyv2（matte已完成），三名实际8hell敌人战斗通过；全十人1902帧位base/EZ原时钟/事件/缓存通过。新的eventAnchors82normal0=>0,28=>16;skill0=>36,31=>54。打包器nativeImpact选第一个正帧事件，0仍保留单独映射。
- 82实战先两次失败，attempt1/2报告保留。trace每段只到native10就回idle。offline-hit-events.js窄修复两个82_03 base/EZ的gongji/jineng启动pia@time0抢先触发once回调问题；保留原事件流和数值，frameHandler仅跳过启动标记的战斗回调。paired-hit-runtime-test4case通过，原生仍2pia、回调一次933/1033ms、缓存清0。之后实际77/82/94全部通过。不要移除诊断失败报告或把它们写成成功。
- 六列表板官方生成+官方清理仍有白边，最终六格本地RMBG抠像完成并看图、street_ui_region_group.py按配置源格/alpha和精确sheet/bare映射。47资源18可见纹理通过，游戏原列表已看无碎边。ui-regions六条complete，其余2297pending。
- 0.32提交后立即push30/31/32 delivery HEAD:main并lsremote核对，nextPush0.35。
- tools/street-visible-assets.mjs新诊断输出visible-assets-heroes.json，已确认底部七导航实际语义：main_icon_wujiang居民、zhuangbei装备、ybd背包、zhandou战斗、baoxiang宝箱、lilian历练、gonghui公会。第八可生成main_img_tubiaodik_png圆底盘，准备下一批官方8图。无需把ybd误当商店。
- 9/14/15/24/25/30的v3姿势已与idle并排批准（道具手持正确），新bodyv1正在队列。31v3灰度仍太亮退回，新增--revision=4生成更深charcoal-black肤色/破西装（未看完不能批准）；76v3饭团严格持续双手握持已生成待全帧复查。当前约13:36，还有6h24，继续自主工作到20:00。

## 最新0.33验收准备提交（本地14:04；截止20:00）
- 0.32已提交且push并核对远端main=d9e0b387c9ec135945368b1ae692aee1a6097507。0.30=5a598eb,0.31=448a891。下一次push0.35，v33本地完成待提交。
- v33新增9/14/15各73帧身体，合计13人949帧/2492base-EZ帧位，最新roster通过；实际9/14/15战斗通过，截图已看。9技能18个pia时点用versions/0.33.0/hero009-event-anchors.json逐个映射54–64持续手势，最后117=>64，119=>72恢复。
- v33新官方navigation-source.png八格，语义七导航+圆底盘；groups/navigation.json/reference、prompts/navigation.txt。所有图已看，58资源32实际可见通过。通用group_reference/promote支持sheet trim offX/offY、sourceW/H完整外廓。新增street_ui_bind_sheet_variants修复黄/青/升级三个漏qualified；升级whole40x37而sheet91x92，不能把同名两者混为一个尺寸；新qualified不额外覆盖已存在bare的独立原尺寸。
- 新offline-navigation-state.js在MainUI异步children创建后用真实UnlockMgr同步gp_unlock，修复原空遮罩条盖导航；无每帧扫描。街坊标签替代导航武将。7button状态及实际dispatchTouch打开Backpack测试通过。
- 重点实际事件校准：art-migration/native-action-events.json完整344动画、172模型（包含额外13号），首次审计工具尾部expected170错误，仅断言计数有误，完整数据已导出；修正为172后再次全量跑完exit0。发现base/EZ差异15gongji(无/zd17)、34gongji(无/zd18)、37jineng(pia45/无)、48gongji(无/pia14)、49gongji(无/pia15)、66gongji(无/zd16)、78jineng(pia32/无)、83gongji(无/count0+pia20)。后续必须实际审计优先，勿照旧计划rawEvents直接填。
- tools/street_body_promote现在强制完整native-action-events，并按model分别构建actions，cfg.modelActionOverrides保留差异。StreetBody.render及roster/actualbattle测试按每个model选择对应映射。15base无事件使用原离线385ms补发，native11=>source16；15EZ原生zd17=>source16，两个专项均回调1次、正确姿势。误假设两模型都无事件的missing-hit-diagnostic已保留为诊断，工具已改名street-native-hit-runtime-test。legacy1只补nativeEvents元数据（pia12），原帧映射未改；全13cfg均有nativeEventAuditSha256。
- street_art_verify核对native审计SHA、全部26模型52动作时长/帧率/事件内容，并验证modelActionOverrides。不要随意重跑native-action-audit覆写已冻结基线（运行时间/elapsed字段会变SHA）；真需重审写新文件或同步cfg provenance。
- 重要尚未修复：一次14随机8hell战斗pageerror Cannot read properties of undefined(reading fightModelInfo)，初版test仅message所以缺stack。open-issues.json全局登记BATTLE-014-FIGHTMODEL并嵌入review；后续test已记录stack、trace、OfflineLastBattlePayload.teams和battleInfo。14独立重测及2次重复成功，第三次超过90s未捕获攻击窗口（可能控制/快速结束），不是修复证明。下一步做隔离全时长随机战斗压力采样抓stack/真实teams，修复具体原生空引用。可开8792等新server各用独立save并行，不能多测试同时改8791同一个save。
- offline_server路径local_game/offline_server.py，CLI --port --save --config；本机8787用户save、8791隔离effect-test-save，保存后会恢复。增强的--fixed-enemies=1只是请求首个敌人1，其他敌人仍由原有构建器补入随机，已记录实际teams，不能说全8都是1。
- 76v3全帧看完仍丢饭团13-15/45-47已退回；body_batch新增--dense-guides每4帧一个图像条件（所有73帧仍MiniMax生成，不拼静帧），76v4已排队/生成待查。9v1 alpha已看干净；14/15alpha已看并接入。24/25/30v1已生成未逐帧看；16/17/18/19/20/21/22/23/26/27/28/29/32更早bodyv1仍待复查。12v3姿势、31v4深黑肤色、75v3去光球、79v3前挥刀姿势都待看新结果。
- Worker约14:00，generated201/submitted53/pending52，仍按45s自行收集；当前总量会变化。原13仍旧人类，在真实战斗中可见；可单独额外补新身份/动作，不能把它冒算用户85中。还未启动额外13生成。
- 下一阶段：继续body批量逐人审查接入；处理常见巨大的旧蓝爆/龙蛇/红斩特效遮挡（MiniMax生成，非只降透明度）；主界面还剩武将/布阵/图鉴三个旧标签按钮、顶部主公牌/主角属性、VS/胜利等；所有移动/受击/死亡/独立皮肤仍未完成。


## 2026-10-29 14:56 最新 v0.34
- v34准备提交：16角色攻技(新增24/25/30)，1168帧，2994映射，64模型动作核对；全部3实战通过且截图已看。85详情最终无异常，但首轮2次null拒绝原因未定，openissues继续保留。
- BATTLE-014具体FB131问题修复在offline-summons.js。4lane各24场20秒采样(96)全无异常，前4lane都重现原问题；单位原生AI验证10召唤9自爆、分伤及反击；131真实表现完成651ms且推进至ROUND6。142连续链尚未视觉认证。audit512条有总数。audio防积压修复和6项验证通过。
- 四stress服务器8792-8795独立save完成已恢复，可复用。8791probe完成已恢复。outputs/stress-after保存全部96结果，修复前stress不要覆盖。
- 76densev4已看全73+16，饭团全程保留，approved-for-matting并抠图排队；16/18v1全73+16/source看完同样抠图排队，17v1约20帧裁边已拒，v2height520排队。
-33/34/36/37/38/39/40/41/42/44/45/47及49/52/53/54/55/56/58/59/60/62/64及65/66/68/70/71/72/73/74/75/78/80/84/85导图均逐个与idle对照批准，bodyv1批量排队。51attack含火光已撤销批准，未排body。
-35/43/46两导图道具丢失已拒，61鼓槌换手、63麻将丢失、69小绿环丢失、81skill胡萝卜消失已拒。50/57/67/48手部待大图核对，83原火球需要分层方案。31v4、12v3、79v3待看。13额外角色官方3姿势v2路径见上轮摘要，尚未抠图/接入。
- v34提交后下一版本35需按33/34/35一起push delivery main；32远程d9e0b38已核对。原用户未提交文件不动。下一步扩大动作接入、补移动受击死亡和皮肤，旧大特效/顶部VS/UI很多未替换。


## 2026-10-29 15:12 v0.35 最新
- v34已提交2000379，v35准备提交并马上push33/34/35到delivery main，必须ls-remote核对。v35当前19角色1387帧3622映射76模型动作，新增16/18/76；三个真实战斗通过，失败前测保留。16/18/76alpha全73+16均已看。
- 战斗UI8新图已接入(总65绑定，6新sheet区域=剩2280)，官方source battle-controls-source.png。图生成间距不均，sourceBox明确沿透明间隙，group_promote已支持显式sourceBox。实战截图看过，旧顶部头像head1_zhu_10_png/独立头像圈、字体、其他UI仍待换。新角色动作截图多被原大特效遮挡，但全部原生帧位和单独图集检查通过。
- 35/43/46/50/51/57/61/63/69/81实际道具修正版3共20Qwen导图刚排front，用--square保留道具，prop-continuity-overrides有逐手说明。原35金属爪/罐、43菜刀、46鱼竿/桶、61左鼓槌、63左麻将、69右绿环、81胡萝卜不能掉。48/67还没判手部，83火球分层待做；12v3/31v4/79v3需看。
- GPU worker约15:10 submitted40余，Qwen20在前，MiniMaxbody近30在后。现无实战测试占8791，所有save已恢复；其他8792–95也空闲。所有19cfg数据在street-body-data.js。
- tools/street-effects-export-batch.mjs已导出6高频原特效全帧(native.json记录原生frames/fps/aabb/origin)：common_buff_hudun20@24、common_skill_longzhua_0115@24、common_skill_tongyonghuiji9@24、common_skill_huifu28@24、common_skill_qusan19@24、common_skinskill02_jinjishushi_01_232@24。在outputs/street-reskin/effect-reference各folder。多数aabb0，origin256,256，要看输出图是否裁边再用于MiniMax。尚未生成新6特效！最常用禁忌术士命中275次/96样本、护盾203次，优先处理遮挡巨大蓝爆与光球。
- 原effectpack硬编码hero001单条会覆盖effects表，不能直接拿来批量跑。应新建通用打包器保留existingrecords、读真实native时间和anchors；source参考视频用原导出帧ffmpeg编码到Comfy input，然后MiniMax ref2va模板hero001-cast-minimax-v2。当前模板124帧5秒4steps；可以合理改73/512但必须真实生成审查。新工具还没创建。
- 额外13已官方生成v2三姿势但未抠图/接入；源路径exec-d921af9b-e80e-47de-a285-99f6369d8fd8.png在generated_images当前session；现有013pose-source-v1被裁头拒绝，不能用。需单独RMBG3cells+生成body73和独立idle73，不能拿attack前9帧循环冒充新idle。不要改变85目标集合。
- 本heartbeat最终应通知重要v35上传完成，下一次继续到20:00。deadline12UTC，不要提前宣称全替换或零bug；所有move/hit/death和独立skins未完成。Goal保持active。


## 2026-10-29 16:03 v0.36 最新，必须接着做
- v35已push核对remote main=6131446353cf6e66fc16de65b77b634607cda2d6；next push after38（36/37/38）。v36准备本地提交，当前22角色1606帧4134映射88动作，新增20/21/26全帧+alpha+实战截图已看通过；65UI绑定未变。全部角色完整数仍0，动作death/hit/move和独立125skins未完成。
- v36新增street-spark-hit特效，替换common_skinskill02_jinjishushi_01_2/base+ez，124帧新MiniMax→原32@24；官方6设计参考source local_game/assets/street/effects/neighborhood-six-guides.png。新1FX全124+16放大看过，旧蓝云没有保留。初次实战切入镜头会放大到覆盖全屏，已修runtime cfg.maxScreenDiagonal=240按屏幕变换限大小，保留原本位置/clock/events/伤害；3个Point复用，缩放0.2/1/4/12测试通过，之后实战3实例33trace和截图已看，变小且不中断战斗。before/after在versions/0.36.0，初版结构测试pass不等于美术通过，visual-diagnostics明确。
- street_effect_promote.py现在通用不覆盖旧表，读人工approved effect-qa且不裁边，保持native fps/count/峰值，用固定union裁小quad，source sampling单调。street-effects-roster-test4模型170帧原生时钟/显示/销毁缓存0，effectslive单独8792测试通过。8791三身体战斗通过并恢复save；所有服务器当前空闲。
- 其他5FX v2全有原图重建：heal0–25原绿色柱、impact49后原白斩、grapple57后原橙环、shield74后原蓝罩且爆炸/裁边/不闭合、cleanse54后原蓝球。全reject不接入。cleansev3把VAE参考去掉但仍66–82蓝尾光，亦拒。现在5新job（heal/impact/grapple/shield v3,cleanse v4）通过tools/street_effect_image_only.py已排最前。用ONLY官方新图VAE/CLIP条件，不喂原视频（referenceVideoRole明确仅离线动作分析），仍用原生metadata和phase映射；不能说此轮原视频像素条件。注意护盾必须首尾一致持续循环不能衰退/爆炸。所有新FX都124帧，review工具两all页就全124+16。
- 当前GPU后续还有30+body/Qwen任务，无人审自动不上线。19/23v2dense已队尾；22/27/28/29/32v2denseheight520最后也排队。原19/23多出一拳/踢腿，27草束碎，28/32自带flash，29越界，22胸灯复制，已分别拒。20/21/26待提交源folder v1，26bodybattle单独备份后重测20/21合并，最后reports3全通过。
- 新导图50/51/57/61/63/69/81 v3与idle对照批准，两手/物件现在正确，bodyv1排queue-tail。46v3鱼竿/桶都保留，尚未批准，需要解决长杆导致归一化主体大小不一致：body_batch当前按全alpha bbox缩放，须给各idle/attack/skill标主体头脚landmark计算scale，再把长杆连同全画布放进去，cfg.bodyHeight也取主体高度。别直接promote导致小人/跳大小。79attackv3刀在前已批准，skillv3仍刀在后是windup，待改。48/67手持物还需细看。
- 12原图实际褐条纹，旧override错误写gray导致v3灰白，现已改暖taupe brown+chocolate，v4排最后。31原脸charcoal但衣服尘灰而不是漆黑，胫骨暗黄铜不是镀铬，v4太黑已拒并用修正override排v5。不要反过来再改原肖像来匹配错误导图。
- 额外13官方v2三姿势仍未处理！源在当前session generated_images/exec-d921af9b-e80e-47de-a285-99f6369d8fd8.png；v1裁头不能用。先3cell matte，审核后做body+独立idle，补supplemental绑定且85目标表不变。原13人类和原NPC907、独立皮肤仍实战可见。
- 所有native6效果metadata/reference视频与官方6裁图保存在art-migration/references/vfx-native和vfx-guides；生成export工具不要设置_characterIdleSuppressNative否则黑图。tools/street-effects-export-batch支持多个name实际加载并逐帧截1024，native.json有foregroundBox/peak/fps/origin；aabb有时0但像素bbox非空已验证。
- 20:00=12UTC截止，停本任务新生成/新改动、核对停止ownpending、真实盘点、最后push、停automation和20，不归档，不因deadline设goalcomplete。

- 实测get_goal于16:04返回后台status=blocked（此前摘要active不准确），此轮没有调用update_goal设置blocked或暂停。继续用户已授权的heartbeat工作；API不支持自行resume，不要伪造active或另建重复goal，也不要因此停掉仍有效的10小时工作窗口。session-control记录实际observed状态。

## 0.37.0 — 五类特效、原生变体时钟及生成队列恢复

- 新急救加号、石灰冲击、拖钩、清洁扫帚各124帧和线圈护盾73帧全部逐帧/16放大复查后接入，覆盖base/EZ共10个新增容器；原视频只供动作分析/时序映射，本轮生成仅用官方新设计图约束。护盾首尾差0.444/255且无爆炸/裁边；旧错误版本全部保留拒绝记录。
- 真实读取14个原生DB模型事件与时钟，发现挥击9/8、拖钩15/14、清洁19/18、护盾20/19的base/EZ差异，补独立逐模型映射。火花实际pia第15帧，视觉峰由旧图亮度第4帧改对齐15；不改原生伤害/事件。14模型348原生帧位、全部销毁缓存归零和0.2/1/4/12父级缩放上限通过。
- 新效从生成黑底RGB做max-channel alpha及反预乘，常规alpha合成，保留黑底观感并降低亮背景上的加色漂白；全123新效图集帧与原生成RGB裁缩图逐像素核对误差<=2，未添加动画帧。重新实际战斗查看急救/冲击截图。仍有原蓝水柱/凤凰/其他特效未换，不能当全特效完成。
- 三个独立环境各30秒战斗观察到护盾/清洁/拖钩/火花；原生AI+表现层的8/4号20%初血测试场景实际观察到回复/冲击，未向场景合成注入新特效。最初错以为56主动技能治疗，实际原配置是毒敌，两次未覆盖治疗的失败记录保留，改用真实治疗4号再通过。样本不代表所有阵容长时验证。
- 生成worker因补充13号三姿势design无action触发KeyError，曾使监控状态停更；候选检查改为只读带heroId/action的导图，异常局部隔离，截止检查前置至结果收集之前。两个隔离假队列测试验证只停止本任务ID、外来队列不受影响，QA报错仍会更新状态。worker恢复后全部已排队任务已生成，尚待人工审核的内容不计完成。
- 85目标和22攻技身体数量未增，完整角色仍0，独立皮肤/移动/受击/死亡仍待换；已开始额外13安全员独立待机和攻技，但本版本未接入。最终全量台账、85详情、841头像、65UI与所有现有动作/特效另见review.json。DETAIL-NULL-REJECTION仍调查，未宣称零bug。

- v37待本地提交，36/37/38完成后一起push并核对main。13 body-v2已全73/16看过批准，抠图job20bc3a1f-42fd-474d-aa5f-b763d0880b50；独立idle-matte-v1全73/16已看通过。需supplemental13独立idle映射/头像，不改变85目标集合；全部动作齐全仍为0。workerPID36440，最新log generation-worker-1635.log。

## 0.38.0 — 补充13号安全员独立待机、动作和肖像

- 85目标以外仍在实战出现的原13号，新增官方白盔橙背心安全员形象，右手红对讲机、左手停/指路动作。第一版技能生成大绿光被拒，第二版全部73动作帧和透明结果/16放大复查后接入；另生成完整独立73帧呼吸眨眼待机，未用攻击开头冒充待机。共146帧同一坐标/比例图集，普通/EZ各保留原27帧攻击、27帧技能及60帧30fps待机时钟。
- 待机原生实际事件审计独立保存，不覆盖344动作冻结证据；新增228个普通/EZ原生帧位、6模型动作审计及回调/命中/缓存释放通过。13号8敌炼狱真实攻击/技能通过并恢复隔离存档，实战及详情截图已看。初始详情按战斗110高度显得过小，改为明确详情标记250高度，战斗大小保持原配置；独立待机实际详情帧推进验证通过。
- 4个原生肖像资源逐一保留原尺寸，头像/半身/立绘真实RES载入通过；名称与人物介绍改为街区安全员。supplementalHeroes单列，原85目标集合不变，没将共用基础形象计为独立皮肤。新增文字只改展示字段，原技能和属性不变。
- 85详情再次全过、841目标加4补充图像绑定检查通过；22目标攻技加1补充角色，现1752身体图集帧、94模型动作时钟/事件核对。完整角色仍0，13号移动/受击/死亡和所有独立皮肤也未完成，其他原美术仍有大量缺口。16:35修复worker保持有效；生成完成不等于人工验收。

- v38本地完成后立即push36/37/38并核对remote main。下一版39：19/23v2已全73/16批准抠图，各matte正在生成；17v2发现冷灰蓝紫衣变暖象牙、鞋色漂移，虽无裁边仍reject，需修guide。4/5/6v1自动裁边已reject，v2 height500 dense已排队。不要把任何这些未接入内容写成完成。

## 0.39.0 — 九名角色攻技动作与缺事件变体对齐

- 19条纹衫、22机械装、23练功服、27草束马装、28红衫西装、29圆黄牛、33蟑螂苍蝇拍、34松鼠橡果、36头巾拳手，各73帧原生成及全部透明结果、16放大和身份对照均逐项看后接入，共657帧。22旧版复制胸灯、27旧版草束炸开等没有沿用；当前持物完整。36实际拳峰在源13而非预设16，明确对齐源13。
- 23技能6次pia分别对齐源48/51/54/57/60/64；27技能2次pia对齐48/62，不改原生事件或时长。34普通版无攻击事件，保留既有385ms补发，映射原11→源16；EZ真实zd原18→源16，专项实际两种回调各一次和姿势通过。
- 九名普通/EZ共1464帧位、36模型动作时钟/事件、共享缓存与清理均过；三个独立存档环境各3名、每名真实8敌炼狱战斗通过，实际teams/trace及截图留档并已看。原有大斩光/龙等VFX仍会遮挡身体，属于未完成资源，不算已经换完。
- 累计31目标攻技角色，加独立待机/攻技补充13号；2409身体图集帧、130模型动作核对。85详情再次全过，841目标及4补充图绑定、65UI与全部已接入图集全量校验。所有角色完整动画和独立皮肤仍未完成，完整数0。
- 审查17v2发现冷灰蓝紫袍变暖象牙，长横笛可见性不足，拒绝并按实际长笛/冷色重新排Qwen导图；4/5/6v1自动裁边拒绝后缩小主体重做；32v2仍裁边。没有以自动检查通过代替人工身份审核。
