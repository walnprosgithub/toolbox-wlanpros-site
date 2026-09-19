#!/usr/bin/env python3
"""Fail the release push when index.html disagrees with the build it ships.

Why this exists. Twice now the page has made a claim the build contradicted and
nobody noticed until an outsider did:

  * "173 tools" sat on the page against a build shipping 185, caught by chance
    during the 1.10.0 deploy on 2026-09-17.
  * "New in 1.7" sat in an evergreen feature list through 1.8, 1.9 and 1.10.
    Matthew Casteel flagged it twice, on 2026-09-14 and 2026-09-19, and asked
    that the line be updated as part of each release push.

A request to remember something every release is a request that will be
forgotten. This is the mechanical version of it.

Everything it needs is in this repo: app/version.json and the tool help JSON
are both part of the built Flutter web app that ships under app/. No network,
no second checkout, no credentials.

Run it before pushing a release:  python3 scripts/check-version-text.py
Exit 0 = the page agrees with the build. Exit 1 = it does not, and the output
says which line.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
VERSION_JSON = ROOT / "app" / "version.json"
TOOL_HELP = ROOT / "app" / "assets" / "assets" / "help" / "tool_help.json"

# Version-shaped strings on the page that are CORRECT while pointing at an old
# release. Each needs a reason, because an un-explained exemption is how the
# next stale claim gets waved through. The full line is stored, not just the
# version, so that editing the line around the pin re-opens the question.
DELIBERATE_PINS = [
    (
        "v1.9.0",
        "The last universal (Intel) build. 1.10.0 is arm64-only after the Xcode 27 "
        "lipo regression, and the download link always serves the NEWEST release, "
        "so an Intel Mac needs this explicit fallback. It must NOT track the "
        "current version.",
    ),
]

# CSS carries version-shaped numbers that mean nothing of the sort:
# `h1 { font-size: 1.7rem; }` is the live example that a naive find-and-replace
# on "1.7" would have broken.
CSS_UNIT = re.compile(r"\d+\.\d+(rem|em|px|pt|vh|vw|ch|%|s\b)")


def fail(problems):
    print("FAIL: index.html disagrees with the build it ships.\n")
    for line_no, text, why in problems:
        print(f"  index.html:{line_no}")
        print(f"    {text.strip()[:160]}")
        print(f"    -> {why}\n")
    return 1


def main():
    for path in (PAGE, VERSION_JSON, TOOL_HELP):
        if not path.exists():
            print(f"FAIL: cannot run, {path.relative_to(ROOT)} is missing.")
            print("      The built app must be in place before this check means anything.")
            return 1

    shipping = json.loads(VERSION_JSON.read_text())["version"]
    tool_count = len(json.loads(TOOL_HELP.read_text())["tools"])
    lines = PAGE.read_text().splitlines()

    problems = []
    pins_seen = set()

    for i, line in enumerate(lines, 1):
        masked = CSS_UNIT.sub("", line)

        # A pin is written "v1.9.0" in the URL and "version 1.9.0" in the anchor
        # text of the same sentence, so match the bare number and exempt the
        # whole LINE rather than the literal string. Line scope is tight enough:
        # the pin and its explanation are one sentence on one line.
        pin_on_line = False
        for pin, _reason in DELIBERATE_PINS:
            if pin.lstrip("v") in masked:
                pins_seen.add(pin)
                pin_on_line = True

        # "New in 1.7" and friends: a novelty claim that names a version.
        for m in re.finditer(r"[Nn]ew in (\d+\.\d+(?:\.\d+)?)", masked):
            claimed = m.group(1)
            if not shipping.startswith(claimed):
                problems.append((
                    i, line,
                    f'claims "New in {claimed}" but the build ships {shipping}. '
                    f"Either drop the stamp (the feature is no longer new) or move "
                    f"it to what actually shipped in {shipping}.",
                ))

        # "version 1.8.2", "Toolbox 1.9" — an assertion about what is current.
        for m in [] if pin_on_line else re.finditer(r"(?:version|Toolbox)\s+v?(\d+\.\d+(?:\.\d+)?)", masked):
            claimed = m.group(1)
            if not (shipping.startswith(claimed) or claimed.startswith(shipping)):
                problems.append((
                    i, line,
                    f"names version {claimed} while the build ships {shipping}. "
                    f"If that is deliberate, add it to DELIBERATE_PINS with a reason.",
                ))

        # "180+ tools" must still bracket the real number: at or below it, and
        # not so far below that the claim has gone stale by a whole category.
        for m in re.finditer(r"(\d+)\+?\s+(?:Wi-Fi, RF, and network |Wi-Fi, RF and network )?tools", masked):
            claimed = int(m.group(1))
            plus = m.group(0).count("+") > 0
            if plus and not (claimed <= tool_count < claimed + 10):
                problems.append((
                    i, line,
                    f'claims "{claimed}+ tools" but the build carries {tool_count}. '
                    f"Round down to the nearest ten at or below {tool_count}.",
                ))
            elif not plus and claimed != tool_count:
                problems.append((
                    i, line,
                    f"claims an exact {claimed} tools but the build carries {tool_count}. "
                    f"Keith's standing rule is that an exact count over 100 is noise: "
                    f"write it as a rounded-down N+ instead.",
                ))

    for pin, reason in DELIBERATE_PINS:
        if pin not in pins_seen:
            problems.append((
                0, f"(expected somewhere in index.html: {pin})",
                f"this deliberate pin has vanished from the page. It was there for a "
                f"reason: {reason} If it is genuinely no longer needed, delete it from "
                f"DELIBERATE_PINS in this script too.",
            ))

    if problems:
        return fail(problems)

    print(f"PASS: index.html agrees with the build.")
    print(f"  shipping version : {shipping}")
    print(f"  tools in build   : {tool_count}")
    print(f"  deliberate pins  : {', '.join(p for p, _ in DELIBERATE_PINS)} (present, as intended)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
