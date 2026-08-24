#!/usr/bin/env python3
"""Push refreshed profile READMEs + generated graphics to the Gitee / GitCode mirrors."""

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request

REPO = "badhope/badhope"
FILES = ["README.md", "README.zh.md", "README.ja.md"]
ASSET_DIRS = ["assets", "profile-3d-contrib"]
MSG = "sync: refresh profile from GitHub [skip ci]"


def http(url, method="GET", data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def gitee_put(token, path, data: bytes):
    meta = http(
        f"https://gitee.com/api/v5/repos/{REPO}/contents/{path}?access_token={token}"
    )
    if meta.get("sha") == blob_sha(data):
        return f"{path}: unchanged"
    body = json.dumps(
        {
            "access_token": token,
            "content": base64.b64encode(data).decode(),
            "sha": meta["sha"],
            "branch": "main",
            "message": MSG,
        }
    ).encode()
    result = http(
        f"https://gitee.com/api/v5/repos/{REPO}/contents/{path}",
        method="PUT",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    return f"{path}: {result['commit']['message']}"


def gitcode_put(token, path, data: bytes):
    headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}
    url = f"https://api.gitcode.com/api/v5/repos/{REPO}/contents/{path}"
    try:
        meta = http(url, headers=headers)
        if meta.get("sha") == blob_sha(data):
            return f"{path}: unchanged"
        payload = {
            "content": base64.b64encode(data).decode(),
            "sha": meta["sha"],
            "branch": "main",
            "message": MSG,
        }
    except urllib.error.HTTPError as err:
        if err.code != 404:
            raise
        payload = {
            "content": base64.b64encode(data).decode(),
            "branch": "main",
            "message": MSG,
        }
    result = http(url, method="PUT", data=json.dumps(payload).encode(), headers=headers)
    return f"{path}: {result['commit']['message']}"


def collect_files(root):
    paths = list(FILES)
    for d in ASSET_DIRS:
        full = os.path.join(root, d)
        for name in sorted(os.listdir(full)):
            paths.append(f"{d}/{name}")
    return paths


def main():
    gitee = os.environ.get("GITEE_TOKEN", "")
    gitcode = os.environ.get("GITCODE_TOKEN", "")
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for rel in collect_files(root):
        with open(os.path.join(root, rel), "rb") as fh:
            data = fh.read()
        for label, token, put in (
            ("gitee", gitee, gitee_put),
            ("gitcode", gitcode, gitcode_put),
        ):
            if not token:
                print(f"{label}: token not set, skipped")
                continue
            try:
                print(f"{label} {put(token, rel, data)}")
            except Exception as err:  # noqa: BLE001 - isolate per-file/per-platform
                print(f"{label} {rel}: sync failed ({err}), will retry tomorrow")


if __name__ == "__main__":
    main()
