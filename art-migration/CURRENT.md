# 换皮任务接续入口

更新：2026-10-30。后续先读本文件，按具体任务读取证据；不要重复加载整个聊天、WORKLOG、资源台账或生成目录。

## 授权与目标

持续完成85角色、125独立额外皮肤及全部美术的一一对应替换，2.5D半写实半卡通离谱街区风；官方ImageGen/本地Qwen制作图片，本地MiniMax制作动作/特效，同时修复玩法、功能、性能。每个实质版本复查全85和全量台账，每3版推送并核对远端。原10小时窗口已结束，用户随后多次授权继续；不重复询问授权，不擅自缩小完成标准。

## 当前可验证状态

- 工作目录：`C:/Users/dongdong/Documents/ChatGPT/安装`；分支：`codex/street-reskin-20261029`。
- 本地HEAD：v0.67，`1f68e7b`；delivery/main已核对到v0.65，`b849faaefa9fdd009f684908cb1137ee7130c95a`。下一推送v0.68（66/67/68）。保留原origin。
- 完整角色0/85，完整独立额外皮肤0/125。连续攻技10/85：2、3、46、52、63、73、79、80、84、85。76动作映射，34隔离。姿势图/共用肖像不算完整动作或独立皮肤。
- v0.67：2号新增独立跑动24图块，单周期映射原生10帧30fps；旧124攻技图块RGBA逐字节保留。普通/EZ各4次循环及20帧截图、10角色1876项帧位/时序检查、全85详情及1768运行依赖检查通过。
- 跑动只证明原生夹具循环；8敌炼狱战斗证明攻技回归，没有证明战斗自主位移触发。2号受击仍缺。待机422页/10510图块未改。
- 当前UI/场景资源绑定81项；原作许多UI、地图、道具、动画仍未完成。所有完成比例以台账及对应证据为准，不宣称零bug或全设备不卡顿。
- 2026-10-30最近实际API检查：Comfy正在运行独立皮肤待机任务`1afd4f96-86e6-49a1-bdcf-fe208bc3d26c`，等待0；下一次先查同一任务，不重复提交。旧worker状态文件不能证明后台仍运行。

## 正在推进的下一项

正在制作2号独立皮肤100201（盛装小丑，模型`hero_skin_002_01`）。`skin-migration/100201/{plan,inventory,native-events}.json`含原资源SHA与普通/EZ16时间线证据：5人物动作45/46/21/198/16帧、3独立特效19/19/39帧，普攻zd18。原普攻普通/EZ45帧和普通技能46帧已查看，独轮车/杂耍道具必须覆盖。

本地Qwen已生成独立青紫演出服/围领/独轮车外观，`generation/skin100201-unicycle-qwen-v2/qwen_00237_.png`；实际右手一核桃、左手两球，不能写成提示要求的三球。BEN2及技术alpha清理已验，合格参考为`generation/skin100201-unicycle-matte-v2/clean-alpha.png`，同目录alpha-qa/alpha-cleaning保存证据。未发布。新MiniMax124帧待机候选`generation/skin100201-idle-minimax-v1`正在运行，收集后按全帧/透明边缘/循环验收；不能套用基础角色动作。当前四个静态绑定仍共用基础图，完整皮肤数仍0/125。

2号受击候选v1/v2均因长停顿拒收；12号body-v9/single-attack-v10也拒收。4号旧73帧实际复查不合格，保持隔离；attack-v3官方输出审核失败，requestId `49ece68b-771f-4509-bc79-3751a03843b1`，无图片，不换提供商规避。61/64也有既往审核失败，生成前查对应记录。

## 关键文件与入口

- 最新全量证据：`art-migration/versions/0.67.0/review.json`；历史按需查`WORKLOG.md`，不整份加载。
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
