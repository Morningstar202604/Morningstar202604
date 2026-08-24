#!/usr/bin/env python3
"""Push refreshed profile READMEs to the Gitee / GitCode mirrors."""

import base64
import json
import os
import urllib.request

REPO = "badhope/badhope"
FILES = ["README.md", "README.zh.md", "README.ja.md"]
MSG = "sync: refresh profile from GitHub [skip ci]"


def http(url, method="GET", data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def sync_gitee(token, fname, content_b64):
    meta = http(
        f"https://gitee.com/api/v5/repos/{REPO}/contents/{fname}?access_token={token}"
    )
    body = json.dumps(
        {
            "access_token": token,
            "content": content_b64,
            "sha": meta["sha"],
            "branch": "main",
            "message": MSG,
        }
    ).encode()
    result = http(
        f"https://gitee.com/api/v5/repos/{REPO}/contents/{fname}",
        method="PUT",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    print(f"gitee {fname}: {result['commit']['message']}")


def sync_gitcode(token, fname, content_b64):
    headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}
    meta = http(
        f"https://api.gitcode.com/api/v5/repos/{REPO}/contents/{fname}",
        headers=headers,
    )
    body = json.dumps(
        {
            "content": content_b64,
            "sha": meta["sha"],
            "branch": "main",
            "message": MSG,
        }
    ).encode()
    result = http(
        f"https://api.gitcode.com/api/v5/repos/{REPO}/contents/{fname}",
        method="PUT",
        data=body,
        headers=headers,
    )
    print(f"gitcode {fname}: {result['commit']['message']}")


def main():
    gitee = os.environ.get("GITEE_TOKEN", "")
    gitcode = os.environ.get("GITCODE_TOKEN", "")
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for fname in FILES:
        with open(os.path.join(root, fname), "rb") as fh:
            content_b64 = base64.b64encode(fh.read()).decode()
        if gitee:
            sync_gitee(gitee, fname, content_b64)
        else:
            print("gitee: GITEE_TOKEN not set, skipped")
        if gitcode:
            sync_gitcode(gitcode, fname, content_b64)
        else:
            print("gitcode: GITCODE_TOKEN not set, skipped")


if __name__ == "__main__":
    main()
