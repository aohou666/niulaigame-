# 换皮任务接续入口

更新：2026-10-30。后续先读本文件，按具体任务读取证据；不要重复加载整个聊天、WORKLOG、资源台账或生成目录。

## 授权与目标

持续完成85角色、125独立额外皮肤及全部美术的一一对应替换，2.5D半写实半卡通离谱街区风；官方ImageGen/本地Qwen制作图片，本地MiniMax制作动作/特效，同时修复玩法、功能、性能。每个实质版本复查全85和全量台账，每3版推送并核对远端。原10小时窗口已结束，用户随后多次授权继续；不重复询问授权，不擅自缩小完成标准。

## 当前可验证状态

- 工作目录：`C:/Users/dongdong/Documents/ChatGPT/安装`；分支：`codex/street-reskin-20261029`。
- 本地HEAD为v0.69，`d97be85`；delivery/main已核对到v0.68，`43fde10eb774d77155bda84932c88e6e615441ac`。下一推送v0.71（69/70/71）。保留原origin。
- 完整角色0/85，完整独立额外皮肤0/125。连续攻技10/85：2、3、46、52、63、73、79、80、84、85。76动作映射，34隔离。姿势图/共用肖像不算完整动作或独立皮肤。
- v0.67：2号新增独立跑动24图块，单周期映射原生10帧30fps；旧124攻技图块RGBA逐字节保留。普通/EZ各4次循环及20帧截图、10角色1876项帧位/时序检查、全85详情及1768运行依赖检查通过。
- 跑动只证明原生夹具循环；8敌炼狱战斗证明攻技回归，没有证明战斗自主位移触发。2号受击仍缺。待机422页/10510图块未改。
- 当前UI/场景资源绑定81项；原作许多UI、地图、道具、动画仍未完成。所有完成比例以台账及对应证据为准，不宣称零bug或全设备不卡顿。
- 当前待查生成：attack Qwen-v2 `15921c2e-235c-4c21-9647-55d46145c1aa`最近API运行，等待0。其他任务已收集；下一次查同一任务queue/history，不重复提交。旧worker状态文件不能证明后台仍运行。

## 正在推进的下一项

正在制作2号独立皮肤100201（盛装小丑，模型`hero_skin_002_01`）。`skin-migration/100201/{plan,inventory,native-events}.json`含原资源SHA与普通/EZ16时间线证据：5人物动作45/46/21/198/16帧、3独立特效19/19/39帧，普攻zd18。原普攻普通/EZ45帧和普通技能46帧已查看，独轮车/杂耍道具必须覆盖。

本地Qwen已生成独立青紫演出服/围领/独轮车外观，`generation/skin100201-unicycle-qwen-v2/qwen_00237_.png`；实际右手一核桃、左手两球，不能写成提示要求的三球。BEN2及技术alpha清理已验，合格参考为`generation/skin100201-unicycle-matte-v2/clean-alpha.png`，同目录alpha-qa/alpha-cleaning保存证据。

v0.68已发布4项独立静态绑定：两头像、半身和官方盛装小丑铜框皮肤卡，路径`assets/street/skins/100201/revision-1f3efd1c1a2b6b40/`。原生HeroDermaListItem及4资源纹理/尺寸/别名、全85详情、1768运行依赖通过。证据`versions/0.68.0`和`skin-migration/100201/static-integration.json`。原始基础肖像及其他皮肤绑定保留；完整皮肤仍0/125。

MiniMax待机v1/v2近静态拒收。v3实际为连续双球杂耍多个循环：全部124原帧、16放大、8道具放大已查看，右手核桃/独轮车稳定，球数2，准许作待机循环原片。BEN2 `generation/skin100201-idle-matte-v3`的124 alpha及16放大也已看并批准，证明文件alpha-qa.json。尚未打包/接入，下一步独立皮肤待机候选，保留基础2号；原native daiji198帧30fps的6.6秒循环作为接入约束，避免错用基础角色发布工具覆盖hero2。

独立Qwen attack-v1姿势太接近idle而拒收；skill-v1抬两球参考批准，`generation/skin100201-skill-matte-v1`已生成单图alpha但尚未查看。attack-v2加宽参考画布并前置伸臂指令，正在生成。原生独立3特效属于各自armature；截帧须直接调用骨架animation.gotoAndStopByFrame，DBPlayer别名接口不支持它们，早期effect3空白图无效，已另取direct-timeline图核对。

