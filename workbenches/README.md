# 本地工作台迁移

## 动作调参台

`XSXB-Frame-Tuner-Lite-Portable` 从本机微信目录中的 `XSXB-Frame-Tuner-Lite-Portable-Windows-x64.zip` 恢复。原包 SHA-256：`7179cb0ec0d95707e0b7eec546f5de106b37df843290a4eec564c170535ca31e`。

GitHub 仓库保存源码；Release `migration-20261013` 保存完整便携 ZIP，包含 Node.js、Lite 项目参数及 66 帧素材。将整个便携目录解压到可写位置，双击 `Start_XSXB_Lite.cmd`，打开 `http://127.0.0.1:5180/`。参数在 `data/lite`，素材在 `workspace/lite`；结束时在命令窗口按 Ctrl+C。

恢复后已通过 `tools/self_test.js` 和 Lite 项目校验，结果为 1 个 profile、1 个动画、66 帧、0 个警告。原包包含 MIT 许可证，原项目地址见内部 README。

## 绿幕导帧工作台

仍在定位，尚未确认目标程序。已找到山海诡录“英雄特效工作台”的 2026-09-24 备份，但它主要用于特效素材抠像和五人战斗编排，目前不作为用户指定的独立动作导帧工作台交付。
