#!/usr/bin/env python3
"""Reformat cv.yaml in place: consistent indentation, long text wrapped as >- blocks.

Keeps the leading comment block. Refuses to write if the result does not load
back to exactly the same data.
"""

import json
import re
import sys
import textwrap
from pathlib import Path

import yaml

WIDTH = 88
PLAIN_OK = re.compile(r"^[A-Za-z0-9(][^#]*$")


def scalar(s, col, child):
    """Render a string whose first line starts at column col; wrapped lines at child."""
    if not s.isprintable() or s != s.strip() or "\n" in s:
        return json.dumps(s)  # JSON strings are valid YAML double-quoted scalars
    if len(s) + col <= WIDTH and PLAIN_OK.match(s) and ": " not in s and not s.endswith(":"):
        try:
            if yaml.safe_load(s) == s:
                return s
        except yaml.YAMLError:
            pass
    if len(s) + col + 2 <= WIDTH:
        return json.dumps(s)
    pad = " " * child
    # Folded blocks join lines with one space, so only break at single spaces.
    lines = textwrap.wrap(s, WIDTH - child, break_long_words=False,
                          break_on_hyphens=False)
    if " ".join(lines) != s:
        return json.dumps(s)
    return ">-\n" + "\n".join(pad + l for l in lines)


def has_list(d):
    return isinstance(d, dict) and any(isinstance(v, list) for v in d.values())


def emit(node, indent, out):
    pad = " " * indent
    if isinstance(node, dict):
        prev_scalar = False
        for i, (k, v) in enumerate(node.items()):
            nested = isinstance(v, (dict, list))
            # Blank line between top-level keys, except runs of short scalars.
            if indent == 0 and i and (nested or not prev_scalar or ">-" in out[-1]
                                      or out[-1].startswith("  ")):
                out.append("")
            if nested:
                out.append(f"{pad}{k}:")
                emit(v, indent + 2, out)
            else:
                val = v if not isinstance(v, str) else scalar(v, indent + len(k) + 2, indent + 2)
                out.append(f"{pad}{k}: {val}")
            prev_scalar = not nested
    else:
        for i, item in enumerate(node):
            if isinstance(item, dict):
                if i and has_list(item):
                    out.append("")
                sub = []
                emit(item, indent + 2, sub)
                sub[0] = pad + "- " + sub[0][indent + 2:]
                out.extend(sub)
            else:
                out.append(f"{pad}- {scalar(item, indent + 2, indent + 2)}")


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "cv.yaml")
    text = path.read_text()
    data = yaml.safe_load(text)
    header = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            header.append(line)
        else:
            break
    while header and not header[-1].strip():
        header.pop()
    out = []
    emit(data, 0, out)
    result = "\n".join(header + [""] + out) + "\n"
    if yaml.safe_load(result) != data:
        sys.exit("fmt_yaml: formatted output does not round-trip; not writing")
    path.write_text(result)


if __name__ == "__main__":
    main()
