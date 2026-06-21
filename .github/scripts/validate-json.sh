#!/usr/bin/env bash

set -euo pipefail

errors=0
report=""
mapfile -t FILES <<< "$CHANGED_FILES"
for file in "${FILES[@]}"; do
    [[ -z "$file" ]] && continue
    result=$(python3 -m json.tool "$file" 2>&1 > /dev/null) || true
    if [ -n "$result" ]; then
        echo "::error file=$file::Invalid JSON"
        report="${report}### \`${file}\`"$'\n'"${result}"$'\n\n'
        errors=$((errors + 1))
    fi
done
if [ "$errors" -gt 0 ]; then
    delim="EOF_$(openssl rand -hex 16)"
    {
        echo "report<<$delim"
        printf '%s\n' "$report"
        echo "$delim"
    } >> "$GITHUB_OUTPUT"
    echo "failed=true" >> "$GITHUB_OUTPUT"
fi
