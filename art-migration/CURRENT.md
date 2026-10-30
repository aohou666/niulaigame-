# 游戏换皮接续（先读此文件，历史按需查 WORKLOG）

## 授权与范围
用户已授权自主继续，无需重复询问。85目标角色、125独立额外皮肤及全部UI/地图/建筑/文字/道具/特效，2.5D半写实半卡通离谱街区风；官方ImageGen/本地Qwen2.1与MiniMax H3。不能以关键姿势、共享图、局部测试冒充完整动作/皮肤；不能宣称零bug或全设备不卡。原10小时窗口已结束，后续用户明确继续，当前目标仍在进行。每实质版本全量台账及85角色复查，每3版推送并核对远端SHA。

## 仓库与交付
工作区 C:/Users/dongdong/Documents/ChatGPT/安装，分支 codex/street-reskin-20261029。delivery=https://github.com/aohou666/oldniulai.git，保留原origin。
最新实质版本v0.83本次提交，v0.82为efca267b。已验证delivery/main到v0.80完整6eb4f1fdf0a7b97b35f787688aaf7cff954dcd37。下一推送v0.83（81/82/83），命令git push delivery HEAD:main后ls-remote核对完整SHA。
保留无关dirty Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复及大量旧collector job/qa改动；禁止git add .、批量reset/删除。原resource大包是独立Release依赖，不入Git大包。

## 真实完成状态
完整角色0/85；完整独立额外皮肤0/125。连续攻技批准10/85：2、3、46、52、63、73、79、80、84、85；76动作映射，34隔离。2号v0.67新增独立跑动24源图，原生10帧循环；旧攻技RGBA保留。2号受击仍缺；战斗自主跑动触发未证明。
100201盛装小丑（2号独立青紫演出服、独轮车、右手核桃、左手两球）有4独立静态绑定和v0.70连续待机124原图/7WebP。普通/EZ/编队正式循环通过，原作198帧30fps的6.6秒保持；基础85英雄保留。完整皮肤还缺gongji/jineng/shouji/paobu、effect_1/2/3以及真实装备战斗验证。
100201普攻MiniMax-v1长停姿/跳变拒收；v2首帧only仍弱动作/停姿拒收；技能-v1双次抛球/停姿拒收。全部124及16放大已看，body-qa保存，不抠像不发布。目前无活动生成任务，旧worker JSON不作运行证据。

## 最新v0.81证据
版本目录 art-migration/versions/0.81.0。四项独立官方底框正式接入：名字285x38、属性202x39、透明外框640x346、小底框55x55。原生纹理/九宫格/截图已核对。来源generation/skin-panel-{namebar,attribute,outer,small}-official-v1；各自独立原图、SHA与技术适配说明，不共用占位。
先前正常AppFacade皮肤面板14类资源错误在hero2已复现路径全部消除，脚本/HTTP/网络/RES/Promise失败0；关闭SKIN-PANEL-069-RESOURCE-KEYS，只限此已复现路径，不等于历史DETAIL-NULL根因已修或所有面板穷尽。
125皮肤属性名称/数值按真实AttrConfig显示，非战斗枚举；4可见卡按源135x82比例159x96.58显示。已穿戴89徽章、佩戴/卸下/图鉴64图标、敬请期待159x246各有独立资产。状态测试是临时浏览器hero.dermaCode后恢复，不是装备交易。
原生列表私有renderer从list.itemRenderer取得；只注册一次gp_root监听读取当前data，修复旧闭包复用双回调及徽章遮挡点击。normal→last→normal真实中心点击计数1→1→2；末项清图名/状态并禁止选中。第四张是有效100202魔龙君临，第五项才末项，旧截图推断已纠正。
全85详情、10角色1876动作检查、1910运行依赖索引/全量台账通过。v0.82已对齐100201脚底与台面，关闭该已验证布局issue；新发现100202错误共用基础2待机，另开SKIN-PREVIEW-082-UNMAPPED-SHARING。其余原UI/地图/道具/角色动作/独立皮肤资产及玩法缺口仍多，不得缩小总目标。历史DETAIL-NULL、RESOURCE-LOAD-015和TEMPORAL问题未据此关闭。

## 运行与工具
Python .tools/python/python.exe，先设PYTHONUTF8=1；Node/Playwright已可用。
主服务8787使用pc_server_data/offline-replica-save.json，禁止重置或战斗测试修改主存档。隔离8794/8796先查是否在线，战斗工具用隔离save并finally恢复。
Comfy http://127.0.0.1:8188；实际queue/history为准。目录G:/comfylight/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI。
Qwen模型qwen_image_2.1_int8_convrot.safetensors，MiniMax H3已验证。已有任务只用street_comfy.py collect同一目录，不因观察超时重启。官方生成结果必须复制进项目并真实查看；PIL只技术裁切/缩放/alpha/图集，不作创作替代。
street_skin_action_candidate.py按独立skinCode/nativeAudit，禁止基础hero发布器覆盖独立皮肤。先前导图source QA、alpha清理与动作失败证据在generation/skin100201-*。

