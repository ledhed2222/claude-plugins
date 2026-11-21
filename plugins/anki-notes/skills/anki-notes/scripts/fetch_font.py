# pyright: basic
"""Fetch an openly licensed web font from npm (@fontsource) as .woff2 files.

Usage:
  python3 -I fetch_font.py --info "<Font Family>"
      category (serif, sans-serif, monospace, display, handwriting), subsets, weights, styles
  python3 -I fetch_font.py "<Font Family>" <out dir> [--subsets latin,cyrillic] [--weights 400,700] [--italic]

Fontsource packages every Google Fonts family under the SIL Open Font License,
and npm is reachable from the claude.ai sandbox when Google's font servers are
not. Needs `npm` on the PATH (present wherever Claude Code runs).

Each file is one subset (alphabet) x weight x style, named
_<family>-<subset>-<weight>[-italic].woff2; the leading _ keeps Anki's Check
Media from deleting it. Each comes with its unicode-range, so a device only
loads the subsets a card actually uses. Standard library only (asyncio).
"""
import asyncio
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile


class FontError(Exception):
    pass


def slug(family):
    return re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")


async def _pack(family, tmp):
    fid = slug(family)
    if not fid:
        raise FontError("empty font family")
    proc = await asyncio.create_subprocess_exec(
        "npm", "pack", f"@fontsource/{fid}", "--pack-destination", tmp, "--silent",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        _, err = await asyncio.wait_for(proc.communicate(), 120)
    except asyncio.TimeoutError:
        proc.kill()
        raise FontError(f"npm pack @fontsource/{fid} timed out") from None
    if proc.returncode:
        raise FontError(f"no Fontsource package for {family!r} (npm pack @fontsource/{fid} failed)")
    return os.path.join(tmp, next(n for n in os.listdir(tmp) if n.endswith(".tgz")))


def _read_json(tar, name):
    f = tar.extractfile(f"package/{name}")
    return json.loads(f.read()) if f else {}


def _info(tgz):
    with tarfile.open(tgz) as t:
        meta, ranges = _read_json(t, "metadata.json"), _read_json(t, "unicode.json")
    return {"family": meta.get("family"), "category": meta.get("category"), "subsets": meta.get("subsets", []),
            "weights": meta.get("weights", []), "styles": meta.get("styles", []), "unicode": ranges}


def plan_files(info, subsets, weights, italic):
    """Which files to take from the package, or FontError naming what's missing."""
    missing = [s for s in subsets if s not in info["subsets"]]
    if missing:
        raise FontError(f"{info['family']} lacks {', '.join(missing)} (has {', '.join(info['subsets'])})")
    absent = [w for w in weights if w not in info["weights"]]
    if absent:
        raise FontError(f"{info['family']} lacks weight {absent} (has {info['weights']})")
    if italic and "italic" not in info["styles"]:
        raise FontError(f"{info['family']} has no italic")
    fid = slug(info["family"])
    styles = ["normal", "italic"] if italic else ["normal"]
    return [{"member": f"package/files/{fid}-{s}-{w}-{st}.woff2",
             "filename": f"_{fid}-{s}-{w}{'-italic' if st == 'italic' else ''}.woff2",
             "family": info["family"], "subset": s, "weight": w, "style": st,
             "unicode_range": info["unicode"].get(s, "")}
            for s in subsets for w in weights for st in styles]


def _extract(tgz, files, out):
    with tarfile.open(tgz) as t:
        for f in files:
            data = t.extractfile(f["member"]).read()
            with open(os.path.join(out, f["filename"]), "wb") as fh:
                fh.write(data)


async def font_info(family):
    tmp = await asyncio.to_thread(tempfile.mkdtemp)
    try:
        return await asyncio.to_thread(_info, await _pack(family, tmp))
    finally:
        await asyncio.to_thread(shutil.rmtree, tmp, True)


async def fetch_font(family, out, subsets=("latin",), weights=(400,), italic=False):
    """Fetch the files into `out`. Returns their descriptions (filename, path, subset,
    weight, style, unicode_range, category). Raises FontError before writing anything
    if the font lacks a requested subset, weight or italic."""
    tmp = await asyncio.to_thread(tempfile.mkdtemp)
    try:
        tgz = await _pack(family, tmp)
        info = await asyncio.to_thread(_info, tgz)
        files = plan_files(info, list(subsets), list(weights), italic)
        await asyncio.to_thread(os.makedirs, out, exist_ok=True)
        await asyncio.to_thread(_extract, tgz, files, out)
    except KeyError as e:
        raise FontError(f"{family}: file missing from package ({e})") from None
    finally:
        await asyncio.to_thread(shutil.rmtree, tmp, True)
    for f in files:
        f.pop("member")
        f["path"] = os.path.abspath(os.path.join(out, f["filename"]))
        f["category"] = info["category"]
    return files


def _arg(args, name, default):
    return args[args.index(name) + 1] if name in args else default


async def main():
    args = sys.argv[1:]
    try:
        if args[:1] == ["--info"] and len(args) == 2:
            info = await font_info(args[1])
            info.pop("unicode")
            print(json.dumps(info))
        elif len(args) >= 2:
            files = await fetch_font(args[0], args[1],
                                     _arg(args, "--subsets", "latin").split(","),
                                     [int(w) for w in _arg(args, "--weights", "400").split(",")],
                                     "--italic" in args)
            print(json.dumps(files, indent=1))
        else:
            sys.exit(__doc__)
    except FontError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    asyncio.run(main())
