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
- 角色 1 技能、角色 2–6 普攻/技能的 11 张姿势已看联系表并批准为视频引导。ID1 旧普攻右拳贴边已拒绝，方形画布重做 v3 已逐图检查通过。其他姿势待逐项人工检查；QA 的 automatic pass 不能冒充人工批准。
- `hero001-body-actions-minimax-v1` 是首个真正身体运动样片：124 帧，首尾待机，中间分别引导普攻、回到待机、技能、回到待机。脚本 `tools/street_body_pilot.py`，生成后须检查全部运动、身体身份和脚底稳定，再抠像、切片并按原 pia 事件打点重采样。尚未接入，不算完成动作。

## v0.24 进行中

- 已将 MiniMax 成功生成的牛角音波 VFX 接入 `common_skill_caocao_02_1` 及 `_ez`。保持原生 53 帧/24fps 动画时钟与回调；只替换显示。模型输入来自实际原效果回放视频，失败的 SageAttention 编译作业与成功重试都保留了记录。
- `tools/street-effects-runtime-test.mjs` 已通过：两次完成各一次回调、约 2.2 秒；销毁后新缓存为零；输出在 `art-migration/versions/0.24.0/effect-runtime.json`。
- `tools/street-effects-battle-test.mjs` 使用 8791 端口的隔离存档，不能修改玩家的 `pc_server_data` 存档。继承高关卡或仅一个敌人的尝试中，战斗胜利前未触发目标技能，90 秒等待超时，诊断保留。正确可复现场景要同时清零 `progress.battles` 和 `progress.stage=1`，ID1 单独出战、四个普通曹魏敌人、无支援实体，已在实际战斗触发新 VFX。
- 第一次实战发现 VFX 过大过亮，已把显示范围由 512 调为 256、alpha 0.72，第二次实战复查正在进行或已输出；务必查看 `effect-battle-live.png`，确认没有遮挡问题再提交。
- 修正 DBPlayer.reset/destroy 中 COMPLETE 与 FRAME_EVENT 移除监听函数写反的两处代码；85/85 角色详情在此修正后通过，0 异常、0 失败资源。
- 尚需：完成缩小后的实战视觉复查、重新跑 VFX 回调验证、全量台账复查、更新覆盖状态和 WORKLOG，然后提交 v0.24。
- 生成的 UI 主按钮底图已复制到 `local_game/assets/street/ui/primary-button-source.png`，提示词已保存。还未接入，不能宣称 UI 完成。后续逐键替换时注意原按钮可能含文字，不能直接用空白底图覆盖掉标签；图集子键需要防止被后加载的 sheet 覆盖。

## 不可遗漏的后续目标

85 人普通/技能/受击/移动/死亡及 125 条独立皮肤；所有 UI、字图、按钮、返回、道具、地图、建筑；尚未完善的玩法。已有图片身份绑定和待机不能冒充全部角色完成。全量清单约 19,063 文件，打包内容含 81,620 区域、7,239 动画。原始输入和用户未提交修改保留，禁止为了清单好看改成假完成。

继续使用原项目修复和实际浏览器验证；不要仅做独立展示页。每个实质版本全面复查台账和 85 角色，保留失败；每三版推送并核对 GitHub。到 20:00 如未全部完成，必须如实报告缺口，不得仅因截止就把完整换皮目标标记为达成。