v0.69 `character-idle.js`新增可选data.skins和按模型/拥有者选择独立待机缓存。普通/EZ/切回基础/再选皮肤四次路由通过；用浏览器隔离单帧测试配置验证，绝不是正式动画或完整皮肤。全85详情及1876动作帧位通过。实际data尚无发布的独立皮肤待机。

原生HeroDermaPanel选择核查已通过：按生产回调顺序从100201选100202后，预览/列表选中/名称正确；未发现所疑错位，不改该逻辑。证据`skin-migration/100201/selection-probe.json`。只读选择测试，无穿戴/激活RPC，未证明换装战斗。

新增已复现问题：正常AppFacade打开皮肤面板，14缺失/非法资源键导致404和28 null拒绝；`versions/0.69.0/skin-panel-normal-traced.json`与`skin-migration/100201/missing-panel-resources.json`保存逐键证据。尚未修复，不能以模型路由夹具通过说整个面板通过；也未证明与历史DETAIL-NULL同因。后续需实际补齐/绑定各UI资产和非法`_png`属性标签。

2号受击候选v1/v2均因长停顿拒收；12号body-v9/single-attack-v10也拒收。4号旧73帧实际复查不合格，保持隔离；attack-v3官方输出审核失败，requestId `49ece68b-771f-4509-bc79-3751a03843b1`，无图片，不换提供商规避。61/64也有既往审核失败，生成前查对应记录。

## 关键文件与入口

- 最新全量证据：`art-migration/versions/0.69.0/review.json`；历史按需查`WORKLOG.md`，不整份加载。
- 运行映射：`local_game/{character-art-data,character-idle-data,street-body-data,street-art-data}.js`。
- 全资源：`assets.jsonl`、`packed-art.jsonl`、`ui-regions.jsonl`；用脚本筛选目标行，避免打印大行。
- 2号run：`generation/hero002-single-run-{minimax,matte}-v1`；matte目录含alpha审批、action-design、integration；minimax含cycle-plan。旧攻技来源`hero002-body-actions-matte-v8`。
- 单动作生成：`tools/street_single_action_candidate.py`支持gongji/shouji/paobu、独立scope、相同高度足底、可选endpoints-only。`street_single_action_pack.py`只打包候选，不能自动批准或发布。
- `street-body.js`支持每动作geometry；`street_art_verify.py`检查动作alpha证明与补充原生审计。新增状态必须保留已有状态与事件。
- 历史问题见`open-issues.json`：DETAIL-NULL、RESOURCE-LOAD根因仍未知；TEMPORAL动作质量仍未全面解决。故障注入仅证明审计捕获，不能算游戏根因修复。

## 操作与验证约束

- Python：`.tools/python/python.exe`，PowerShell设`PYTHONUTF8=1`；Node/Playwright已可用。Comfy `http://127.0.0.1:8188`，实际queue/history为准；已有任务只collect，不重复提交。
- 主服务8787本次已恢复PID12104，启动存档SHA未变，绝不重置`pc_server_data/offline-replica-save.json`。8794/8796本次未运行，需用时先检查并恢复隔离服务。战斗隔离存档`outputs/street-reskin/stress/8794-save.json`，工具finally恢复。
- `node tools/street-runtime-check.mjs --all-heroes --assert-no-detail-body-loads --output=独立目录`；成功后复制3份审计JSON到版本目录及全局输出，再运行`street_review.py --version 版本`。
- `street-body-roster-test.mjs`角色ID用空格分隔；未批准角色不能混入已批准名单。新运行图片须先精确git add才能通过索引依赖检查。
- 保留用户无关修改；禁止`git add .`、批量reset/删除。`local_game/resource`原包独立Release依赖，不入Git大包。每3版`git push delivery HEAD:main`后`ls-remote`核对完整SHA。
- 图片创作/修改用imagegen技能；查看源图后再生成。PIL仅作技术裁切、缩放、alpha、图集处理。实际全帧和透明边缘必须人工查看，自动数字不能代替验收。

## 对话与上下文节流

用户明确要求减少对话占用。只在重要版本、可处理失败、关键决策时汇报；不逐个命令报完成。工具输出定向且有上限，JSON只打印必要摘要，图片只在实际验收时查看。重要结论写本文件或版本证据，过程保留WORKLOG。不得删除历史审计/生成结果来制造“完成”或空闲空间。聊天历史无法由文件工具删除，精简接续记录不等于已压缩应用内部历史。

