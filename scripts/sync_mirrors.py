#!/usr/bin/env python3
"""Push refreshed profile READMEs + generated graphics to the Gitee / GitCode mirrors."""

import base64
import os

import common

ASSET_DIRS = ("assets", "profile-3d-contrib")
SYNC_MSG = "sync: refresh profile from GitHub [skip ci]"


def gitee_put(token, path, data):
    api = f"https://gitee.com/api/v5/repos/{common.MIRROR_REPO}/contents/{path}"
    meta = common.http_json(f"{api}?access_token={token}", allow_404=True)
    if meta and meta.get("sha") == common.blob_sha(data):
        return "unchanged"
    payload = {
        "access_token": token,
        "content": base64.b64encode(data).decode(),
        "branch": "main",
        "message": SYNC_MSG,
    }
    if meta:
        payload["sha"] = meta["sha"]
    result = common.http_json(api, method="PUT", payload=payload)
    return result["commit"]["message"]


def gitcode_put(token, path, data):
    headers = {"PRIVATE-TOKEN": token}
    api = f"https://api.gitcode.com/api/v5/repos/{common.MIRROR_REPO}/contents/{path}"
    meta = common.http_json(api, headers=headers, allow_404=True)
    encoded = base64.b64encode(data).decode()
    if meta:
        if meta.get("sha") == common.blob_sha(data):
            return "unchanged"
        payload = {
            "content": encoded,
            "sha": meta["sha"],
            "branch": "main",
            "message": SYNC_MSG,
        }
    else:
        payload = {"content": encoded, "branch": "main", "message": SYNC_MSG}
    result = common.http_json(api, method="PUT", payload=payload, headers=headers)
    return result["commit"]["message"]


PLATFORMS = (("gitee", gitee_put), ("gitcode", gitcode_put))


def collect_paths():
    paths = list(common.README_FILES)
    for d in ASSET_DIRS:
        full = os.path.join(common.ROOT, d)
        paths += [f"{d}/{name}" for name in sorted(os.listdir(full))]
    return paths


def main():
    tokens = {
        "gitee": os.environ.get("GITEE_TOKEN", ""),
        "gitcode": os.environ.get("GITCODE_TOKEN", ""),
    }
    for rel in collect_paths():
        with open(os.path.join(common.ROOT, rel), "rb") as fh:
            data = fh.read()
        for label, put in PLATFORMS:
            if not tokens[label]:
                print(f"{label}: token not set, skipped")
                continue
            try:
                print(f"{label} {rel}: {put(tokens[label], rel, data)}")
            except Exception as err:  # noqa: BLE001 - isolate per-file/per-platform
                print(f"{label} {rel}: sync failed ({err}), will retry tomorrow")


if __name__ == "__main__":
    main()
