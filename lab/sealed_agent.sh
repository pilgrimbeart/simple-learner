#!/bin/bash
# sealed_agent.sh: run a blind agent in an enforced seal (the user, 2026-11-14: agents have repeatedly read what they shouldn't, so
# isolation must be enforced, not requested). bubblewrap gives the agent a private filesystem holding only:
#   the system's programs and libraries (/usr, /etc), read-only;
#   a fresh, empty home with nothing but a copy of the login credential (no memory, no history, no project settings, no ~/.claude.json);
#   the claude program, read-only;
#   a Python environment of its own (~/.cache/sealed_venv, built from requirements.txt plus scipy), read-only, at /opt/venv;
#   its work folder, the one writable place, at /home/agent/work.
# The repository, the user's home, memory and transcripts do not exist inside. Network is shared (the API and web search need it).
# Usage: lab/sealed_agent.sh WORKDIR PROMPTFILE OUTFILE [TOOLS] [MODEL]
#   WORKDIR: a folder prepared with everything the agent may see (bundle any engine files into it: never point at the repository)
#   TOOLS: claude's --tools list (default Read,Write,Edit,Bash,WebSearch,WebFetch)
set -e
WORK=$(readlink -f "$1"); PROMPT=$(readlink -f "$2"); OUT=$3
TOOLS=${4:-Read,Write,Edit,Bash,WebSearch,WebFetch}
MODEL=${5:-sonnet}
CLAUDE_BIN=$(readlink -f "$(which claude)")
VENV=$HOME/.cache/sealed_venv
CRED=$(mktemp -d /tmp/sealcred_XXXXXX)
cp "$HOME/.claude/.credentials.json" "$CRED/.credentials.json"
bwrap --unshare-all --share-net --die-with-parent --new-session \
  --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/sbin /sbin \
  --ro-bind /etc /etc --ro-bind /mnt/wsl/resolv.conf /mnt/wsl/resolv.conf \
  --proc /proc --dev /dev --tmpfs /tmp \
  --tmpfs /home --dir /home/agent --dir /home/agent/.local --dir /home/agent/.local/bin \
  --bind "$CRED" /home/agent/.claude \
  --ro-bind "$CLAUDE_BIN" /home/agent/.local/bin/claude \
  --ro-bind "$VENV" /opt/venv \
  --bind "$WORK" /home/agent/work \
  --setenv HOME /home/agent --setenv PATH /opt/venv/bin:/home/agent/.local/bin:/usr/bin:/bin --setenv USER agent \
  --unsetenv OLDPWD \
  --chdir /home/agent/work \
  /home/agent/.local/bin/claude -p --setting-sources "" --strict-mcp-config --no-session-persistence --model "$MODEL" \
    --tools "$TOOLS" --allowedTools "$TOOLS" < "$PROMPT" > "$OUT" 2> "$OUT.err" || true
rm -rf "$CRED"
