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