## v0.70 接入收尾（优先于上文旧状态）
100201独立待机124原图/7WebP已正式接入，普通、EZ、编队live循环通过，原生6.6秒；248图块像素与124回退SHA核对通过，全85详情通过，1899依赖索引通过。10角色1876动作帧位回归全部通过。完整角色0/85、完整皮肤0/125。attack-qwen-v2已查看批准姿势参考，matte-v2任务502efb76-bbd2-4ccf-bddf-e997841d0d4e已提交，后续只collect。skill-matte-v1尚未做背景合成alpha验收。

## v0.71优先接续
已补官方皮肤背景pf_img_ditu_png，正常面板缺失键14降13但整面板仍失败27异常。85详情、1876帧位、1900依赖通过。普攻MiniMax e5f0cdc8-2e21-4314-ac58-35783a5c4c52实际运行，技能96517373-3612-4689-99e9-99cfb29da847实际排队；只collect。工具street_skin_action_candidate.py按独立skinCode和nativeAudit生成，未发布战斗动作。下一项官方选中边框generation/skin-panel-selected-official-v1，已保存透明原图及167x254缩放，需叠原生卡验收再接入pf_img_xuanzhong_png。

远端推送已核对：v0.71 HEAD与delivery/main均9cae85c0e95c2a7b16ef3d238895dc8d7d08b23f，1900依赖HEAD检查通过。首次443连接失败，重试成功。下一推送v0.74（72/73/74）。官方选中边框167x254灰背景叠图已看，透明中心/细框/勾选可读，仍未原生列表接入。

## v0.72优先接续
独立选中框pf_img_xuanzhong_png已正式接入，实际正常面板四项167x254纹理、一个可见，剩余12缺失键/23异常。85详情、1876检查、1901依赖通过。普攻v1停姿拒收，body-qa保留全部124/16放大实际审核，不抠像。普攻v2 d57e9fec-5bf7-4186-aeab-a81a15255adf首帧only实际运行，技能v1已终结正在collect/整段复查。官方卸下图标正在生成，工具cell181必须等结果保存，不重复生成。下一推送v0.74。

最新HEAD v0.72为8096529，暂未推送（下一v0.74）。技能v1全部124/16放大已看，双次抛球且中段停姿，拒收不抠像；body-qa保存。官方卸下图标cell181已完成并保存generation/skin-panel-unequip-official-v1，64x64尚待实际图标/按钮验收，未接入。普攻v2仍应查同一d57e9fec任务。

## v0.73优先接续
卸下图标已接入原生按钮并截图检查，正常面板剩11缺失键/22异常；85详情、1876检查、1902依赖通过。新工具street-skin-attr-inspect.mjs在数据就绪后发现125皮肤属性解析返回_png；诊断outputs/street-reskin/skin-attribute-diagnostics.json。类型[15,1011,1016,1017,1022,10001,10002,11001,11002]，需查原配置语义后改文字/美术，不能直接%10000。普攻v2只collect d57e9fec。下一推送v0.74。

最新HEAD v0.73 fa59eb6，尚未推送。普攻v2全部124/16放大实际看完：较v1无突跳，但只慢抬手、未形成清楚完整伸臂攻击且有长停姿，仍拒收，body-qa已记，不抠像。当前两个MiniMax任务均已收集终结，不能再说运行。下一步需改变实际编舞/参考或推进其余UI，未提交新动作任务。

## v0.74接续优先
125皮肤属性名称/值按AttrConfig修复并检查，移除无效_png和缺失默认pf_img_baojizi_png请求。剩9键/17异常，面板整体仍fail。皮肤容器指定脚底450使预览低于标题，但人物未贴背景台面/旧卡拉伸仍开issue。85详情和100201正式待机循环回归通过；1902依赖索引通过，10角色1876动作检查全部通过。没有活动生成任务，普攻v1/v2和技能v1均已拒收不抠像。v74完成后推72/73/74并核对SHA。

推送已核对：v0.74 HEAD和delivery/main均a4b005c92f6cdba5ae55d52f14cba24c0db823e4；1902依赖HEAD通过。下一推送v0.77（75/76/77）。

## v0.75在做
修复HeroDermaItem横图拉伸：原生类为私有未导出，首次game.HeroDermaItem补丁无效、比例测试失败；现从this.list_derma.itemRenderer取得实际类，4张原生135x82纹理按159x96.58显示并居中，125属性检查通过。全85/10角色回归运行中，未提交v75。官方佩戴图标工具cell228正在生成，完成必须保存到项目，不重复提交。

