#!/usr/bin/env python3
"""Refresh the BLOG block in profile READMEs by scraping the CSDN article list."""

import html
import os
import re
import urllib.request

BLOG_USER = "weixin_56622231"
LIST_URL = f"https://blog.csdn.net/{BLOG_USER}/article/list/1"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
MAX_ITEMS = 5


def fetch_articles():
    req = urllib.request.Request(
        LIST_URL,
        headers={
            "User-Agent": UA,
            "Referer": f"https://blog.csdn.net/",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", errors="replace")

    articles = []
    for chunk in page.split('<div class="article-item-box')[1:]:
        m_url = re.search(
            rf'href="(https://blog\.csdn\.net/{BLOG_USER}/article/details/\d+)"', chunk
        )
        if not m_url:
            continue
        m_a = re.search(r"<a[^>]*>(.*?)</a>", chunk, flags=re.S)
        if not m_a:
            continue
        title = re.sub(r"<span[^>]*>.*?</span>", "", m_a.group(1), flags=re.S)
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        m_date = re.search(r'<span class="date">(\d{4}-\d{2}-\d{2})', chunk)
        date = m_date.group(1) if m_date else ""
        articles.append((title, m_url.group(1), date))
    return articles[:MAX_ITEMS]


def rewrite(path, blog_block):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    new = re.sub(
        r"(<!-- BLOG:START -->).*?(<!-- BLOG:END -->)",
        lambda m: f"{m.group(1)}\n{blog_block}\n{m.group(2)}",
        text,
        flags=re.S,
    )
    if new == text:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    return True


def main():
    try:
        articles = fetch_articles()
    except Exception as err:  # noqa: BLE001 - keep old content, never fail the job
        print(f"warn: csdn unreachable ({err}); keeping existing block")
        return
    if not articles:
        print("no articles fetched, keeping existing block")
        return
    lines = [
        f"- [{t}]({u})" + (f" · `{d}`" if d else "") for t, u, d in articles
    ]
    blog_block = "\n".join(lines)

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    touched = [
        name
        for name in ("README.md", "README.zh.md", "README.ja.md")
        if rewrite(os.path.join(root, name), blog_block)
    ]
    print(f"fetched {len(articles)} articles")
    print("updated:", ", ".join(touched) if touched else "nothing (already current)")


if __name__ == "__main__":
    main()
