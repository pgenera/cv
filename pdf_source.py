#!/usr/bin/env python3
"""Tell which commit(s) a CV PDF was built from.

Reads the cv.yaml fingerprint that build.py writes into the PDF's Keywords
(`cv.yaml sha256:<12 hex>`) and finds the commits whose cv.yaml matches.

Usage: pdf_source.py some.pdf     (or: make identify PDF=some.pdf)
"""

import hashlib
import re
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def main():
    pdf = sys.argv[1]
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    m = re.search(r"cv\.yaml sha256:([0-9a-f]{12})", info)
    if not m:
        sys.exit(f"{pdf}: no cv.yaml fingerprint in its metadata (built before fingerprints were added?)")
    want = m.group(1)
    date = re.search(r"^CreationDate:\s*(.*)$", info, re.M)
    print(f"{pdf}: cv.yaml sha256:{want}" + (f", content date {date.group(1).strip()}" if date else ""))

    hits = []
    for line in git("log", "--format=%H %cs %s", "--", "cv.yaml").decode().splitlines():
        sha, day, subject = line.split(" ", 2)
        try:
            blob = git("show", f"{sha}:cv.yaml")
        except subprocess.CalledProcessError:
            continue
        if hashlib.sha256(blob).hexdigest().startswith(want):
            hits.append(f"  {sha[:10]} {day} {subject}")
    working = hashlib.sha256(open("cv.yaml", "rb").read()).hexdigest().startswith(want)
    if hits:
        print("matches cv.yaml as committed in:")
        print("\n".join(hits))
    if working:
        print("matches the current working-copy cv.yaml")
    if not hits and not working:
        print("no commit's cv.yaml matches; built from an uncommitted edit")


if __name__ == "__main__":
    main()