v0.75全85/1876动作/1902依赖/台账复查全部通过，待提交。官方佩戴图标cell228已完成保存generation/skin-panel-equip-official-v1；下一步验64x64及实际ButtonSkinIcon2，接入缺失common_icon_peidai。保留所有其他缺口，下一推送v0.77。

## v0.76优先接续
佩戴新图标正式接入，原生按钮检查/截图通过；正常面板剩8键/16异常。全85、1876检查、1903依赖/台账通过。下一项图鉴图标generation/skin-panel-catalog-official-v1已保存，需看64和原生ButtonSkinIcon2再绑定common_icon_tujian；注意原图非正方形已等比缩放，勿强拉。没有活动生成任务。下一推送v0.77（75/76/77）。

## v0.77在做
图鉴64x64新图标已接入原生80x94按钮并截图检查；正常皮肤面板剩7缺失键/15异常，未整体修复。1904依赖索引通过，85详情/10角色回归仍运行。官方已穿戴89x89徽章cell244正在生成，须等结果保存，不重复生成。下一推送v77。

v0.77全85/1876动作/1904依赖/台账通过。官方已穿戴徽章cell244已生成保存generation/skin-panel-worn-official-v1，89x89待看和原生项检查后绑定pf_img_yichuandai_png，无活动生成任务。剩7缺失键含4面板/属性底框、1职业图标和敬请期待/已穿戴。完整角色/皮肤仍0；下一推送v0.80。

远端已核对v0.77：HEAD和delivery/main均7f5237e98b050730c046c0e267914eb03bf9d4ca，1904依赖HEAD通过。下一推送v0.80。

## v0.78优先接续
已穿戴徽章89x89正式接入，4项原生状态/125属性/4卡比例及全85/1876/1905依赖通过。正常面板剩6键/11异常。状态夹具已改临时浏览器hero.dermaCode一致后恢复，明确未执行穿戴交易。下一项generation/skin-panel-coming-soon-official-v1已保存159x246候选，需实际查看/绑定pf_img_jingqingqidai_png，并修复原生isLast复用残图：在installOfflineCardAspect的dataChanged后对isLast显式换待更新卡、清lb_name、隐藏isLock、关闭image.touchEnabled；普通项恢复点击。不可计新皮肤。无活动生成任务，下一推送v0.80。

## v0.79优先接续
敬请期待159x246卡正式接入；末项显式换图/清名称/隐藏标记/禁图片点击。已修复原生复用重复监听，单次gp_root监听读取当前data，真实中心点击normal→last→normal回调1→1→2通过。第四张实际有效100202魔龙君临，第五项才末项，之前截图推断已纠正，不能计有效卡为残图。125属性/4卡比例/全85/1876动作/1906依赖/台账通过。正常面板仍5键/7异常：4个底框和职业图标；人物与背景舞台仍有距离。无活动生成任务，下一推送v0.80。

## v0.80在做
已移除皮肤模板不存在的默认职业子键；实际配置阵营图标_hero_ar_m_json.common_btn_wei的58x62纹理保留并核对通过，算错误加载修复不算新美术。125属性/4卡比例/穿戴状态夹具通过，正常面板剩4缺失底框键/6异常，1906依赖索引通过。全85/10角色动作回归仍运行。官方285x38名字底条cell273正在生成，必须等结果保存后再结束，不重复生成。v80收尾后推78/79/80核对远端。

## v0.80优先接续
无效默认职业子键清除，实际阵营图标58x62未变，125属性/4比例/穿戴状态/全85/1876动作/1906依赖/台账通过。剩4底框键/6异常。官方namebar cell273已保存generation/skin-panel-namebar-official-v1，285x38适配待看/原生面板验收。下一v81集中补4底框，勿每1资产反复出版本：namebar目标285x38；属性条common_img_heiditiao_03为202.27x38.89，九宫格(8,3,30,21)；主外框common_img_jichukuang_09在本面板662x900，九宫格(302,165,18,16)；小底框common_img_dikuang03在本面板125x30，九宫格(6,6,43,43)，原图建议至少55x55。需各自独立新图，保留原生九宫格并实际核对，或有完整设计的代码原生UI；不可通用占位遮错。无活动生成任务。下一推送v0.83。