## 验证入口
node tools/street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立输出目录；成功后复制all-heroes-runtime.json/browser-log.json/detail-body-load-review.json到版本及全局输出。
node tools/street-body-roster-test.mjs 2 3 46 52 63 73 79 80 84 85 --version=版本（ID用空格）。
node tools/street-skin-attribute-test.mjs --version=版本 --assert-card-aspect --assert-worn --assert-race-icon --assert-clean-panel --assert-panel-frames。
node tools/street-skin-last-item-test.mjs --version=版本；不会覆盖老版本证据。
node tools/street-skin-idle-routing-probe.mjs --normal-panel --live --label=唯一标签；strict检查四类错误，结果outputs/street-reskin/skin-idle-routing。
Python street_atlas_verify.py；精确stage新启用图片后street_runtime_tracking.py（索引）与street_review.py --version版本。提交后tracking --tree HEAD。禁止把未入Git资源说已交付。

## 接续重点与上下文
下一步应修好预览/台面布局并验证实际选择/换装（隔离存档），随后推进100201完整身体动作和3独立特效/其余85目标，避免长期只做局部UI。原生皮肤审计skin-migration/100201/native-events.json：普通/EZ主动作45/46/21/198/16帧，普攻zd18；effect_1/2/3独立armature19/19/39帧，截帧直接骨架animation.gotoAndStopByFrame。
用户要求少占对话；输出定向摘要，历史只按需查WORKLOG/版本证据。保持重要进展/失败通知，不刷无变化状态。不能删除历史审计来制造完成；应用聊天历史无法由文件工具压缩。

## v0.82优先接续
100201脚底与台面global均[363,878]；属性底446/激活底502/身体顶608，脚底X/Y容器级锚点、截图/125属性/4卡/九宫格/阵营/无资源错通过。85详情、1876动作、1910依赖通过。并发详情采样曾失败，串行113帧复测通过；复用夹具加弹窗就绪+置顶等待后实际点击通过，不抹去失败记录。
下一v83重点：config100202实际model=hero_087_03，组件实际用基础2新待机，fidelity-gap.json明确失败。不要用猜的hero_skin_002_02（不存在，诊断资源错误无效）。可在皮肤面板容器标记明确选择skinCode，bindView只允许匹配该code/model的data.skins序列；没有批准独立序列时恢复原生模型而非共用基础新序列。注意清理旧standIn/原生suppress/cache，选择100201→100202→基础→100201及普通/EZ/编队均要证据，不能改测试期望掩盖错误。需实际读取配置建测试并记录无独立映射=未完成。v83完成后推81/82/83并核对SHA。无活动生成任务。

## v0.83进行中，勿沿用旧单一85门槛
独立预览守卫及真实选择/编队100201→100202→100201普通/EZ已通过；100202原生保留，不算新皮肤。初次全85旧审计83/85：20实际穿102002/modelhero_089_03，77穿107701/modelhero_092_03。原生回退正确，旧审计把这两个已装备原生皮肤强判无基础新待机，非基础动画坏掉。审计现分当前装备85详情（必须配置对应原生模型/可见性/技能、明确标原作未重绘）和baseaudit临时浏览器卸皮肤85基础新待机（恢复，不做交易），新待机还断言实际cfg.id等于预期。两组最终强化审计正在跑，尚未提交。10角色1876及1910依赖索引通过。
角色效果3的all-direct-timeline.jpg39张看起来相同crescent/dots，不可直接当有变化的motion-reference证据；下一步应检查原生实时播放/子骨架，再做MiniMax独立特效。无活动生成任务。v83提交后推81/82/83核对SHA。

## v0.83最终接续（优先于上文进行中状态）
实际独立选择普通/EZ/基础变体/编队切换通过；无批准独立序列恢复原生，100202不再共用base2。代码守卫显式skinCode优先，模糊共享模型不能单凭名当独立序列。新的fidelity测试tools/street-independent-skin-fidelity-test.mjs替代旧routing-probe手动面板模型循环作实际选择验收。
两套强化85审计均通过：当前穿戴85（83 new-base-idle、2 original-unreplaced-skin：20/77确实穿原生额外皮肤）；--base-heroes在独立浏览器临时卸皮肤、逐项恢复，85基础新待机ID/帧变化全部通过。每版应两套都验：street-runtime-check.mjs --all-heroes ...（当前装备），再加--base-heroes（基础）；不同输出目录，当前装备3报告复制版本和全局，基础all-heroes-runtime.json另存版本/base-heroes-runtime.json。审计报告含presentationCounts，勿把85详情通过当85完整换皮。旧83/85并非生产回退错，详见equipped20-77-state.json，已保留失败。1876动作/1910依赖/台账通过。
新open SKIN-NATIVE-083-PREVIEW-BOUNDS：100202原作模型已正确显示，但巨型原生模型超出面板，截图unmapped100202-native.png；下一步必须适配原生bounds，不能用新基础图遮它。100201批准新序列台面布局仍通过。没有活动生成任务。v83推81/82/83核SHA，下一推送v86。
