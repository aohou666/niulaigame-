# 离线复刻测试包

这份目录包含从原包运行缓存中恢复的 Egret 客户端、配置和美术资源。当前不经过 Icefox 登录，也不连接原服务器。

## 启动

连接 Android 设备并启用 USB 调试后，在 PowerShell 运行：

```powershell
.\start-local-game.ps1
```

脚本会启动电脑端资源与存档服务器、执行 `adb reverse`，并在测试设备中打开应用。电脑端使用 8787 端口，设备端使用 8788 端口，避免与 APK 内置服务冲突。存档保存在项目根目录的 `pc_server_data/offline-replica-save.json`，不会被打进 APK。

可直接指定模式：

```powershell
.\start-local-game.ps1 -Mode map
.\start-local-game.ps1 -Mode heroes
.\start-local-game.ps1 -Mode fight
.\start-local-game.ps1 -Mode demo
.\start-local-game.ps1 -Mode admin
```

指定虚拟机：

```powershell
.\start-local-game.ps1 -Mode launcher -Serial emulator-5554
```

- `map`：实际 SLG 地图视图。
- `heroes`：可搜索、筛选和滚动浏览 60 名可用正式武将，并在六个阵位执行上下阵。
- `fight`：选择敌方阵容、三档难度和 1–6 人规模。
- `demo`：读取当前本地阵容，运行双方普攻、主动技能、伤害统计、胜利结算并保存奖励。
- `admin`：在电脑默认浏览器打开可视化编辑后台。

电脑浏览器入口：`http://127.0.0.1:8787/offline-launcher.html`。

可视化后台：`http://127.0.0.1:8787/admin.html`。后台可编辑武将与人物、技能、皮肤、装备、我方/敌方阵容、世界地图奖励、摇钱树、功能开关和美术资源映射。保存后重新进入相应游戏页面生效。

## 当前状态

- 已恢复资源、主题、配置和主要客户端脚本。
- 已绕过 Icefox 登录初始化。
- 已禁止离线模式的 WebSocket 重连遮罩。
- 电脑端服务器提供 `/api/save` 的 GET、PUT、POST 接口，并使用临时文件替换方式原子保存玩家、主角、60 名可用正式武将、六个阵位、地图和战斗进度。
- 英雄升级已改为本地事务，刷新页面后等级和战力保持。
- 英雄与阵容使用原生界面：六个阵位支持点击下阵和指定阵位上阵，武将背包显示 60/60 名可用正式武将及原头像，变更立即存档。
- 世界地图的友军、敌军、五名玩家和城池会生成可点击标记；选中后可指定目标位置移动。排行、建筑、奖励、野外悬赏、四象争霸、霸业宏图和一键收获均有可操作面板并持久化。
- 本地阵容战提供黄巾余党、曹魏精锐、蜀汉突击、江东火阵、名将试炼五类敌方阵容，以及普通、困难、炼狱和 4/6/8 人配置；战斗包含全体敌军、技能回放、伤害总览和胜利结算。
- 战斗配置会立即写入电脑端存档；返回入口后“本地阵容战”会显示并使用已保存的敌队、难度和人数。
- 六名默认英雄均已生成四件初始装备，装备列表、英雄属性和本地存档可以互相恢复。
- 独立 Android 测试壳已完成构建，不包含 Icefox、渠道登录或原包原生代码；详见 `../android_offline_shell/README.md`。
- 本地钱包已接管铜币和元宝读取；英雄升级按原 `HeroUpgradeCostsLO` 配置合计并扣除铜币，不再使用无限资源调试逻辑。
- 主角升级、主角进阶和装备强化已接入原配置成本并持久化；初始档案含有限玄铁、进阶丹，阵容战胜利可继续获得这两种材料。
- 英雄升星读取原 `HeroUpstarCostsLO` 的下一形态和同名副本数量，更新配置码、星级、属性、技能与战力；阵容战会轮流掉落六名初始英雄的同名副本。
- APK 内置 `/api/save` 本地存档接口，档案原子写入应用私有文件；旧 `localStorage` 档案会自动迁移并保留一份兼容副本。
- 当前本地数据库部署 60 名有完整可用配置的正式武将，并生成对应的四部位基础装备；已排除开发测试木桩和缺失关键配置的条目。
- 本地关卡采用两回合战报：双方普攻与伤害结算后，我方释放各自主动技能；原骨骼动画、技能特效、音效、受击和胜利界面继续工作。

## Android 独立测试壳

已生成调试 APK：

