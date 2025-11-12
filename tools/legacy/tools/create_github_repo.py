#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a GitHub repository using a token stored in a local _netrc file.
- Reads token from _netrc at repo root (machine github.com login x-access-token password <TOKEN>)
- Creates repo under the authenticated user
- Usage: python tools/create_github_repo.py <repo_name> [private]
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETRC_PATH = os.path.join(ROOT, "_netrc")
API_URL = "https://api.github.com/user/repos"


def read_token_from_netrc(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"_netrc not found: {path}")
    token = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Expect lines like: machine github.com / login x-access-token / password TOKEN
            parts = line.split()
            if len(parts) >= 6 and parts[0] == 'machine' and parts[1] == 'github.com':
                # find 'password' index
                for i in range(len(parts)-1):
                    if parts[i] == 'password':
                        token = parts[i+1]
                        break
    if not token:
        raise RuntimeError("GitHub token not found in _netrc")
    return token


def create_repo(repo_name: str, private: bool = False) -> dict:
    token = read_token_from_netrc(NETRC_PATH)
    data = json.dumps({
        "name": repo_name,
        "private": private,
        "auto_init": False,
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "repo-init-script")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"GitHub API error {e.code}: {msg}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error: {e}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python tools/create_github_repo.py <repo_name> [private:true|false]")
        return 2
    repo_name = argv[1]
    private = False
    if len(argv) >= 3:
        val = argv[2].strip().lower()
        private = val in ("1", "true", "yes")

    info = create_repo(repo_name, private)
    print(json.dumps({
        "full_name": info.get("full_name"),
        "ssh_url": info.get("ssh_url"),
        "clone_url": info.get("clone_url"),
        "default_branch": info.get("default_branch"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
