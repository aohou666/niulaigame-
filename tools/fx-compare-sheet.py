"""Compose the 10-character original-vs-reskin comparison sheets from fx-compare-10.mjs frames."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
SRC = ROOT / "art-migration/generation/fx-compare-20261103"
OUT = ROOT / "outputs/street-reskin/preview-20261103/compare10"
FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
FRAME = 260
GAP = 8
MARGIN = 40
LABEL_W = 96
PICK = 6

ENTRIES = [
    ("懂子", "common_skill_caocao_02_1"),
    ("马宝果", "common_skill_guanyu_1_01"),
    ("鸡", "common_skill_pangtong_01_1"),
    ("锤王", "common_skill_pangde_02"),
    ("丧尸牛", "common_skill_zhangbao_02"),
    ("蓝色妖姬", "common_skill_xiahouyuan_01_1"),
    ("机器牛", "common_skill_huangyueying_01"),
    ("驱鬼道长", "common_skill_zhangjiao_baguazhen"),
    ("金龙", "common_shenzhaoyun_2_1"),
    ("虎", "common_skill_zhangliao_1_03"),
]


def font(size):
    return ImageFont.truetype(str(FONT), size)


def coverage(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    return float((np.abs(im - 16).max(axis=2) > 12).mean())


def pick_indices(key):
    cov = [coverage(SRC / f"original-{key}-f{i}.png") for i in range(10)]
    order = sorted(range(10), key=lambda i: cov[i], reverse=True)[:PICK]
    return sorted(order), cov


def main():
    plan = json.loads((ROOT / "outputs/fx-handoff-20261102/plan.json").read_text("utf-8-sig"))
    by_key = {}
    for job in plan["jobs"]:
        by_key.setdefault(job["originalResourceKey"], job)
    OUT.mkdir(parents=True, exist_ok=True)

    f_title = font(22)
    f_label = font(20)
    f_small = font(15)
    f_head = font(30)

    sheets = []
    for part in range(2):
        entries = ENTRIES[part * 5:(part + 1) * 5]
        blocks = []
        for idx, (hero, key) in enumerate(entries):
            job = by_key.get(key) or {}
            slot = job.get("slot", "")
            theme = (job.get("profile") or {}).get("theme", "")
            palette = (job.get("profile") or {}).get("palette", "")
            indices, cov = pick_indices(key)
            rows = {}
            for variant in ("original", "reskin"):
                frames = [Image.open(SRC / f"{variant}-{key}-f{i}.png").convert("RGB").resize((FRAME, FRAME), Image.LANCZOS)
                          for i in indices]
                rows[variant] = frames
            blocks.append((hero, key, slot, theme, palette, rows, cov))
            print(hero, key, indices, [round(c, 2) for c in cov])

        width = MARGIN * 2 + LABEL_W + PICK * FRAME + (PICK - 1) * GAP
        header = 92
        block_h = 48 + 28 + FRAME + 16 + 28 + FRAME + 34
        height = header + len(blocks) * block_h + MARGIN
        sheet = Image.new("RGB", (width, header + len(blocks) * block_h + MARGIN), (16, 20, 26))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, 24), "技能特效换皮 · 10 角色原版 / 换皮后对比", font=f_head, fill=(255, 212, 134))
        draw.text((MARGIN, 62), f"A/B {part + 1}/2 · 每格为同一动画时间点；上排原版，下排换皮后。", font=f_small, fill=(150, 160, 175))

        y = header
        for bi, (hero, key, slot, theme, palette, rows, cov) in enumerate(blocks):
            draw.text((MARGIN, y), f"{part * 5 + bi + 1:02d}  {hero}", font=f_title, fill=(242, 231, 210))
            info = " · ".join(x for x in [slot, theme, palette, key] if x)
            draw.text((MARGIN + 150, y + 3), info, font=f_small, fill=(145, 154, 168))
            y += 44

            for variant, label, color in (("original", "原版", (180, 190, 205)), ("reskin", "换皮后", (255, 180, 120))):
                draw.text((MARGIN, y + 3), label, font=f_label, fill=color)
                x = MARGIN + LABEL_W
                for im in rows[variant]:
                    sheet.paste(im, (x, y))
                    x += FRAME + GAP
                y += FRAME + 18
            y += 26

        path = OUT / f"compare-10-{'AB'[part]}.png"
        sheet.save(path)
        sheets.append(path)
        print("wrote", path, sheet.size)

    # one combined tall sheet for convenience
    ims = [Image.open(p) for p in sheets]
    combined = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims) + 20), (16, 20, 26))
    yy = 0
    for im in ims:
        combined.paste(im, (0, yy))
        yy += im.height + 20
    combined.save(OUT / "compare-10.png")
    print("wrote", OUT / "compare-10.png", combined.size)


if __name__ == "__main__":
    main()