`../android_offline_shell/app/build/outputs/apk/debug/app-debug.apk`

它使用包名 `com.local.offlinereplica`，入口名为“离线复刻测试”。0.13.0 支持两种模式：直接启动时读取 APK 内置资源和应用存档；由 `start-local-game.ps1` 启动时通过 8788→8787 反向端口读取电脑资源、电脑存档和可视化后台配置。本版实现本地世界挑战、摇钱树、武将技能解锁显示、四人敌方默认阵容，并新增武将、技能、皮肤、装备、战斗、地图和全部美术资源的电脑端可视化编辑后台。

```powershell
..\android_offline_shell\build-and-install.ps1
```

Android 14 真机与 Android 15 x86_64 虚拟机均已连接电脑端服务器。真机验证“江东火阵、炼狱、8 人”从配置页写入电脑存档、从入口再次启动后实际生成八名对应敌军并完成胜利结算。

## 资源镜像

如需续传缺失资源：

```powershell
& 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '..\recovered_runtime\build_local_mirror.py'
```

失败文件记录在 `download_failures.json`。


## 2026-10-21 完整角色待机

按资产表的素材目录 ID 接入 85 个角色，共 5201 张 PNG，来源为 `D:\参考图片\角色待机_抠像成品\各角色待机动作`。ID 13 于禁保留原待机。源 PNG 无损逐文件复制，24 fps 正向播放，游戏显示时按模型位置和大小适配，仅裁去透明留白，不修改原素材文件。非待机动作继续使用原骨骼动画。

预览：`http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=heroes&idlepreview=1`。也可从离线入口的“角色待机动作预览”进入。选择角色后使用游戏原生 HeroDynamicModel 和 DBPlayer 渲染；“逐项验证”检查 85 个序列的绑定和帧推进，以及于禁排除状态。

导入脚本 `tools/install-character-idles.py`；验证和备份位于 `outputs/game_idle_rollout`。本次更新电脑端游戏资源，未重新打包独立 APK。


2026-10-21 尺寸修复：待机显示使用整段序列的固定透明边界，不再读取逐帧变化的骨骼边界。详情页使用独立同级显示层，按 420×300 的舞台范围等比适配并保留顶部留白；战斗使用固定 210×260 的模型范围。长武器或宽体角色按完整宽高缩小以防出框。原始 PNG、帧序和播放速度不变。验证记录位于 `outputs/game_idle_size_fix`。


2026-10-21 六项显示修复：新待机首帧就绪前隐藏旧待机，保留攻击/受击原动作；CommonHeroName 改用中文文字标签；运行时清除 alpha≤8 的背景噪点，整段边界同步复核；完整背包补齐到 86 个（85 个新待机及于禁原待机）。详情页、布阵槽位、战斗分别适配，布阵主体高度125槽位单位，战斗主体高度110舞台单位，抵消原模型各自缩放。活跃序列保留缓存，离场后释放；显示纹理按实际屏幕需求适配，原始5201张PNG未修改。验证记录和回滚备份位于 `outputs/game_idle_six_fixes`。


## 2026-11-04 大招透明帧序列换皮

85 个角色的大招视频按原作帧数／帧率替换原皮，改动分三层：

- **素材**：`assets/street/ultimate/<角色ID>/f###.webp` + `meta.json`。由 `tools/street_ultimate_mat.py` 从 `outputs/street-reskin/ultimate-keys-86/videos` 生成：逐帧抠幕（移植本地绿幕导帧工作台的取色算法，并对同色系卡板补第二取色）、裁透明留白、按原作容器的帧数重采样、WebP 有损压缩。全部 83 个可映射角色共约 70MB（同内容 PNG 约 1.1GB）。
- **数据**：`street-ultimate-data.js`，由 `tools/build_street_ultimate_data.py` 生成，登记每个角色的目录、帧数、fps、帧框和可触发键名。只有唯一归属于某角色的键才直接触发；共享键（如 `common_skill_tianfeng_02` 被 6 个角色共用）改由施法者判定。
- **运行时**：`street-ultimate.js`。包装 `DBEffect.prototype.trigger`，命中某角色大招容器时隐藏原骨骼显示、在战场层中心播放新帧序列；帧率 = 原作容器 fps × 原效果 timeScale，帧数与原作一致，因此时长和技能时钟不变。帧图片按播放头前后 10 帧预取并即时释放，单个序列不会整体常驻内存；任何异常都回退到原效果。

