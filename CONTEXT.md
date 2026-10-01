# 工作区上下文（精简入口）

## 当前可交付版本

- 最新安装包：`离线复刻测试-v0.17-五项修复版.apk`
- 原始包：`apk_analysis/package_test/original.apk`
- Android 工程：`android_offline_shell/`
- 游戏资源与本地服务：`local_game/`
- 项目说明：`完整复刻_已知信息与实施方案.md`

## 构建

在 `android_offline_shell/` 中运行：

```powershell
.\build-and-install.ps1 -BuildOnly
```

构建产物位于 `android_offline_shell/app/build/outputs/apk/debug/app-debug.apk`。发布时复制到仓库根目录并使用带版本号的文件名；APK 仅作为 GitHub Release 资产上传，不加入 Git 历史。

## 上下文与性能约束

- 默认只读取本文件以及任务直接相关的源码；不要递归扫描 `.tools/`、`apk_analysis/`、`outputs/`、构建目录或整棵资源树。
- 搜索源码时优先限定到 `android_offline_shell/app/src/`、`local_game/` 或具体文件类型。
- 历史截图和旧 APK 只用于发布归档，不作为日常上下文。
- Git 只保存源码、脚本和小型文档；大文件通过 GitHub Releases 管理。

## 发布与本地保留策略

- 上传全部根目录版本化 APK 后，核对 GitHub Release 资产的文件名和大小。
- 核验通过后，本地仅保留最新 APK 与原始包 `apk_analysis/package_test/original.apk`。
- 不删除源码、资源、说明文档或用户提供的原始包。

