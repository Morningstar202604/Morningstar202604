#!/usr/bin/env python3
"""Deprecated refresh for STATS / PROJECTS blocks.

The profile READMEs are now built from a curated, cross-platform source
(scripts/build_profile.py): stats aggregate four platforms, projects are a
curated selection mirrored from GitCode. Running this script on a single
GitHub account would overwrite those blocks with one-account data.

Kept as a no-op so the `update-stats` workflow keeps working for the BLOG
block (see update_blog.py) without corrupting STATS / PROJECTS.
"""

import sys


def main():
    print(
        "note: STATS/PROJECTS are curated cross-platform content; "
        "only the BLOG block is refreshed by update_blog.py",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()