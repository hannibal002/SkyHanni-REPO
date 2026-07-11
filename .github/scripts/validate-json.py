#!/usr/bin/env python3

import json
import os
import random
import re

errors = 0
report = ""

with open(".github/outputs/all_changed_files.json", "r", encoding="utf-8") as fd:
    changed_files = json.load(fd)
for filename in changed_files:
    # Escape the filename for display in inline code
    if "`" in filename:
        delim = max(re.findall(r"`+", filename), key=len) + "`"
    else:
        delim = "`"

    try:
        with open(filename, "r", encoding="utf-8") as fd:
            json.load(fd)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"::error file={filename}::Invalid JSON")
        # Extra whitespace around delimiter is intentional for escaping purposes
        report += f"### {delim} {filename} {delim}\n{e}\n\n"
        errors += 1

if errors > 0:
    delim = random.randbytes(8).hex()
    assert delim not in report, "Delimiter was found in report. This should never happen."
    with open(os.environ["GITHUB_OUTPUT"], "w", encoding="utf-8") as fd:
        print(f"report<<{delim}", file=fd)
        print(report, file=fd)
        print(delim, file=fd)
        print("failed=true", file=fd)
