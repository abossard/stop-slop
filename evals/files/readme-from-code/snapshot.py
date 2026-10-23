#!/usr/bin/env python3
"""Back up Grafana dashboards to a git repository."""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import urllib.request

DEFAULT_URL = "http://localhost:3000"
AUTH_SCHEME = "Bearer"


def fetch(url: str, token: str, path: str):
    req = urllib.request.Request(f"{url}{path}", headers={"Authorization": f"{AUTH_SCHEME} {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=os.environ.get("GRAFANA_URL", DEFAULT_URL))
    p.add_argument("--out", default="dashboards", help="directory inside the git repo")
    p.add_argument("--folder", action="append", help="only these folder titles (repeatable)")
    p.add_argument("--no-commit", action="store_true", help="write files but do not commit")
    args = p.parse_args()

    token = os.environ.get("GRAFANA_TOKEN")
    if not token:
        print("GRAFANA_TOKEN is not set", file=sys.stderr)
        return 2

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for hit in fetch(args.url, token, "/api/search?type=dash-db"):
        if args.folder and hit.get("folderTitle", "General") not in args.folder:
            continue
        dash = fetch(args.url, token, f"/api/dashboards/uid/{hit['uid']}")["dashboard"]
        dash.pop("version", None)
        dash.pop("id", None)
        folder = out / hit.get("folderTitle", "General")
        folder.mkdir(exist_ok=True)
        (folder / f"{hit['uid']}.json").write_text(json.dumps(dash, indent=2, sort_keys=True) + "\n")
        count += 1

    if not args.no_commit:
        subprocess.run(["git", "add", str(out)], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode:
            subprocess.run(["git", "commit", "-m", f"Snapshot {count} dashboards"], check=True)
    print(f"{count} dashboards written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
