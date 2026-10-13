# 新电脑继续开发

本目录为 2026-10-13 的当前工作区快照，包括 v0.19 工程及其后的本地修改。源码状态与已有 v0.19 APK 不完全一致；迁移不代表后续战斗修复已全部完成验收。

## 完整迁移包

下载 GitHub Release `migration-20261013` 中的 `game-development-20261013.zip`，解压到固定目录，例如 `D:\Projects\OfflineGame`。完整包包含源码、完整游戏资源、便携 Python、当前电脑存档和后台配置、Git 历史包。

双击 `start-desktop.cmd` 打开电脑游戏，双击 `start-admin.cmd` 打开编辑后台。浏览器地址为 `http://127.0.0.1:8787`；存档和后台配置在 `pc_server_data`。关闭服务可在任务管理器结束该目录启动的 Python 进程。

安装 Git 后，在项目根目录运行以下命令恢复可继续提交的仓库：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore-git.ps1
git status
```

使用 Codex 或编辑器打开解压后的项目根目录。GitHub 普通源码 ZIP 不包含 `local_game/resource`，首次迁移应使用完整开发 ZIP。

## 构建 Android APK

安装 Android Studio，通过 SDK Manager 安装 Android SDK Platform 35、Build Tools 和 Platform Tools。脚本会自动找到当前用户的 SDK；自定义安装目录请设置 `ANDROID_HOME`。JDK 自动使用 Android Studio 的 `jbr`，也可设置 `JAVA_HOME`。

```powershell
.\android_offline_shell\build-and-install.ps1 -BuildOnly
```

首次构建需要联网，脚本下载并校验 Gradle 8.9，Gradle 下载构建依赖。之后可添加 `-Offline` 使用缓存。生成 APK 在 `android_offline_shell/app/build/outputs/apk/debug/app-debug.apk`。Android SDK、模拟器和构建缓存需在新电脑安装，未打包。

## 校验与保存

迁移 ZIP 附有 SHA-256 文件。ZIP 内 `migration-manifest.json` 记录每个文件的路径、大小和 SHA-256；可用 `tools/verify-migration.py` 验证解压后的文件。存档属于迁移时的快照，后续新电脑修改保存在新电脑本地。

GitHub 仓库保存源码、脚本和文档；完整资源与开发包存放在 Releases。旧原包和逆向分析缓存保留在旧电脑，继续修改当前离线工程不依赖它们。
