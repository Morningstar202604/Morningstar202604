#!/usr/bin/env python3
"""One-off: inject visual components (header/typing/trophy/cards/graph/metrics/skillicons/footer)."""

import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HEADER = (
    '<p align="center">\n'
    '  <img src="https://capsule-render.vercel.app/api?type=waving&height=220'
    '&text=badhope%20%2F%20weed33834&fontSize=45&fontAlignY=34'
    '&subText=%E5%A4%9C%E8%A7%82%E6%98%9F%E8%B1%A1%EF%BC%8C%E4%BB%A5%E4%BB%A3%E7%A0%81%E4%BD%9C%E8%88%9F%E3%80%82'
    '&subTextSize=17&subTextAlignY=58&animation=twinkling'
    '&color=0:0B1026,55:16213E,100:C9A86A&stroke=C9A86A&strokeWidth=0" '
    'alt="header" width="100%" />\n'
    '</p>\n\n'
    '<div align="center">\n'
    '  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24'
    '&pause=1200&color=C9A86A&center=true&vCenter=true&width=700&height=60&lines='
    '%E5%A4%9C%E8%A7%82%E6%98%9F%E8%B1%A1%EF%BC%8C%E4%BB%A5%E4%BB%A3%E7%A0%81%E4%BD%9C%E8%88%9F%E3%80%82;'
    '%E4%B8%8E%E5%85%B6%E6%9B%B4%E5%A5%BD%EF%BC%8C%E4%B8%8D%E5%A6%82%E4%B8%8D%E5%90%8C;'
    'Code%20under%20the%20stars%2C%20ship%20with%20the%20dawn" alt="typing" />\n'
    '</div>'
)

EXTRA_STATS = (
    '<p align="center">\n'
    '  <img src="https://github-profile-trophy.vercel.app/?username=Morningstar202604'
    '&theme=tokyonight&no-frame=true&row=1&column=7&margin-w=6" alt="trophies" width="98%" />\n'
    '</p>\n\n'
    '<img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details'
    '?username=Morningstar202604&theme=tokyonight" alt="profile details" width="99%" />\n\n'
    '<table>\n'
    '<tr>\n'
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language'
    '?username=Morningstar202604&theme=tokyonight" alt="repos per language" width="100%" /></td>\n'
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/stats'
    '?username=Morningstar202604&theme=tokyonight" alt="stats" width="100%" /></td>\n'
    '<td><img src="https://github-profile-summary-cards.vercel.app/api/cards/productive-time'
    '?username=Morningstar202604&theme=tokyonight" alt="productive time" width="100%" /></td>\n'
    '</tr>\n'
    '</table>\n\n'
    '<p align="center">\n'
    '  <img src="https://github-readme-activity-graph.vercel.app/graph?username=Morningstar202604'
    '&area=true&area_color=16213E&bg_color=0B1026&color=C9A86A&line=7C3AED&point=EAB308'
    '&hide_border=true&radius=16" alt="activity graph" width="98%" />\n'
    '</p>\n\n'
    '<p align="center">\n'
    '  <img src="./metrics.svg" alt="metrics panorama" width="98%" />\n'
    '</p>'
)

SKILLICONS = (
    '<p align="center">\n'
    '  <img src="https://skillicons.dev/icons?i=ts,js,py,rust,nodejs,react,vite,tailwind,docker,git,githubactions,md&theme=dark" '
    'alt="tech stack" />\n'
    '</p>'
)

FOOTER = (
    '<p align="center">\n'
    '  <img src="https://capsule-render.vercel.app/api?type=waving&section=footer&height=90'
    '&color=0:C9A86A,100:0B1026" alt="footer" width="100%" />\n'
    '</p>\n\n'
)


def transform(text):
    text = re.sub(
        r'<h1 align="center">badhope / weed33834</h1>', HEADER, text, count=1
    )
    text = re.sub(
        r"(<!-- STATS:END -->)",
        lambda m: f"{m.group(1)}\n\n{EXTRA_STATS}",
        text,
        count=1,
    )
    text = re.sub(
        r'<p align="center">\s*<img src="https://img\.shields\.io/badge/TypeScript.*?</p>\s*<p align="center">.*?</p>',
        SKILLICONS,
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<p align="center">\s*<sub>&copy; badhope/weed33834)',
        FOOTER + r"\1",
        text,
        count=1,
    )
    return text


def main():
    for name in ("README.md", "README.zh.md", "README.ja.md"):
        path = os.path.join(ROOT, name)
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        updated = transform(original)
        changed = updated != original
        if changed:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(updated)
        print(f"{name}: {'injected' if changed else 'no change'}")


if __name__ == "__main__":
    main()
