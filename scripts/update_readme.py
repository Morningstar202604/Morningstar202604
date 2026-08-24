#!/usr/bin/env python3
"""Refresh STATS / PROJECTS blocks in profile READMEs from live GitHub data."""

import json
import os
import re
import time
import urllib.request

TOKEN = os.environ["GH_TOKEN"]
OWNER = os.environ.get("OWNER", "Morningstar202604")
API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "profile-stats-bot",
}


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception as err:  # noqa: BLE001 - degrade silently on transient issues
            last_err = err
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"github api unreachable after retries: {last_err}")


def paginate(path):
    page, out = 1, []
    while True:
        data = get_json(f"{API}{path}?per_page=100&page={page}")
        if not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def build_blocks():
    user = get_json(f"{API}/users/{OWNER}")
    repos = paginate(f"/users/{OWNER}/repos")
    stars = sum(r["stargazers_count"] for r in repos)

    stats_block = (
        f"- ⭐ **{stars}** stars &nbsp;·&nbsp; "
        f"👥 **{user['followers']}** followers &nbsp;·&nbsp; "
        f"📦 **{user['public_repos']}** repositories"
    )

    ranked = sorted(repos, key=lambda r: (-r["stargazers_count"], r["name"].lower()))[:6]
    lines = [
        f"- ⭐ **[{r['name']}](https://github.com/{OWNER}/{r['name']})** · "
        f"{r['stargazers_count']}★ · {r['language'] or 'Code'}"
        + (" (fork)" if r["fork"] else "")
        for r in ranked
    ]
    projects_block = "\n".join(lines) if lines else "- 🚧 projects syncing…"
    return stats_block, projects_block


def rewrite(path, stats_block, projects_block):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    new = re.sub(
        r"(<!-- STATS:START -->).*?(<!-- STATS:END -->)",
        lambda m: f"{m.group(1)}\n{stats_block}\n{m.group(2)}",
        text,
        flags=re.S,
    )
    new = re.sub(
        r"(<!-- PROJECTS:START -->).*?(<!-- PROJECTS:END -->)",
        lambda m: f"{m.group(1)}\n{projects_block}\n{m.group(2)}",
        new,
        flags=re.S,
    )
    if new == text:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    return True


def main():
    try:
        stats_block, projects_block = build_blocks()
    except Exception as err:  # noqa: BLE001 - keep old content, never fail the job
        print(f"warn: {err}; keeping existing blocks")
        return
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    touched = [
        name
        for name in ("README.md", "README.zh.md", "README.ja.md")
        if rewrite(os.path.join(root, name), stats_block, projects_block)
    ]
    print("updated:", ", ".join(touched) if touched else "nothing (already current)")


if __name__ == "__main__":
    main()
