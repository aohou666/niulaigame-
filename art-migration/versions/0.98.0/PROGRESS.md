# v0.98.0 交付记录（2026-11-02）

## 版本状态：已提交并推送

- 版本提交：`980eab63fdc08aaa6123a23c1e6aac220db9187d`
- 远端 `delivery/main` 与 `delivery/codex/street-reskin-20261029`：`980eab63…`（96/97/98 批次已交付）
- 主存档 `pc_server_data/offline-replica-save.json`：SHA-256 `b8cf849c3667a890645b66c08d155e4d2a23fe6d717b756a1d413b40f035e050`，测试前后一致
- 测试服务：8787/8794 均使用存档副本，测试结束已停止

## 已完成

1. **4 个共享主动技能 FX 容器接入生产**
   - `street-art-data.js` 容器 6→10，version 0.98.0。
   - `common_newskill_simayi_01_1`（15 纹理 / 62@24）与 `01_2`（16 纹理 / 16@24），normal/EZ 各一。
   - 目标 .bin 逐字节 SHA 与候选一致。

2. **生产实例验证**（`active-fx-production.json` / `active-fx-instantiation.json`）
   - 无 route 覆盖，4 alias 全部安装、digest 一致；
   - 四容器完整原生循环 62/62/16/16 帧、24fps、回调/完成各 1、纹理 15/15/16/16；
   - 每模型 0/中/末帧截图。

3. **v98 全量门禁**
   - 双85 两套：各 85/85，浏览器/网络/资源错误 0；
   - 1876 base 连续帧、14FX、125 属性、6 缓存、100202 fidelity：全通过；
   - `street_art_verify` errors 0；`review.json` bindingErrors 0 / artErrors 0；
   - `generatedRuntimeGitTracking` pass，1802 项，missing/binaryDiff 0；
   - verifiedPhysicalRegions 384 / verifiedPhysicalAnimations 24（较 v97 +62 / +2）；
   - 单资源 complete 69→73；完整角色 0/85、独立皮肤 0/125（未变）。

## 明确边界

- **ground2（`common_newskill_simayi_01_3` normal/EZ，2 纹理）不接入**：依赖审计已证明它只出现在 `default.res` 清单，
  `g_skill` 的 `common_newskill_simayi_01_jn` 只引用 01_1/01_2，无任何技能组或代码消费 01_3 → 孤儿资源；
  候选保留、不计入必需美术。证据 `skin-migration/100201/active-skill-native/dependency-audit.json`。
- **`packed-art.jsonl` 未翻状态**：按 v95–v97 约定保持原始打包台账；`street_review.py` 从未 complete 行
  与 verified container 推导 confirmedRegions，翻成 complete 会让 review 跳过这些行、丢失已确认区域计数。
- **隔离实战沿用 v97 证据**：v98 容器字节与候选完全相同（targetSha256 一致），
  `native-battle-active31-focused/runtime.json`（SHA `b06a3908…`）仍是实际 BattleAI 证据；
  v98 新增的是生产 alias 的实例证明。release-note 已标注 `reusedNotRerun: true`。
- 不声称 APK/手机/全设备零 bug。

## 证据清单

| 文件 | 用途 |
| --- | --- |
| `review.json` | v98 版本门禁汇总 |
| `release-note.json` | 版本说明与边界 |
| `active-fx-production.json` | 生产绑定运行报告 |
| `active-fx-instantiation.json` | 原生循环实例证据 |
| `artverify.json` | 容器/资源校验 |
| `all-heroes-runtime.json` / `base-heroes-runtime.json` | 双85 |
| `body-roster.json` | 1876 帧 |
| `effects-roster-runtime.json` | 14FX |
| `skin-attributes-native.json`(+png) | 125 属性 |
| `effect-idle-cache.json` | 6 缓存 |
| `independent-skin-fidelity.json` | 100201/100202 保真 |
| `git-tracking.json` | index 依赖 |

## 下一阶段

1. `common_newskill_simayi_01_3` 实际消费审计（g_skill/技能配置引用链），再决定是否接入。
2. 技能横幅、剩余共享 FX。
3. 按 85 角色拆批推进；每 3 个实质版本推 delivery/main 并核 SHA。
