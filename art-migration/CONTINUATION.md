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
