# 本地工作台迁移

## 动作调参台

`XSXB-Frame-Tuner-Lite-Portable` 从本机微信目录中的 `XSXB-Frame-Tuner-Lite-Portable-Windows-x64.zip` 恢复。原包 SHA-256：`7179cb0ec0d95707e0b7eec546f5de106b37df843290a4eec564c170535ca31e`。

GitHub 仓库保存源码；Release `migration-20261013` 保存完整便携 ZIP，包含 Node.js、Lite 项目参数及 66 帧素材。将整个便携目录解压到可写位置，双击 `Start_XSXB_Lite.cmd`，打开 `http://127.0.0.1:5180/`。参数在 `data/lite`，素材在 `workspace/lite`；结束时在命令窗口按 Ctrl+C。

恢复后已通过 `tools/self_test.js` 和 Lite 项目校验，结果为 1 个 profile、1 个动画、66 帧、0 个警告。原包包含 MIT 许可证，原项目地址见内部 README。

## 绿幕导帧工作台

旧版可能位于旧电脑 G 盘，本机没有找回。按用户授权，在 `greenscreen-frame-studio` 中基于原作者 MIT 开源版本制作新改版：橡皮擦、撤销上一笔、恢复本帧擦除、透明 PNG，以及逐帧移动、缩放和旋转。

完整便携包名 `Greenscreen-Frame-Studio-Eraser-Portable-Windows-x64.zip`，解压后双击 `Start_Greenscreen.cmd`，访问 `http://127.0.0.1:8791/`。无需 npm 或安装 Node.js。

换电脑前使用“导出项目”，携带 `.green-project.json`；在新电脑“导入项目”恢复原图、擦除和位置参数。浏览器“保存”不会随程序文件夹迁移。

已用实际浏览器和 PNG 像素验证抠绿、擦除、移动/缩放/旋转、撤销，以及项目导出后重新导入；重新导入后的 PNG 与之前逐像素相同。详细使用方法和作者链接见工作台 README。
