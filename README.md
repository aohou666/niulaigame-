# 离谱街区 · 离线游戏换皮工程

进行中的 2.5D 半写实、半卡通街区风改造。当前已发布阶段性版本 v0.21–v0.23；**全量换皮尚未完成**，实际覆盖和缺口以 [工作记录](art-migration/WORKLOG.md) 与逐版 `review.json` 为准。

已接入 85 名角色的 841 处图片引用、5,201 帧待机共享纹理和街区战斗背景。125 条皮肤配置目前仅绑定对应角色身份图，不能视为 125 套独立新皮肤。多数攻击、受击、死亡、UI、建筑和道具仍在替换。

## 恢复运行环境

1. 克隆本仓库 `main`。
2. 从 [v0.23.0 Release](https://github.com/aohou666/oldniulai/releases/tag/street-v0.23.0) 下载 `original-game-resources.zip`，解压到仓库根目录。
3. 使用 Python 3.10 或更高版本运行：

   ```powershell
   python local_game/offline_server.py --save pc_server_data/offline-replica-save.json
   ```

4. 浏览器打开 `http://127.0.0.1:8787/offline-launcher.html`。

资源包 SHA-256：`73269000c2bdd694fbdf69c88fc70ee869b1d125e5037b66bc31cd2aabd69b4a`。原始运行资源包含 13,786 个文件；新待机图集与本轮已接入美术在 Git 中。资源包不含存档或凭据。原始 3.15 GB 待机 PNG 输入仍在本地保留，用于重新生成图集；运行已发布版本不需要这些输入帧。

## 验证和美术来源

- `art-migration/assets.jsonl`：原始资源逐文件台账。
- `art-migration/packed-art.jsonl`：打包纹理区域及动画台账。
- `art-migration/versions/`：每版资源、角色和实际运行复查结果。
- `art-migration/generation/`：本地 Qwen Image 2.1、MiniMax H3 的实际工作流、状态与失败记录；原始模型输出不直接作为已完成美术发布。
- `art-migration/prompts/`：官方图像生成及其他美术提示词记录。
- `local_game/assets/street/`：已接入或待接入的本轮资源；是否完成仍以逐项复查记录为准。

v0.23 的 85/85 原生角色详情和技能栏检查通过；同样六名我方角色的估算解码纹理存储降低 84.34%。测试不构成所有玩法无 bug 或所有设备永不卡顿的保证。
