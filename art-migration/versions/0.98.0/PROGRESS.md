# v0.98.0 进度（2026-11-02，DSH 接手后第 1 轮）

## 已完成

1. **4 个共享主动技能 FX 容器接入生产**
   - `local_game/street-art-data.js`：容器 6 → 10，version 0.97.0 → 0.98.0。
   - 新增（normal/EZ 各一）：
     - `common_newskill_simayi_01_1_bin` → `native-fx/common_newskill_simayi_01_1-walnut-flight-c58cf22e06d7f7f6.bin`（15 纹理 / 62 帧 @24）
     - `common_newskill_simayi_01_1_ez_bin` → `..._ez-walnut-flight-54dee81791501554.bin`
     - `common_newskill_simayi_01_2_bin` → `...-walnut-slam-5d51a3800b6d7cec.bin`（16 纹理 / 16 帧 @24）
     - `common_newskill_simayi_01_2_ez_bin` → `..._ez-walnut-slam-9299f9ed9dbdeafd.bin`
   - 目标 .bin 原已在 `local_game/assets/street/skins/100201/native-fx/`，逐字节 SHA 与候选一致。

2. **生产绑定运行验证通过**（`active-fx-production.json`）
   - 直接加载生产 `street-art-data.js`（无 route 覆盖），4 个 alias 全部安装。
   - 4 个容器各自跑完整 native 循环：62/62/16/16 帧、24fps、回调 1 次、完成 1 次、纹理 15/15/16/16。
   - 每模型 0/中/末帧截图已存 `versions/0.98.0/active-fx-*.png`。

3. **原生实例证据**：`active-fx-instantiation.json`（pass、resourceDigests、manualReview=approved-complete-native-loop），四个容器均指向它。

4. **台账**
   - `assets.jsonl`：4 行 `pending → complete`，写入 replacement / generation / runtimeVerification / visualReview / completionScope。
   - `packed-art.jsonl` **有意不动**：按 v95–v97 约定，packed 行保持原始打包台账，`street_review.py` 从未 complete 行 + verified container 推导 confirmedRegions；若把行翻成 complete，review 会跳过它们、丢失已确认区域计数。

5. **静态门禁**
   - `street_art_verify.verify()`：errors 0，images 97，containers 10，四容器 `completeContainerReplaced=true`。
   - 数据 JS 可被 Node vm 解析；CRLF 保持；资源数 97 未变。

## 明确未做 / 下一步

- **ground2（common_newskill_simayi_01_3 normal/EZ）未接入**：候选 `actualBattleDependencyProven=false`，实际消费关系未证明；按交接要求先做依赖审计，不因“原生纹理通过”就绑定。
- **v98 全量门禁未跑**：双85、1876 动作、14FX、125 属性、6 缓存、100202 保真、1798 依赖、隔离实战、review.json 尚未生成。
- **未提交**：等全量门禁通过后按 v96/v97/v98 批次精确提交、推送、核远端 SHA。
- 主存档未改（SHA 见每轮记录）；隔离 8794 服务仅用于渲染验证，未写存档。

## 证据清单

| 文件 | 用途 |
| --- | --- |
| `versions/0.98.0/active-fx-production.json` | 生产绑定运行报告 |
| `versions/0.98.0/active-fx-instantiation.json` | 原生循环实例证据（container 校验引用） |
| `versions/0.98.0/artverify.json` | street_art_verify 全量输出 |
| `versions/0.98.0/active-fx-*.png` | 4 容器 × 3 帧截图 |
| `outputs/street-reskin/v098/` | 复跑脚本与备份（gitignored） |
