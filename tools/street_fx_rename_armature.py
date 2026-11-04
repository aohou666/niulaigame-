"""Rename the DragonBones data/armature/action name inside a packed FX container to a new key.

Layout of chunk 0 (skeleton): 'DBDT' + 4 bytes + uint32 payloadLength + JSON payload + binary tail.
Only the three name occurrences inside the JSON payload change; the DBDT prefix (except the length),
the binary tail, the atlas chunk, the image chunk and the 12-byte bundle header stay byte-identical.

Renaming is required because DBPlayer.init(dbName) derives the armature and action name from dbName;
a candidate that keeps the original armature name would not resolve under its new resource key.
"""
import argparse, hashlib, json, struct, zlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from street_packed_inventory import decode


def sha(b): return hashlib.sha256(b).hexdigest()


def split(blob):
    assert blob[:3] == bytes([219, 189, 30]) and blob[6] == 0, "only audited PNG DB bundles"
    parts, pos = [], 12
    for _ in range(3):
        n = struct.unpack_from("<I", blob, pos)[0]; pos += 4
        parts.append(blob[pos:pos + n]); pos += n
    assert pos == len(blob), "trailing data"
    return parts


def raw(blob, part):
    return zlib.decompress(part, -15) if blob[4] else part


def pack(blob, part):
    if not blob[4]:
        return part
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return c.compress(part) + c.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--atlas-name", required=False, default=None,
                    help="texture-atlas registration name; must equal the resource dbName "
                         "(key for the normal bin, key+'_ez' for the ez bin). Defaults to --new.")
    ap.add_argument("--receipt", required=True)
    a = ap.parse_args()

    src, dst = Path(a.input), Path(a.output)
    assert not dst.exists(), "use a new output path"
    blob = src.read_bytes()
    parts = split(blob)
    skel = raw(blob, parts[0])
    assert skel[:4] == b"DBDT", skel[:4]
    size = struct.unpack_from("<I", skel, 8)[0]
    prefix, payload, tail = skel[:12], skel[12:12 + size], skel[12 + size:]
    assert len(payload) == size

    old, new = a.old.encode(), a.new.encode()
    # The EZ container's DATA name already carries the "_ez" postfix while armature/action do not,
    # so replace the longer token first and then the bare one; both end up as the target key.
    tokens = [old + b"_ez", old]
    replaced = {}
    text = payload
    for tok in tokens:
        c = text.count(tok)
        if c:
            replaced[tok.decode()] = c
            text = text.replace(tok, new)
    assert sum(replaced.values()) >= 2, f"expected data/armature/action names, got {replaced}"
    assert new not in payload, "target name already present"

    def normalise(obj):
        """All three name slots -> placeholder, so the rest can be deep-compared."""
        import copy
        o = copy.deepcopy(obj)
        o["name"] = "<NAME>"
        for arm in o.get("armature", []):
            arm["name"] = "<NAME>"
            for an in arm.get("animation", []):
                an["name"] = "<NAME>"
            for an in arm.get("defaultActions", []) or []:
                if isinstance(an, dict) and "name" in an:
                    an["name"] = "<NAME>"
        return o

    before = json.loads(payload)
    after = json.loads(text)
    assert normalise(after) == normalise(before), "JSON changed beyond the name rewrite"
    assert after["name"] == a.new
    assert after["armature"][0]["name"] == a.new
    assert after["armature"][0]["animation"][0]["name"] == a.new
    for an in after["armature"][0].get("defaultActions", []) or []:
        if isinstance(an, dict) and "name" in an:
            assert an["name"] == a.new, an["name"]

    new_payload = text
    # The binary tail that follows the JSON payload is read as typed arrays, so the tail must stay
    # 8-byte aligned. Pad the JSON with trailing spaces (legal JSON whitespace) before the tail.
    pad = (-(12 + len(new_payload))) % 8
    if pad:
        new_payload = new_payload + b" " * pad

    new_skel = prefix[:8] + struct.pack("<I", len(new_payload)) + new_payload + tail

    # The texture atlas must be registered under the SAME name as the DragonBones data, because the
    # factory resolves textures with BaseFactory._getTextureData(dragonBonesName, textureName).
    atlas_name = a.atlas_name or a.new
    atlas_json = json.loads(raw(blob, parts[1]))
    atlas_before = json.loads(json.dumps(atlas_json))
    prev_name = atlas_json.get("name")
    prev_image_path = atlas_json.get("imagePath")
    atlas_json["name"] = atlas_name
    if "imagePath" in atlas_json:
        atlas_json["imagePath"] = atlas_name + "_tex.png"
    atlas_bytes = json.dumps(atlas_json, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # prove the atlas only changed in those two fields
    restored_atlas = dict(atlas_json)
    restored_atlas["name"] = prev_name
    if "imagePath" in atlas_json:
        restored_atlas["imagePath"] = prev_image_path
    assert restored_atlas == atlas_before, "atlas JSON changed beyond name/imagePath"

    out = blob[:12] + b"".join(struct.pack("<I", len(p)) + p
                               for p in [pack(blob, new_skel), pack(blob, atlas_bytes), parts[2]])
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(out)

    d = decode(dst)
    assert d["skeleton"]["armature"][0]["name"] == a.new
    assert d["skeleton"]["armature"][0]["animation"][0]["name"] == a.new
    assert d["skeleton"]["name"] == a.new
    assert d["atlas"]["name"] == atlas_name, d["atlas"]["name"]
    assert d["atlas"]["SubTexture"] == atlas_before["SubTexture"]
    assert d["image"] == raw(blob, parts[2])
    new_parts = split(out)
    assert out[:12] == blob[:12], "bundle header changed"
    assert new_parts[2] == parts[2], "image chunk changed"

    rec = {
        "inputPath": str(src), "inputSha256": sha(blob),
        "outputPath": str(dst), "outputSha256": sha(out),
        "renamedFrom": a.old, "renamedTo": a.new, "replacedTokens": replaced,
        "occurrencesReplaced": sum(replaced.values()),
        "skeletonPayloadBytes": [len(payload), len(new_payload)],
        "binaryTailByteIdentical": True,
        "atlasNameFrom": prev_name, "atlasNameTo": atlas_name,
        "atlasSubTextureIdentical": True,
        "imageChunkByteIdentical": True, "bundleHeaderByteIdentical": True,
        "jsonIdenticalModuloName": True,
        "armatureName": d["skeleton"]["armature"][0]["name"],
        "animationName": d["skeleton"]["armature"][0]["animation"][0]["name"],
        "dataName": d["skeleton"]["name"],
        "regions": len(d["atlas"]["SubTexture"]),
        "frames": d["skeleton"]["armature"][0]["animation"][0].get("duration"),
    }
    Path(a.receipt).write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
