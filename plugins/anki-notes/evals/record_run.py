# pyright: basic
"""Keep a history of eval runs in history.jsonl, and show what moved.

Usage:
  python3 -I record_run.py add <result.json> [--commit SHA] [--note TEXT]
  python3 -I record_run.py diff [<result.json>]
  python3 -I record_run.py --check

<result.json> is a run's evals/results/<time>/aggregate-result.json, or the
file `claude plugin eval --json <file>` wrote.

add appends one line per run (date, commit, Claude version, cost, arms, per-case
scores) and prints what moved. --commit defaults to HEAD, marked "-dirty" when
the plugin has uncommitted changes, since the run measured the working tree.
diff compares a run, or the last recorded one, with the latest earlier score of
each case: overall on the cases both have, and every case whose score changed.
A case runs 3 times, so a move of 0.33 or less on one case is often noise;
re-run it before acting on it. --check validates the file (CI).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HISTORY = HERE / "history.jsonl"
FIELDS = {"started": str, "commit": str, "claude": str, "cost_usd": (int, float), "partial": bool,
          "arms": str, "runs_per_case": int, "scores": dict, "note": str}


def load():
    if not HISTORY.exists():
        return []
    return [json.loads(l) for l in HISTORY.read_text().splitlines() if l.strip()]


def head_commit():
    git = ["git", "-C", str(HERE)]
    sha = subprocess.run(git + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(git + ["status", "--porcelain", "--", str(HERE.parent)], capture_output=True, text=True).stdout.strip()
    return sha + ("-dirty" if dirty else "")


def entry(result, commit, note):
    cases = result["cases"]
    both = any(c.get("arms", {}).get("without") for c in cases)
    return {
        "started": result["startedAt"],
        "commit": commit,
        "claude": result.get("claudeVersion", ""),
        "cost_usd": round(result.get("costUsd", 0), 2),
        "partial": bool(result.get("partial")),
        "arms": "with+without" if both else "with",
        "runs_per_case": cases[0].get("runsPerCase", 0) if cases else 0,
        "scores": {c["name"]: round(c["aggregates"]["score"], 4) for c in cases},
        "note": note,
    }


def baseline(history):
    """Latest score of each case across the given runs."""
    out = {}
    for h in history:
        for name, score in h["scores"].items():
            out[name] = (score, h["commit"])
    return out


def diff(new, history):
    base = baseline(history)
    shared = sorted(set(new["scores"]) & set(base))
    lines = []
    if shared:
        b = sum(base[n][0] for n in shared) / len(shared)
        a = sum(new["scores"][n] for n in shared) / len(shared)
        passing = (sum(base[n][0] >= 1 for n in shared), sum(new["scores"][n] >= 1 for n in shared))
        lines.append(f"overall on {len(shared)} shared cases: {b:.3f} -> {a:.3f}; passing {passing[0]} -> {passing[1]}")
    for n in shared:
        before, at = base[n]
        after = new["scores"][n]
        if abs(after - before) > 1e-9:
            lines.append(f"  {n:30} {before:.2f} -> {after:.2f}  (was {at})")
    for n in sorted(set(new["scores"]) - set(base)):
        lines.append(f"  {n:30} new: {new['scores'][n]:.2f}")
    missing = sorted(set(base) - set(new["scores"]))
    if missing and len(new["scores"]) > 1:
        lines.append(f"  not run: {', '.join(missing)}")
    return lines


def check(history):
    problems = []
    for i, h in enumerate(history, 1):
        for key, kind in FIELDS.items():
            if not isinstance(h.get(key), kind):
                problems.append(f"line {i}: {key} missing or not {kind}")
        if any(not isinstance(v, (int, float)) or not 0 <= v <= 1 for v in h.get("scores", {}).values()):
            problems.append(f"line {i}: scores must be numbers from 0 to 1")
    starts = [h.get("started", "") for h in history]
    if starts != sorted(starts):
        problems.append("lines must be in the order the runs started")
    return problems


def read_result(path):
    return json.loads(Path(path).read_text())


def main():
    args = sys.argv[1:]
    if args == ["--check"]:
        problems = check(load())
        print("\n".join(problems) or f"{len(load())} runs recorded")
        sys.exit(1 if problems else 0)
    if not args or args[0] not in ("add", "diff"):
        sys.exit(__doc__)
    history = load()
    opt = lambda name: args[args.index(name) + 1] if name in args else None  # noqa: E731
    if args[0] == "add":
        if len(args) < 2:
            sys.exit(__doc__)
        new = entry(read_result(args[1]), opt("--commit") or head_commit(), opt("--note") or "")
        if any(h["started"] == new["started"] for h in history):
            sys.exit(f"run started {new['started']} is already recorded")
        print("\n".join(diff(new, history)))
        history.append(new)
        history.sort(key=lambda h: h["started"])
        HISTORY.write_text("".join(json.dumps(h, ensure_ascii=False) + "\n" for h in history))
        print(f"recorded run {new['started']} at {new['commit']}")
    else:
        if len(args) > 1:
            new, earlier = entry(read_result(args[1]), "this run", ""), history
        elif history:
            new, earlier = history[-1], history[:-1]
        else:
            sys.exit("no runs recorded")
        print("\n".join(diff(new, earlier)) or "nothing to compare")


if __name__ == "__main__":
    main()
