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

    # Recency first: new projects must surface as soon as they are pushed,
    # which a star ranking never does. Original work outranks forks; stars
    # only break ties between equally fresh repos.
    def recency(r):
        return (r["pushed_at"] or "", r["stargazers_count"])

    originals = sorted(
        (r for r in repos if not r["fork"] and r["name"] != owner),
        key=recency,
        reverse=True,
    )
    forks = sorted((r for r in repos if r["fork"]), key=recency, reverse=True)
    ranked = (originals + forks)[:6]
    projects = []
    for r in ranked:
        bits = []
        if r["stargazers_count"]:
            bits.append(f"{r['stargazers_count']}★")
        bits.append(r["language"] or "Code")
        bits.append((r["pushed_at"] or "")[:10])
        projects.append(
            f"- **[{r['name']}](https://github.com/{owner}/{r['name']})** · "
            + " · ".join(bits)
            + (" (fork)" if r["fork"] else "")
        )
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
