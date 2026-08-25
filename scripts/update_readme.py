#!/usr/bin/env python3
"""Refresh STATS / PROJECTS blocks in profile READMEs from live GitHub data."""

import os

import common


def paginate(path):
    page, out = 1, []
    while True:
        data = common.github_api(
            f"{path}?per_page=100&page={page}", os.environ["GH_TOKEN"]
        )
        if not data:
            break
        out.extend(data)
        if len(data) < 100:
            page += 1
        else:
            break
    return out


def build_blocks(owner):
    user = common.github_api(f"/users/{owner}", os.environ["GH_TOKEN"])
    repos = paginate(f"/users/{owner}/repos")
    stars = sum(r["stargazers_count"] for r in repos)

    stats = (
        f"- ⭐ **{stars}** stars &nbsp;·&nbsp; "
        f"👥 **{user['followers']}** followers &nbsp;·&nbsp; "
        f"📦 **{user['public_repos']}** repositories"
    )

    ranked = sorted(repos, key=lambda r: (-r["stargazers_count"], r["name"].lower()))[
        :6
    ]
    projects = [
        f"- ⭐ **[{r['name']}](https://github.com/{owner}/{r['name']})** · "
        f"{r['stargazers_count']}★ · {r['language'] or 'Code'}"
        + (" (fork)" if r["fork"] else "")
        for r in ranked
    ]
    return {
        "STATS": stats,
        "PROJECTS": "\n".join(projects) if projects else "- 🚧 projects syncing…",
    }


def main():
    owner = os.environ.get("OWNER", "Morningstar202604")
    try:
        blocks = build_blocks(owner)
    except Exception as err:  # noqa: BLE001 - keep old content, never fail the job
        print(f"warn: {err}; keeping existing blocks")
        return
    common.update_all_readmes(blocks)


if __name__ == "__main__":
    main()
