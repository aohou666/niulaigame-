# 工作区上下文（精简入口）

## 当前可交付版本

- 2026-10-13 迁移说明：`MIGRATION.md`；完整开发包发布到 Release `migration-20261013`。
- 当前工程版本：0.19.0，包含已有 v0.19 APK 之后的本地修改；迁移快照不等于新增修复全部验收。
- 此前已发布安装包：`离线复刻测试-v0.18-原包界面与世界状态修复版.apk`
- GitHub Release：<https://github.com/houguangdong104-beep/-/releases/tag/v0.18>
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
- 本地对话开始时先以用户本轮限定范围为准，再按需读取对应文件；不要把历史任务自动并入当前修改范围。
- 历史截图和旧 APK 只用于发布归档，不作为日常上下文。
- Git 保存源码、脚本和小型文档；`local_game/resource/` 等大资源通过 GitHub Releases 开发迁移包管理。

## 发布与本地保留策略

- 上传全部根目录版本化 APK 后，核对 GitHub Release 资产的文件名和大小。
- 核验通过后，本地仅保留最新 APK 与原始包 `apk_analysis/package_test/original.apk`。
- 不删除源码、资源、说明文档或用户提供的原始包。

