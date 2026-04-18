#!/usr/bin/env bash

set -euo pipefail

errors=0
report=""
read -ra FILES <<< "$CHANGED_FILES"
for file in "${FILES[@]}"; do
    result=$(python3 -m json.tool "$file" 2>&1 > /dev/null) || true
    if [ -n "$result" ]; then
        echo "::error file=$file::Invalid JSON"
        report="${report}### \`${file}\`\n${result}\n\n"
        errors=$((errors + 1))
    fi
done
if [ "$errors" -gt 0 ]; then
    {
        echo "report<<EOF"
        echo -e "$report"
        echo "EOF"
    } >> "$GITHUB_OUTPUT"
    echo "failed=true" >> "$GITHUB_OUTPUT"
fi
