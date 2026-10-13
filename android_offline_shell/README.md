# 离线复刻 Android 测试壳

这是独立于原包、Icefox 和渠道登录 SDK 的原生 Android WebView 壳。游戏资源直接打包在 APK 内，并由应用内置的本机 HTTP 服务读取；安装后运行游戏不需要 USB、电脑资源服务或网络。

## 构建

```powershell
.\build-and-install.ps1 -BuildOnly
```

输出：`app\build\outputs\apk\debug\app-debug.apk`。当前应用版本为 0.13.0（versionCode 13）。

## 安装并测试

1. 手机开启开发者选项和 USB 调试，并允许本电脑调试。
2. 在此目录运行：

```powershell
.\build-and-install.ps1
```

脚本会构建包含全部资源的 APK、安装并启动应用。USB 只用于执行安装命令，安装后可以拔线运行。

0.9.0 增加电脑服务器模式。应用收到 `startUrl=http://127.0.0.1:8788/...` 时不会启动包内服务器，而是通过 ADB 反向端口读取电脑端资源和存档；普通点击应用图标时仍可使用包内资源独立运行。

项目根目录的 `start-virtual-machine.ps1` 会启动 `OfflineReplica_API35` 虚拟机、检查或安装当前 APK、连接电脑服务器并打开指定模式。
