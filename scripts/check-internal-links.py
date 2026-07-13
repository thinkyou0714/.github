#!/usr/bin/env python3
"""Fail if any relative Markdown link points at a file/anchor that does not exist.

Scope: internal links only. http(s)://, mailto:, tel: and pure in-page anchors
(#section) are skipped — external URL liveness is out of scope (would add a flaky
network dependency). Catches the "doc links to a file that was never committed"
class of bug (e.g. a README pointing at a not-yet-added page).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# [text](target) — target up to the first whitespace or closing paren; ignore images? keep them too.
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def main() -> int:
    broken = []
    checked = 0
    for path in sorted(md_files()):
        base = os.path.dirname(path)
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for target in LINK.findall(line):
                    if target.startswith(SKIP_PREFIXES):
                        continue
                    file_part = target.split("#", 1)[0]
                    if not file_part:  # pure anchor already handled, but be safe
                        continue
                    resolved = os.path.normpath(os.path.join(base, file_part))
                    checked += 1
                    if not os.path.exists(resolved):
                        rel = os.path.relpath(path, ROOT)
                        broken.append(f"{rel}:{lineno}  ->  {target}")
    if broken:
        print("Broken internal Markdown links:")
        for b in broken:
            print(f"  {b}")
        return 1
    print(f"Internal Markdown links OK ({checked} relative links checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
