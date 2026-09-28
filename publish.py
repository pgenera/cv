#!/usr/bin/env python3
"""Publish a filtered copy of this repo's history to GitHub.

The full repo (including CLAUDE.md and private/) lives in SVN via git-svn.
GitHub gets the same linear history with the private paths removed from every
commit, git-svn-id trailers stripped, and commits that only touched private
files dropped. The filter is deterministic, so re-running it reproduces the
same commit hashes and every push is a fast-forward.

Usage:
  publish.py            build refs/publish/main and run every check (dry run)
  publish.py --push     same, then push to GitHub if every check passed

Safety rails:
  - publishes only what is already in SVN (refs/remotes/git-svn)
  - refuses merges (git-svn history is linear anyway)
  - verifies no private path exists in any published commit
  - scans every published file, PDF text, and commit message against
    private/publish-denylist.txt
  - pushes only to the `github` remote, only if its URL is pgenera/cv,
    only refs/publish/main -> main, and never with --force
"""

import os
import re
import subprocess
import sys
import tempfile

SOURCE = "refs/remotes/git-svn"
TARGET = "refs/publish/main"
PRIVATE = ("CLAUDE.md", "private", "osm", "map_data.json")
DENYLIST = "private/publish-denylist.txt"
REMOTE = "github"
ALLOWED_URLS = {
    "git@github.com:pgenera/cv.git",
    "https://github.com/pgenera/cv.git",
    "https://github.com/pgenera/cv",
}
BRANCH = "main"


def git(*args, env=None, input=None, check=True):
    r = subprocess.run(["git", *args], capture_output=True, env=env, input=input)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stderr.decode(errors='replace')}")
    return r.stdout.decode(errors="replace").strip()


def fail(msg):
    sys.exit(f"REFUSING TO PUBLISH: {msg}")


def is_private(path):
    return any(path == p or path.startswith(p + "/") for p in PRIVATE)


def filtered_tree(commit, index):
    env = {**os.environ, "GIT_INDEX_FILE": index}
    git("read-tree", commit, env=env)
    git("rm", "--cached", "-r", "-q", "-f", "--ignore-unmatch", "--", *PRIVATE, env=env)
    return git("write-tree", env=env)


def clean_message(msg):
    lines = [l for l in msg.splitlines() if not l.startswith("git-svn-id:")]
    return "\n".join(lines).rstrip() + "\n"


def build():
    if not git("rev-parse", "--verify", "-q", SOURCE, check=False):
        fail(f"{SOURCE} does not exist; set up git-svn first")
    unsynced = git("rev-list", f"{SOURCE}..HEAD")
    if unsynced:
        fail(f"{len(unsynced.split())} local commit(s) not yet in SVN; run `git svn dcommit` first")

    commits = git("rev-list", "--reverse", "--parents", SOURCE).splitlines()
    parent, prev_tree, kept, dropped = None, None, 0, 0
    with tempfile.TemporaryDirectory() as tmp:
        index = os.path.join(tmp, "index")
        for line in commits:
            sha, *parents = line.split()
            if len(parents) > 1:
                fail(f"merge commit {sha[:10]}; history must be linear")
            tree = filtered_tree(sha, index)
            if tree == prev_tree or (parent is None and not git("ls-tree", tree)):
                dropped += 1
                continue
            fmt = "%an%x00%ae%x00%ad%x00%cn%x00%ce%x00%cd%x00%B"
            an, ae, ad, cn, ce, cd, body = git("log", "-1", "--date=raw", f"--format={fmt}", sha).split("\0", 6)
            env = {**os.environ,
                   "GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae, "GIT_AUTHOR_DATE": ad,
                   "GIT_COMMITTER_NAME": cn, "GIT_COMMITTER_EMAIL": ce, "GIT_COMMITTER_DATE": cd}
            args = ["commit-tree", tree] + (["-p", parent] if parent else [])
            parent = git(*args, env=env, input=clean_message(body).encode())
            prev_tree, kept = tree, kept + 1
    if parent is None:
        fail("nothing to publish")
    git("update-ref", TARGET, parent)
    return kept, dropped


def load_denylist():
    try:
        entries = [l.strip() for l in open(DENYLIST) if l.strip() and not l.lstrip().startswith("#")]
    except FileNotFoundError:
        fail(f"{DENYLIST} is missing")
    if not entries:
        fail(f"{DENYLIST} is empty")
    return [(e, re.compile(r"(?<![\w/.])" + re.escape(e) + r"(?![\w])", re.I)) for e in entries]


def pdf_text(blob):
    r = subprocess.run(["pdftotext", "-", "-"], input=blob, capture_output=True)
    if r.returncode:
        fail("pdftotext failed on a published PDF; cannot scan it")
    return r.stdout.decode(errors="replace")


def verify():
    problems = []
    commits = git("rev-list", TARGET).split()
    for c in commits:
        bad = [p for p in git("ls-tree", "-r", "--name-only", c).splitlines() if is_private(p)]
        if bad:
            problems.append(f"commit {c[:10]} contains private paths: {bad}")

    deny = load_denylist()
    texts = [(f"message of {c[:10]}", git("log", "-1", "--format=%B", c)) for c in commits]
    for where, msg in texts:
        if re.search(r"^git-svn-id:", msg, re.M):
            problems.append(f"git-svn trailer left in {where}")
    seen = set()
    for line in git("rev-list", "--objects", TARGET).splitlines():
        sha, _, path = line.partition(" ")
        if not path or sha in seen or git("cat-file", "-t", sha) != "blob":
            continue
        seen.add(sha)
        data = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True).stdout
        if path.endswith(".pdf"):
            texts.append((path, pdf_text(data)))
        elif b"\0" not in data[:8000]:
            texts.append((path, data.decode(errors="replace")))
    for where, text in texts:
        for entry, rx in deny:
            if rx.search(text):
                problems.append(f"denylisted {entry!r} in {where}")
    return commits, problems


def push():
    url = git("remote", "get-url", REMOTE, check=False)
    if url not in ALLOWED_URLS:
        fail(f"remote {REMOTE!r} is {url or 'missing'}; expected one of {sorted(ALLOWED_URLS)}")
    ours = git("rev-parse", TARGET)
    remote_head = git("ls-remote", REMOTE, f"refs/heads/{BRANCH}").split()
    if remote_head:
        theirs = remote_head[0]
        if theirs == ours:
            print("GitHub is already up to date.")
            return
        if git("cat-file", "-t", theirs, check=False) != "commit" or \
                subprocess.run(["git", "merge-base", "--is-ancestor", theirs, ours]).returncode:
            fail(f"GitHub {BRANCH} ({theirs[:10]}) is not an ancestor of {ours[:10]}; "
                 "refusing a non-fast-forward push")
    r = subprocess.run(["git", "push", REMOTE, f"{TARGET}:refs/heads/{BRANCH}"])
    if r.returncode:
        sys.exit("push failed")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    kept, dropped = build()
    commits, problems = verify()
    head = git("rev-parse", TARGET)
    print(f"Built {TARGET} = {head[:10]}: {kept} commit(s), {dropped} private-only commit(s) dropped.")
    print("Published files at HEAD:")
    for p in git("ls-tree", "-r", "--name-only", TARGET).splitlines():
        print("  " + p)
    if problems:
        print("\nCHECKS FAILED:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("All checks passed.")
    if "--push" in sys.argv[1:]:
        push()
    else:
        print("Dry run. Re-run with --push to publish.")


if __name__ == "__main__":
    main()
