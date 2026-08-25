#!/usr/bin/env python3
"""Rebuild the 3 profile READMEs from the pristine Gitee template, applying every
transformation deterministically. Replaces the buggy regex-based beautify pass."""

import os
import subprocess

SOURCE_COMMIT = "7c3182e"
GIT_REPO = r"D:\Temp\User\opencode\profile-repo"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = "https://gitee.com/badhope/badhope/raw/main"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126"

OLD_ACC = "github.com/Morningstar202604"
NEW_ACC = "github.com/Morningstar202604"
CSDN_BADGE = '<a href="https://blog.csdn.net/weixin_56622231"><img src="https://img.shields.io/badge/CSDN-Blog-C9A86A?style=flat&logo=bytes&logoColor=white&labelColor=0B1026" alt="CSDN Blog" /></a>'
NEW_BADGES = (
    CSDN_BADGE + "\n"
    '  <a href="https://www.cnblogs.com/badhope"><img src="https://img.shields.io/badge/cnblogs-badhope-C9A86A?style=flat&labelColor=0B1026" alt="cnblogs" /></a>\n'
    '  <a href="https://juejin.cn/user/2350111542479753"><img src="https://img.shields.io/badge/Juejin-2350111542479753-C9A86A?style=flat&logo=juejin&logoColor=white&labelColor=0B1026" alt="Juejin" /></a>'
)

HEADER = (
    '<p align="center">\n'
    '  <img src="https://capsule-render.vercel.app/api?type=waving&height=220'
    "&text=Morningstar202604%20%2F%20Morningstar202604&fontSize=45&fontAlignY=34"
    "&subText=%E5%A4%9C%E8%A7%82%E6%98%9F%E8%B1%A1%EF%BC%8C%E4%BB%A5%E4%BB%A3%E7%A0%81%E4%BD%9C%E8%88%9F%E3%80%82"
    "&subTextSize=17&subTextAlignY=58&animation=twinkling"
    '&color=0:0B1026,55:16213E,100:C9A86A&stroke=C9A86A&strokeWidth=0" '
    'alt="header" width="100%" />\n'
    "</p>\n\n"
    '<div align="center">\n'
    '  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24'
    "&pause=1200&color=C9A86A&center=true&vCenter=true&width=700&height=60&lines="
    "%E5%A4%9C%E8%A7%82%E6%98%9F%E8%B1%A1%EF%BC%8C%E4%BB%A5%E4%BB%A3%E7%A0%81%E4%BD%9C%E8%88%9F%E3%80%82;"
    "%E4%B8%8E%E5%85%B6%E6%9B%B4%E5%A5%BD%EF%BC%8C%E4%B8%8D%E5%A6%82%E4%B8%8D%E5%90%8C;"
    'Code%20under%20the%20stars%2C%20ship%20with%20the%20dawn" alt="typing" />\n'
    "</div>"
)

EXTRA_STATS = (
    '<p align="center">\n'
    '  <img src="https://github-profile-trophy.vercel.app/?username=Morningstar202604'
    '&theme=tokyonight&no-frame=true&row=1&column=7&margin-w=6" alt="trophies" width="98%" />\n'
    "</p>\n\n"
    '<img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details'
    '?username=Morningstar202604&theme=tokyonight" alt="profile details" width="99%" />\n\n'
    "<table>\n<tr>\n"
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=Morningstar202604&theme=tokyonight" alt="repos per language" width="100%" /></td>\n'
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=Morningstar202604&theme=tokyonight" alt="stats" width="100%" /></td>\n'
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=Morningstar202604&theme=tokyonight" alt="productive time" width="100%" /></td>\n'
    "</tr>\n</table>\n\n"
    '<p align="center">\n'
    '  <img src="https://github-readme-activity-graph.vercel.app/graph?username=Morningstar202604'
    "&area=true&area_color=16213E&bg_color=0B1026&color=C9A86A&line=7C3AED&point=EAB308"
    '&hide_border=true&radius=16" alt="activity graph" width="98%" />\n'
    "</p>\n\n"
    '<p align="center">\n  <img src="./metrics.svg" alt="metrics panorama" width="98%" />\n</p>'
)

SKILLICONS = (
    '<p align="center">\n'
    '  <img src="https://skillicons.dev/icons?i=ts,js,py,rust,nodejs,react,vite,tailwind,docker,git,githubactions,md&theme=dark" '
    'alt="tech stack" />\n'
    "</p>"
)

FOOTER = (
    '<p align="center">\n'
    '  <img src="https://capsule-render.vercel.app/api?type=waving&section=footer&height=90'
    '&color=0:C9A86A,100:0B1026" alt="footer" width="100%" />\n'
    "</p>\n\n"
)


def fetch(path):
    """Read the pristine file from git history (Gitee mirror is polluted)."""
    return subprocess.run(
        ["git", "-C", GIT_REPO, "show", f"{SOURCE_COMMIT}:{path}"],
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
    ).stdout


def replace_tech_stack(text):
    """Replace exactly the tech-stack <p> block(s): the one containing the
    TypeScript badge, plus any IMMEDIATELY following sibling badge <p> block."""
    i = text.index("badge/TypeScript")
    start = text.rindex('<p align="center">', 0, i)
    end = text.index("</p>", i) + len("</p>")
    while True:
        k = end
        while k < len(text) and text[k] in "\r\n\t ":
            k += 1
        if not text.startswith('<p align="center">', k):
            break
        close = text.index("</p>", k) + len("</p>")
        if "img.shields.io" not in text[k:close]:
            break
        end = close
    return text[:start] + SKILLICONS + text[end:]


def transform(name, text):
    text = text.replace(OLD_ACC, NEW_ACC).replace(
        "GitHub-Morningstar202604-", "GitHub-Morningstar202604-"
    )
    if "cnblogs.com/badhope" not in text:
        assert CSDN_BADGE in text, f"{name}: CSDN badge anchor missing"
        text = text.replace(CSDN_BADGE, NEW_BADGES)
    assert '<h1 align="center">Morningstar202604 / Morningstar202604</h1>' in text, f"{name}: h1 missing"
    text = text.replace('<h1 align="center">Morningstar202604 / Morningstar202604</h1>', HEADER, 1)
    assert "<!-- STATS:END -->" in text, f"{name}: STATS marker missing"
    text = text.replace("<!-- STATS:END -->", f"<!-- STATS:END -->\n\n{EXTRA_STATS}", 1)
    text = replace_tech_stack(text)
    marker = "<sub>&copy; Morningstar202604"
    idx = text.index(marker)
    p_start = text.rindex('<p align="center">', 0, idx)
    text = text[:p_start] + FOOTER + text[p_start:]

    required = [
        "STATS:START",
        "STATS:END",
        "PROJECTS:START",
        "PROJECTS:END",
        "BLOG:START",
        "BLOG:END",
        "skillicons.dev",
        "capsule-render",
        "./metrics.svg",
        "cnblogs.com/badhope",
        "juejin.cn/user",
        "section=footer",
        NEW_ACC,
    ]
    for r in required:
        assert r in text, f"{name}: post-check failed, missing {r}"
    assert OLD_ACC not in text, f"{name}: stale account link survived"
    return text


def main():
    os.makedirs(ROOT, exist_ok=True)
    for name in ("README.md", "README.zh.md", "README.ja.md"):
        rebuilt = transform(name, fetch(name))
        with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(rebuilt)
        print(f"{name}: rebuilt {len(rebuilt.encode('utf-8'))}B, all checks passed")


if __name__ == "__main__":
    main()