没有可映射大招容器的角色（6 刀盾牛、18 肘击牛）继续使用原特效加此前的回纹换色候选，不进入本批。

验证：

```powershell
node tools/street-ultimate-test.mjs --hero=1          # 独立引擎夹具：隐藏原画、逐帧推进、按时结束
node tools/street-ultimate-battle-test.mjs --heroes=1,83,45  # 真实战斗场景（8794 隔离存档，自动恢复）
```

真实战斗实测：角色 1 的 53 帧全部呈现、耗时 1650ms（53/24/1.34），原画隐藏，AI 实际释放的角色 3／22／45 大招同样被接管；主存档 SHA 不变。

### 打包 APK（2026-11-04）

`tools/package-full-apk.py` 复用上一次 debug 构建的 shell（`classes*.dex` + 二进制 manifest + `resources.arsc`），把 `assets/` 整棵树换成当前 `local_game`，再由调用方签名。

两种产物：

- `--slim`（默认）：`outputs/原创角色换皮-大招版-精简.apk`，**1.21 GiB**（初始 2.05 GiB，降 41%）。
- `--full`：全部资产，`outputs/原创角色换皮-大招版-预览.apk` 等价物约 2.05 GiB。

精简模式删的是引擎取不到的内容，不是"看起来没用"的图：

| 类别 | 大小 / 文件 | 依据 |
|---|---|---|
| 未注册的街景 FX 容器 | 433.2 MB / 1026 | 不在 `street-fx-table.js` 的 `StreetFXResources` 里，`RES` 没有任何入口，全工作区也搜不到引用；含 `fx/pilot` 旧试验包 |
| 有 `_ez` 孪生的 HD 特效容器 | 348.5 MB / 890 | `DB_GLOBAL.ENABLE_AUTO_EZ=true`，`getDBFileName()` 只要 `_ez` 已注册就永远走 `_ez`；只删特效区（`effect`/`ui_effect`/`street/fx`），`model` 区的 HD 保留给 `useHD:true` 的展示模型 |
| 街景角色/皮肤 WebP 重编码 | 约 117 MB | `characters/`、`skins/` 以 q92 重压（原文件接近无损，体积虚高），哈希只当缓存键、不做校验 |
| 大 PNG 无损重压 | 约 50 MB | `optimize=True, compress_level=9`，像素不变；跳过调色板/16bit/动图 |

再往下压的可选项（未做，需确认）：`assets/street/idle` 图集降采样约 −100 MB、`model` 区 HD 容器 −75 MB、街景 idle 用 q85 再省 40 MB。原版 `resource/assets`（783 MB）是没被换掉的原始美术，删了会掉原皮内容。

关键约束（改打包脚本前先看）：

- **所有资产必须 STORED（不压缩）**：`AssetHttpServer` 用 `AssetManager.openFd()` 读资产，压缩过的条目会直接 404，表现就是「Asset not found」白屏。
- **ZIP 路径要镜像 `local_game`**：APK 里是 `assets/<相对 local_game 的路径>`。街景资产请求 `/assets/street/...`，所以 APK 内必须是 `assets/assets/street/...`；根目录的 html/js 则是 `assets/index_bh_...html`。
- **zipalign 处理不了 ≥2 GiB 的包**（实测 2.2GB 直接报 `Unable to open ... as zip archive`），所以 4 字节对齐由打包脚本用 `0xD935` 填充扩展字段自己写入；`resources.arsc` 必须 STORED 且对齐，否则 Android 11+ 拒装。
- 未打入：`assets/character_idle/`（85 个角色的全分辨率待机源帧，运行时走 `character-idle-atlas-data.js` 的 atlas）与 `assets/street/idle/**/*.png`（旧帧，atlas 只引用 .webp）。要连源帧一起打包会变成 5 GiB 以上，Android 也无法安装。

签名密钥：`outputs/apk-build/offline.p12`（别名 `offlinekey`，密码 `offline`）。同一密钥签名才能覆盖安装升级，别丢。

验证（Android 16 x86_64 模拟器，两种包都能正常安装）：

```powershell
adb install -r "outputs\原创角色换皮-大招版-精简.apk"
# 精简包实测：main / heroes / demo 三屏无新增缺资源；demo 战 matched 20、frames 174，
# StreetBody 帧 284；控制台只有既有的「找不到 pack.etc1.ktx，使用 png」提示（原包本来就有）
node tools/verify-apk-webview.mjs   # 需要先 adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>
```

真实战斗画面：`outputs/apk-build/slim-battle-1.png`、`slim-battle-2.png`。

