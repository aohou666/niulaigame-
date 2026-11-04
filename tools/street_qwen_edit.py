"""Drive the user's 'Qwen Image 2.1 文生/图像编辑一体化' workflow for one effect.

Pipeline per effect:
  1. build a 4x2 contact sheet of the effect's eight native regions (uniform cells)
  2. feed it as the workflow's base/reference image + a character-specific restyle prompt
  3. the prompt optimizer branch is bypassed so the wording is deterministic
  4. submit, wait, collect the result
"""
import argparse, hashlib, io, json, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

API = "http://127.0.0.1:8188"
COMFY = Path(r"G:\comfyqiuye\ComfyUI-aki-v3.2\ComfyUI")
ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
WF = COMFY / "user/default/workflows/Qwen Image 2.1 文生、图像编辑一体化.json"
WORK = ROOT / "outputs/_handoff-verify/qwen-edit"
WORK.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode


def contact_sheet(bin_path: Path, cell=(512, 512), cols=4) -> Image.Image:
    d = decode(bin_path)
    atlas = Image.open(io.BytesIO(d["image"])).convert("RGBA")
    regions = d["atlas"]["SubTexture"]
    rows = (len(regions) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell[0], rows * cell[1]), (0, 0, 0, 255))
    for i, r in enumerate(regions):
        box = (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])
        sprite = atlas.crop(box)
        bg = Image.new("RGBA", sprite.size, (0, 0, 0, 255))
        bg.alpha_composite(sprite)
        bg = bg.convert("RGB")
        bg.thumbnail((cell[0] - 8, cell[1] - 8), Image.Resampling.LANCZOS)
        x = (i % cols) * cell[0] + (cell[0] - bg.width) // 2
        y = (i // cols) * cell[1] + (cell[1] - bg.height) // 2
        sheet.paste(bg, (x, y))
    return sheet.convert("RGB")


def req(path, data=None, timeout=120):
    body = None if data is None else json.dumps(data).encode()
    r = urllib.request.Request(API + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--tag", default="t1")
    args = ap.parse_args()

    plan = json.loads((ROOT / "outputs/fx-handoff-20261102/plan.json").read_text("utf-8-sig"))
    job = next(j for j in plan["jobs"] if j["jobId"] == args.job)
    src_rel = job["normal"].get("path") or job["normal"]["candidates"][0]
    src = ROOT / src_rel

    sheet = contact_sheet(src)
    img_name = f"fxsheet_{args.tag}.png"
    sheet.save(COMFY / "input" / img_name)
    print(f"sheet {sheet.size} -> {img_name}")

    wf = json.loads(WF.read_text("utf-8-sig"))
    nodes = {n["id"]: n for n in wf["nodes"]}
    # base image drives both the reference and the output size
    nodes[193]["widgets_values"][0] = f"{img_name} [input]"
    nodes[38]["widgets_values"][0] = f"fx_edit/{args.tag}"
    # bypass the prompt optimizer: cut its link into the encoder and write the prompt directly
    enc = nodes[118]
    for inp in enc.get("inputs", []) or []:
        if inp.get("name") == "prompt" and inp.get("link") is not None:
            lid = inp["link"]
            row = next((l for l in wf["links"] if l[0] == lid), None)
            if row:
                src_id, src_slot = row[1], row[2]
                src_node = nodes.get(src_id)
                if src_node:
                    outs = src_node.get("outputs") or []
                    if 0 <= src_slot < len(outs):
                        outs[src_slot]["links"] = [x for x in (outs[src_slot].get("links") or []) if x != lid]
            wf["links"] = [l for l in wf["links"] if l[0] != lid]
            inp["link"] = None
    enc["widgets_values"][0] = args.prompt

    out_wf = WORK / f"{args.tag}-workflow.json"
    out_wf.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched workflow:", out_wf)

    api_out = WORK / f"{args.tag}-api.json"
    node_bin = "C:/Users/dongdong/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/node/bin/node.exe"
    r = subprocess.run([node_bin, str(ROOT / "outputs/_handoff-verify/export_api.mjs"), str(out_wf), str(api_out)],
                       capture_output=True, text=True, cwd=str(ROOT))
    print(r.stdout.strip()[:400], r.stderr.strip()[:300])
    if not api_out.exists():
        raise SystemExit("API export failed")

    api = json.loads(api_out.read_text("utf-8"))
    q = req("/queue")
    while q.get("queue_running") or q.get("queue_pending"):
        time.sleep(3); q = req("/queue")
    resp = req("/prompt", {"prompt": api, "client_id": "qwen-edit-batch"})
    pid = resp["prompt_id"]
    print("queued", pid, "| node_errors", resp.get("node_errors"))
    t0 = time.time()
    while time.time() - t0 < 600:
        h = req("/history/" + pid)
        if pid in h:
            e = h[pid]
            st = e.get("status", {})
            if st.get("status_str") != "success":
                print("FAILED", json.dumps(st.get("messages", []))[:600]); break
            for out in e.get("outputs", {}).values():
                for it in out.get("images", []) or []:
                    srcf = COMFY / "output" / it.get("subfolder", "") / it["filename"]
                    dst = WORK / f"{args.tag}-result.png"
                    dst.write_bytes(srcf.read_bytes())
                    print(json.dumps({"result": str(dst), "seconds": round(time.time() - t0, 1)}))
            break
        time.sleep(3)


if __name__ == "__main__":
    main()
