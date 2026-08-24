#!/usr/bin/env python3
"""Aggregate latest posts from CSDN / cnblogs / Juejin into profile READMEs."""

import datetime
import html
import os
import re
import urllib.request

CSDN_USER = "weixin_56622231"
CNBLOGS_RSS = "https://www.cnblogs.com/badhope/rss"
JUEJIN_USER_ID = "2350111542479753"
MAX_ITEMS = 6
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_csdn():
    page = _get(
        f"https://blog.csdn.net/{CSDN_USER}/article/list/1",
        headers={"Referer": "https://blog.csdn.net/", "Accept-Language": "zh-CN,zh;q=0.9"},
    )
    out = []
    for chunk in page.split('<div class="article-item-box')[1:]:
        m_url = re.search(
            rf'href="(https://blog\.csdn\.net/{CSDN_USER}/article/details/\d+)"', chunk
        )
        m_a = re.search(r"<a[^>]*>(.*?)</a>", chunk, flags=re.S)
        if not m_url or not m_a:
            continue
        title = re.sub(r"<span[^>]*>.*?</span>", "", m_a.group(1), flags=re.S)
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        m_date = re.search(r'<span class="date">(\d{4}-\d{2}-\d{2})', chunk)
        out.append((title, m_url.group(1), m_date.group(1) if m_date else "", "CSDN"))
    return out


def fetch_cnblogs():
    xml_text = _get(CNBLOGS_RSS)
    out = []
    for entry in xml_text.split("<entry>")[1:]:
        m_url = re.search(r"<id>(https://www\.cnblogs\.com/badhope/p/[^<]+)</id>", entry)
        m_title = re.search(r"<title[^>]*>([^<]+)</title>", entry)
        m_date = re.search(r"<published>(\d{4}-\d{2}-\d{2})", entry)
        if not (m_url and m_title):
            continue
        title = re.sub(r"\s*-\s*badhope33834\s*$", "", html.unescape(m_title.group(1)).strip())
        out.append((title, m_url.group(1), m_date.group(1) if m_date else "", "博客园"))
    return out


def fetch_juejin():
    body = json_dumps({"user_id": JUEJIN_USER_ID, "sort_type": 2, "cursor": "0"}).encode()
    req = urllib.request.Request(
        "https://api.juejin.cn/content_api/v1/article/query_list",
        data=body,
        headers={"User-Agent": UA, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json_loads(resp.read().decode("utf-8"))
    tz = datetime.timezone(datetime.timedelta(hours=8))
    out = []
    for item in payload.get("data") or []:
        info = item.get("article_info") or {}
        if not info.get("title") or not info.get("article_id"):
            continue
        date = datetime.datetime.fromtimestamp(int(info["ctime"]), tz).strftime("%Y-%m-%d")
        out.append((html.unescape(info["title"]).strip(),
                    f"https://juejin.cn/post/{info['article_id']}", date, "掘金"))
    return out


def json_dumps(obj):  # tiny wrappers keep stdlib imports tidy in one place
    import json
    return json.dumps(obj)


def json_loads(text):
    import json
    return json.loads(text)


SOURCES = ("CSDN", fetch_csdn), ("cnblogs", fetch_cnblogs), ("juejin", fetch_juejin)


def main():
    articles = []
    for name, fn in SOURCES:
        try:
            items = fn()
            print(f"{name}: {len(items)} posts")
            articles.extend(items)
        except Exception as err:  # noqa: BLE001 - one source failing must not kill all
            print(f"warn: {name} unavailable ({err}); skipped")

    if not articles:
        print("no articles fetched at all, keeping existing block")
        return

    articles.sort(key=lambda a: a[2], reverse=True)
    lines = [
        f"- [{t}]({u}) · `{d}` · {src}" for t, u, d, src in articles[:MAX_ITEMS]
    ]
    blog_block = "\n".join(lines)

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    touched = [
        name
        for name in ("README.md", "README.zh.md", "README.ja.md")
        if rewrite_block(os.path.join(root, name), blog_block)
    ]
    print("updated:", ", ".join(touched) if touched else "nothing (already current)")


def rewrite_block(path, blog_block):
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


if __name__ == "__main__":
    main()
