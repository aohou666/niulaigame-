# 真机 APK 卡加载 — 问题记录与排查手册

## 症状

用户原话：**"我手机安装后打不开，一直在读进度条，读完又音乐就是没进入主界面"**。

拆开就是：
1. APK 能装、能启动；
2. 加载进度条会走完；
3. 有声音（音乐起来了）；
4. 主界面始终不出现。

## 已知事实（本机实测）

| 环境 | 结果 |
|---|---|
| Android 16 x86_64 模拟器（API 36，默认内存） | 能进主界面，战斗/大招正常 |
| 同一模拟器 `-memory 1024`（1GB） | 一样能进主界面 |
| 模拟器上精简包 + `verify-apk-tour.mjs` 三屏巡检 | 无新增缺资源；只剩原包既有的「找不到 pack.etc1.ktx，使用 png」提示 |
| 桌面 Chrome | 同一套资源正常 |
| 用户真机 | **卡在加载后，未定位** |

证据截图：`outputs/apk-build/apk-main.png`（模拟器主界面）、`lowmem-1.png`（1GB 模拟器）、`slim-battle-1.png` / `slim-battle-2.png`（模拟器战斗）。

注意：本作 `mode=main` 的**主界面本来就是深色背景 + 左右两列功能入口 + 底部导航**，中间不是城市地图（城市地图是 `mode=map`）。
所以先跟用户确认一句：手机上到底有没有看到顶栏（头像/等级/VIP）和底部「街坊/装备/背包/战斗/宝箱/历练/公会」？
- 看得到 → 其实已经进主界面了，只是中间空，是"观感不对"而不是"进不去"；
- 完全黑屏/白屏 → 按下面的流程查。

## 可能原因（按优先级）

1. **旧 WebView 兼容**：主场景初始化链是 `preload_pack → loadGame() → new eui.Theme("resource/game.thm.json") → COMPLETE → GameMVC`。老 WebView 上任何一步抛错都可能让后续 promise 永不 resolve。
2. **精简包删出了真机才会走的路径**：`DB_GLOBAL.ENABLE_AUTO_EZ=true` 时特效优先 `_ez`，但 `useHD:true` 的展示模型走 HD；`preloadEffectList()` 这类预加载是按名字整组加载的，真机若走了不同分支可能请求到被删的 HD 容器（本机未复现）。
3. **内置资源服务差异**：`AssetHttpServer` 用 `AssetManager.openFd()` + Range，真机上某些条目/请求可能失败。
4. **GPU/WebGL 上下文丢失**：音乐会继续、画面停住，表现也可能像"卡住"。

## 排查步骤（任选，从便宜到贵）

### A. 手机浏览器对照（不用装包、不用 USB）

同一 Wi-Fi 下让用户开：

**http://192.168.1.190:8790/offline-launcher.html**

- 服务器没开就这样起（隔离存档，不碰主档）：
  ```powershell
  & .tools\python\python.exe local_game\offline_server.py --host 0.0.0.0 --port 8790 --save outputs\street-reskin\stress\8790-save.json
  ```
- 判定：
  - 手机浏览器**也卡住** → 设备/WebView/GPU 兼容问题，与 APK 打包无关；
  - 手机浏览器**能进** → 问题在 APK 的内置服务或包内容。

### B. 完整包 A/B

让用户改装 `outputs\原创角色换皮-大招版-完整.apk`（2.05 GiB）。
- 完整包能进、精简包不能 → 精简删的东西确实有真机路径在用，重点查 `assets/street/fx` 与 HD 特效；
- 两个都不能进 → 与精简无关。

### C. 真机 logcat（最有效，需要 USB 调试）

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices -l
& $adb shell dumpsys webviewupdate | Select-String "Current WebView package"
& $adb logcat -c
& $adb shell am force-stop com.local.offlinereplica
& $adb shell am start -n com.local.offlinereplica/.MainActivity
Start-Sleep -Seconds 25
& $adb logcat | Select-String "chromium|CONSOLE|AndroidRuntime|offlinereplica"
```

重点看：
- `chromium: [INFO:CONSOLE(...)]` 里的报错（例如 `Uncaught`、`找不到`、`Failed to load resource`）；
- `AndroidRuntime` 崩溃栈；
- WebView 版本（太低就换设备或换 WebView）。

### D. 进 APK 内 WebView 调试（真机能连 USB 时）

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
$sock = (& $adb shell "cat /proc/net/unix | grep webview_devtools") -join ' '   # 取 @webview_devtools_remote_<pid>
& $adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>
node tools\verify-apk-webview.mjs
```

`verify-apk-webview.mjs` 会导航到 `?mode=demo` 并输出 `StreetUltimate.snapshot()`，能直接看到 JS 层是否还在动。

## 排查时顺手记录

- 手机型号 / Android 版本 / WebView 版本（`dumpsys webviewupdate`）；
- 剩余存储（`adb shell df -h /data`）；
- 装的是精简还是完整包、是否先卸载了旧版；
- 卡住时点屏幕有没有反应、有没有声音、有没有看到任何 UI 元素；
- 冷启动 vs 二次启动是否不同。
