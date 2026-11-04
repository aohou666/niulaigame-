"""Build an H018 workflow revision from a validated base + a prompt JSON file.

usage: py h018_build_revision.py <base-workflow.json> <prompts.json> <revisionTag>

Only the two prompt strings and every output prefix change; the graph, links, subgraphs and all
other widget values stay identical to the base revision.
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(r"C:\Users\dongdong\Documents\ChatGPT\安装")
JOB = "H018-ATK-V01-L01-S01"

base = json.loads(Path(sys.argv[1]).read_text("utf-8"))
prompts = json.loads(Path(sys.argv[2]).read_text("utf-8"))
tag = sys.argv[3]

wf = json.loads(json.dumps(base))
nodes = {n["id"]: n for n in wf["nodes"]}
before = {i: json.dumps(n.get("widgets_values"), ensure_ascii=False) for i, n in nodes.items()}

nodes[108]["widgets_values"] = [prompts["imagePrompt"]]
nodes[109]["widgets_values"] = [prompts["videoPrompt"]]
assert nodes[106]["widgets_values"] == [True] and nodes[107]["widgets_values"] == [True]
assert nodes[89]["widgets_values"][0] == 3

prefix = f"street_jobs/{JOB}/{tag}"
for nid, sub in ((24, "base"), (36, "purple"), (37, "cyan"), (38, "red")):
    nodes[nid]["widgets_values"][17] = f"{prefix}/{sub}"
nodes[177]["widgets_values"][1:] = [f"FX/{prefix}/atlas", f"FX/{prefix}/atlas_purple",
                                    f"FX/{prefix}/atlas_cyan", f"FX/{prefix}/atlas_red"]
nodes[178]["widgets_values"][1] = f"FX/{prefix}/atlas_green"
for nid in (39, 40, 41, 85, 134):
    v = nodes[nid].get("widgets_values")
    if isinstance(v, dict):
        v["filename_prefix"] = f"FX/{prefix}/preview_{nid}"
        v.pop("videopreview", None)

wf["extra"]["street_handoff"]["revision"] = tag
wf["extra"]["street_handoff"]["promptMode"] = "manual-handwritten"
wf["extra"]["street_handoff"]["promptNote"] = prompts.get("note", "")

after = {i: json.dumps(n.get("widgets_values"), ensure_ascii=False) for i, n in nodes.items()}
changed = sorted(i for i in nodes if before[i] != after[i])
allowed = {108, 109, 24, 36, 37, 38, 39, 40, 41, 85, 134, 177, 178}
assert set(changed) <= allowed, changed

outdir = ROOT / f"outputs/_handoff-verify/h018-rev-{tag}"
outdir.mkdir(parents=True, exist_ok=True)
out = outdir / "workflow.json"
out.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"out": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                  "changedNodes": changed,
                  "imagePromptChars": len(prompts["imagePrompt"]),
                  "videoPromptChars": len(prompts["videoPrompt"])}, ensure_ascii=False))
