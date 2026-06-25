#!/usr/bin/env bash
# Blocks dangerous rm commands before they execute.
# Receives tool input JSON on stdin from Claude Code.

input=$(cat)

# Extract the bash command — handle both possible JSON structures
_py_extract() {
    "$1" -c "
import sys, json
d = json.load(sys.stdin)
cmd = d.get('tool_input', {}).get('command') or d.get('command', '')
print(cmd)
" 2>/dev/null
}

if command -v jq &>/dev/null; then
    cmd=$(echo "$input" | jq -r '(.tool_input.command // .command) // ""')
elif cmd=$(echo "$input" | _py_extract python3 2>/dev/null) && [ -n "$cmd" ]; then
    : # python3 worked
elif cmd=$(echo "$input" | _py_extract python 2>/dev/null) && [ -n "$cmd" ]; then
    : # python worked
elif cmd=$(echo "$input" | _py_extract py 2>/dev/null) && [ -n "$cmd" ]; then
    : # py launcher worked
else
    # Pure-bash fallback: extract value of "command" key via sed
    cmd=$(echo "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

dangerous=false
reason=""

# Strip comment-only lines so "# rm -f bad" doesn't false-positive
safe_cmd=$(echo "$cmd" | grep -v '^\s*#')

# rm -rf (recursive + force, any flag order: -rf, -fr, -Rf, etc.)
# Both alternatives must be anchored to \brm\b to avoid matching grep -Fr, tar -xfr, etc.
if echo "$safe_cmd" | grep -qE '\brm\b.*-[a-zA-Z]*[rR][a-zA-Z]*[fF]|\brm\b.*-[a-zA-Z]*[fF][a-zA-Z]*[rR]'; then
    dangerous=true
    reason="rm -rf detected"
    exit 2  # Blocking error: tool call is prevented
fi

# rm -r (recursive only)
if echo "$safe_cmd" | grep -qE '\brm\b.*-[a-zA-Z]*[rR]'; then
    dangerous=true
    reason="rm -r detected"
    exit 2  # Blocking error: tool call is prevented
fi

# rm -f (force only)
if echo "$safe_cmd" | grep -qE '\brm\b.*-[a-zA-Z]*[fF]'; then
    dangerous=true
    reason="rm -f detected"
    exit 2  # Blocking error: tool call is prevented
fi

# rm * (wildcard)
if echo "$safe_cmd" | grep -qE '\brm\b[^#\n]*\*'; then
    dangerous=true
    reason="rm * detected"
    exit 2  # Blocking error: tool call is prevented
fi

# Remove-Item -Recurse -Force (PowerShell rm -rf equivalent)
if echo "$safe_cmd" | grep -qiE 'Remove-Item\b.*-[A-Za-z]*Recurse[A-Za-z]*.*-[A-Za-z]*Force|Remove-Item\b.*-[A-Za-z]*Force[A-Za-z]*.*-[A-Za-z]*Recurse'; then
    dangerous=true
    reason="Remove-Item -Recurse -Force detected"
    exit 2
fi

# Remove-Item -Recurse (recursive only)
if echo "$safe_cmd" | grep -qiE 'Remove-Item\b.*-[A-Za-z]*Recurse'; then
    dangerous=true
    reason="Remove-Item -Recurse detected"
    exit 2
fi

# Remove-Item -Force (force only)
if echo "$safe_cmd" | grep -qiE 'Remove-Item\b.*-[A-Za-z]*Force'; then
    dangerous=true
    reason="Remove-Item -Force detected"
    exit 2
fi

# Remove-Item * (wildcard)
if echo "$safe_cmd" | grep -qiE 'Remove-Item\b[^#\n]*\*'; then
    dangerous=true
    reason="Remove-Item * detected"
    exit 2
fi

if [ "$dangerous" = true ]; then
    echo "{\"decision\": \"block\", \"reason\": \"Blocked: dangerous rm command ($reason). Use exact file paths or a safer deletion method.\"}"
    exit 1
fi

exit 0
