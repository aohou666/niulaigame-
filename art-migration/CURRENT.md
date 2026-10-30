# 游戏换皮接续：只先读此文件，历史按需读WORKLOG和版本报告

## 授权、范围与真实完成
用户授权自主继续，不重复询问。85目标角色、125独立额外皮肤、全部UI/地图/建筑/文字/道具/特效，2.5D半写实半卡通离谱街区风；官方ImageGen/本地Qwen2.1及MiniMax H3。原Oct29十小时窗口已结束，Oct30用户明确继续。不得以姿势/共享人物图/原作回退冒充完整新动作/独立皮肤，不宣称零bug/全设备不卡。每实质版本全台账+两套85详情复查，每三版推GitHub核对完整SHA。无关dirty不清理、禁止git add .。
完整角色0/85；完整独立皮肤0/125。连续攻技批准10/85：2、3、46、52、63、73、79、80、84、85；76动作映射、34隔离。2号独立跑动24源图映射原生10帧，受击仍缺，自主战斗跑动触发未证明。100201有4独立静态绑定+124源待机/7WebP，原生198@30的6.6秒保持；缺gongji/jineng/shouji/paobu、effect_1/2/3、真实装备战斗验证。其余资产大量未完成。

## 仓库与交付
cwd C:/Users/dongdong/Documents/ChatGPT/安装，branch codex/street-reskin-20261029，delivery=https://github.com/aohou666/oldniulai.git，保留origin。
最新本地v0.87，6f9ce1e4（后续文档若amend以git rev-parse为准）。delivery/main仍v0.86完整75849ddce72158771c0fdf4e87853a3d09683f90，push-086.json及ls-remote已核。下一推送v89（87/88/89），push delivery HEAD:main后ls-remote核完整SHA。v87 HEAD1911依赖通过，原resource包仍独立Release依赖。
保留无关Android build.gradle/MainActivity、README/offline-launcher、disabled技能修复、大量旧collector job/qa等dirty。原始拒收视频帧大部分仅本地保留，Git保存工作流/QA/关键接触图/参考，拒收图不是运行依赖。

## v87新增地图与限制
bycc_img_ditu_png -> assets/street/environments/community-courtyard.png，960x898保留alpha。宫殿庭院改为青棚铜管社区站、修车棚/面摊/花箱/路锥/混凝土空场；独立官方源generation/city-community-courtyard-official-v1。实际skins.SlgCityView.img_bg隔离渲染别名/尺寸/原九宫格通过，native及720x898截图已看。不是城市服务器玩法证明。机械路由pass不能代替视觉批准。
额外1098高拉伸导致装饰拉长，拒收该扩展布局，CITY-MAP-087-VERTICAL-STRETCH open。生产SlgCityView所读代码不设置img_bg宽高，目前仅批准原生固定960x898；不要虚报纵向可任意伸长。若需要变高，应拆固定边饰+可重复空场，不能伸长树和路锥。
v87两套85/1876动作/14原特效/125属性4卡台面/6副骨架idle缓存复用回收/1911依赖及全台账通过，证据art-migration/versions/0.87.0。

## 当前活动生成：只collect，勿重复提交
已终态：skin100201-shouji-minimax-v3，prompt25e893c9-eb44-464f-9122-d819d7ed86fd，queue18，已collect39帧；全39+16放大已看，飞出额外球/核桃且中间长停姿，拒收。实际queue已空，无活动Comfy任务。不要沿用之前运行状态。实际Comfy /queue /history权威，旧generation-worker.json active过时。
v3用fl2va模型首末同独立idle+第17帧新受击guide，39源帧短片1.625秒；原生shouji21帧@30=0.7秒、无事件。中间guide仅生成条件不是完整动作。工具street_skin_action_candidate.py已支持shouji39源/原生21审计。collect同目录→street_body_review.py→全39+16放大逐看→合格完整受击回正后才alpha、21帧映射、普通/EZ原生与真实战斗受击验证。自动时序筛选pass不等于人工批准。
原生受击参考：outputs/street-reskin/skin100201-native-shouji-v2，全部21帧已看、全帧边距>15px；art-migration/references/skin100201-shouji-native-v2有39@24完整重采样视频/原图SHA/已看接触图。暂停帧不证明实时采样。旧v1截屏frame10球裁边已拒收，只删除实际pending queue16，保留quality-cancelled和失败证据。新官方受击guide原图/768透明适配已看批准设计，右核桃/左两球/独轮车/青紫服保留。

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

## v88接续优先：官方21帧受击源已制作，尚未接入
MiniMax受击v3已终态拒收、实际Comfy队列空；不要再称运行或重提交。改用官方逐帧图像源，全21帧是独立绘制的实际in-between，不是插值/复制关键姿势。三条7帧已技术拆分并查看全部21浅/深底接触图，道具各帧右1核桃/左2球保留；需在原生0.7秒回放中继续验证接缝和idle切换，尚不计完整动画。
有效源目录generation/skin100201-shouji-strip-0-official-v2（0..6）、strip-1-official-v3（7..13）、strip-2-official-v3（14..20），均有official-source.png、frame-NN.png、strip-qa.json。strip0初版外框裁边拒收；strip1/2首版相邻身体重叠已重排留白。工具street_sprite_strip_prepare.py只拆分7独立alpha轮廓，拒绝粘连/贴边/重复；auto-columns各crop可共享空白gap、不共享人物像素，未降低6px边距门槛。21有效源各strip按共同缩放对齐轮胎脚底[384,680]，不逐姿势拉身高，不生成任何插值帧。校准和审查art-migration/../outputs/street-reskin/skin100201-shouji-official21-review/assembly-plan.json（实际从根outputs路径读取），all21-light/dark-calibrated.jpg已看；shouji-wheel-size-review.jpg记录初始尺寸差。
下一实质v88：先组装候选atlas+原生21帧@30一一映射，再给StreetBodyData单独skins注册及主骨架守卫；禁止旧street_body_promote.py覆盖基础2。当前street-body.js只支持characters按model绑定，不能直接偷塞id2，且新独立body必须不绑定effect_1/2/3。完整动作还须ordinary/EZ、销毁回收/原生事件不变、真实隔离战斗受击触发和全量两套85/台账。未完成攻技跑动/3特效依然未完成。此源准备不是新游戏版本，不新增完成计数；v87地图已提交，下一三版推v89。
