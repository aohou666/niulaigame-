# 启动、登录和 Logo 换皮参考

## 01_启动与加载

共 22 张图片，来自游戏的 `resource/loading` 目录。

- `common_img_jiemiandi_360.jpg`：大尺寸启动/进入界面底图。
- `login02_bg.jpg` 至 `login13_bg.jpg`：轮换使用的竖屏加载或登录背景，通常为 960×1560。
- `login01.jpg`、`login02.png` 至 `login05.png`：加载界面的前景插画或覆盖层。
- `common_img_jiemiandi.png`、`star1.png`：加载界面小元素。
- `fenxiang.jpg`、`wanba_img_beijingtu.jpg`：分享/渠道相关背景，可按需要处理。

## 02_登录背景

游戏内主要背景：

- `denglu_img_beijing.jpg`
- `denglu_img_beijing2.jpg`
- `common_denglu_bg_01.jpg`
- `common_denglu_bg_02.png`

另外两张以 `sdk_` 开头的是渠道授权/登录界面背景。若继续使用原渠道 SDK，也建议一并换掉。

## 03_Logo与图标

- `game_denglu_img_logo.png`：游戏登录界面主 Logo，优先替换。
- `app_ic_launcher.png`：手机桌面安装图标。
- `sdk_icefox_login_icon_logo.png`：渠道登录框 Logo。
- `sdk_floatbutton_logo.png`：渠道悬浮球 Logo。

## 制作要求

- 保持文件名、像素尺寸和格式不变。
- PNG 必须保留透明通道。
- JPG 建议使用高质量导出，避免文字与线条出现压缩噪点。
- 新 Logo 尽量保持原图透明边距，避免游戏内缩放后偏移。
