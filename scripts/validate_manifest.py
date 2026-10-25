#!/usr/bin/env python3
"""Validate yunluo's *device-only* repo manifest and reachable upstream branches."""
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EXPECTED = {
    "device/xiaomi/yunluo",
    "device/xiaomi/yunluo-kernel",
    "device/mediatek/sepolicy_vndr",
    "hardware/mediatek",
    "hardware/xiaomi",
    "vendor/xiaomi/yunluo",
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--offline", action="store_true", help="Skip remote git branch checks")
    args = parser.parse_args()
    root = ET.parse(args.manifest).getroot()
    if root.tag != "manifest":
        raise ValueError("Root XML element must be <manifest>")

    remotes = {}
    for el in root.findall("remote"):
        name = el.get("name")
        if not name or name in remotes:
            raise ValueError(f"Missing/duplicate remote name: {name}")
        remotes[name] = el.attrib

    seen = set()
    projects = root.findall("project")
    for project in projects:
        name, path, remote_name = (project.get(k) for k in ("name", "path", "remote"))
        if not name or not path or remote_name not in remotes:
            raise ValueError(f"Malformed project declaration: {project.attrib}")
        if path in seen:
            raise ValueError(f"Duplicate checkout path: {path}")
        seen.add(path)
        remote = remotes[remote_name]
        branch = project.get("revision", remote.get("revision"))
        if not branch or not branch.startswith("refs/heads/"):
            raise ValueError(f"Expected explicit branch for {name}: {branch}")
        url = remote["fetch"].rstrip("/") + "/" + name + ".git"
        print(f"{path}: {url} ({branch})", flush=True)
        if not args.offline:
            run = subprocess.run(
                ["git", "ls-remote", "--exit-code", url, branch],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=90, check=False,
            )
            if run.returncode != 0 or not run.stdout.strip():
                raise RuntimeError(
                    f"Missing/inaccessible branch {branch} in {url}: {run.stderr.strip()}"
                )

    if seen != EXPECTED:
        raise ValueError(f"Unexpected project paths: missing={EXPECTED - seen} extra={seen - EXPECTED}")
    if not args.offline:
        base = subprocess.run(
            ["git", "ls-remote", "--exit-code", "https://github.com/LineageOS/android.git",
             "refs/heads/lineage-23.0"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90,
        )
        if base.returncode or not base.stdout.strip():
            raise RuntimeError("LineageOS 23.0 base manifest branch is not available")
    print(f"OK: verified {len(projects)} yunluo projects; no Android source downloaded.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ET.ParseError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
