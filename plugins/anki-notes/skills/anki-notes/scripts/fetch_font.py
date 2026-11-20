# pyright: basic
"""Fetch an openly licensed web font from npm (@fontsource) as a .woff2 file.

Usage: python3 -I fetch_font.py "<Font Family>" <dest.woff2> [weight]   (weight defaults to 400)

Fontsource packages every Google Fonts family under the SIL Open Font License,
and npm is reachable from the claude.ai sandbox when Google's font servers are
not. Needs `npm` on the PATH (present wherever Claude Code runs). Fetches only
the Latin subset of one weight, about 15-30 KB. Variable and non-Latin fonts
are out of scope.
"""
import asyncio
import os
import re
import shutil
import sys
import tarfile
import tempfile


def slug(family):
    return re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")


def extract(tgz, member, dest):
    with tarfile.open(tgz) as t:
        f = t.extractfile(member)  # KeyError if the weight or subset doesn't exist
        data = f.read()
    with open(dest, "wb") as out:
        out.write(data)


async def fetch_font(family, dest, weight=400):
    fid = slug(family)
    if not fid:
        raise ValueError("empty font family")
    tmp = await asyncio.to_thread(tempfile.mkdtemp)
    try:
        proc = await asyncio.create_subprocess_exec(
            "npm", "pack", f"@fontsource/{fid}", "--pack-destination", tmp, "--silent",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, err = await asyncio.wait_for(proc.communicate(), 120)
        if proc.returncode:
            raise RuntimeError(f"npm pack @fontsource/{fid} failed: {err.decode().strip()[:200]}")
        tgz = os.path.join(tmp, next(n for n in os.listdir(tmp) if n.endswith(".tgz")))
        await asyncio.to_thread(extract, tgz, f"package/files/{fid}-latin-{weight}-normal.woff2", dest)
    except KeyError:
        raise RuntimeError(f"{family} has no latin {weight} file in Fontsource") from None
    finally:
        await asyncio.to_thread(shutil.rmtree, tmp, True)
    return dest


async def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    weight = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    try:
        print(await fetch_font(sys.argv[1], sys.argv[2], weight))
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        sys.exit(str(e))


if __name__ == "__main__":
    asyncio.run(main())
