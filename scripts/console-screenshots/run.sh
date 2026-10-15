#!/bin/sh
# Regenerates public/screenshots/console/*.svg by driving a real gg console
# against a fake control plane that serves invented example data.
#
#   scripts/console-screenshots/run.sh /path/to/gg
#
# Needs Python 3 and the pyte package (pip install pyte==0.8.2). Nothing here
# touches the person's own gg session: gg runs with a throwaway home directory.
set -eu

gg="${1:?usage: run.sh /path/to/gg}"
here="$(cd "$(dirname "$0")" && pwd)"
out="$here/../../public/screenshots/console"
work="$(mktemp -d)"
port=8765

python3 "$here/fakeplane.py" "$port" 2>"$work/fakeplane.log" &
plane=$!
trap 'kill $plane 2>/dev/null; rm -rf "$work"' EXIT
sleep 1

home() {
  mkdir -p "$1/.config/good-grief" "$1/state" "$1/cache"
  printf '{"HOME":"%s","XDG_CONFIG_HOME":"%s/.config","XDG_STATE_HOME":"%s/state","XDG_CACHE_HOME":"%s/cache","GG_CONTROL_PLANE":"http://127.0.0.1:%s"}' "$1" "$1" "$1" "$1" "$port"
}

script() {  # name, env-json, steps-key
  python3 - "$here/shots.json" "$gg" "$2" "$3" "$folder" > "$work/$1.json" <<'PY'
import json, sys
shots = json.load(open(sys.argv[1]))
print(json.dumps({"cmd": [sys.argv[2]], "env": json.loads(sys.argv[3]), "cwd": sys.argv[5],
                  "rows": shots["rows"], "cols": shots["cols"], "steps": shots[sys.argv[4]]}))
PY
}

# THE FOLDER the new-agent menu names ("Claude Code here: <folder>"), so pick a neutral one.
folder="${GG_SCREENSHOT_FOLDER:-/Users/Shared/web-app}"
mkdir -p "$folder"

# A STAND-IN FOR CLAUDE CODE, named claude so the mux gives it activity marks.
mkdir -p "$work/bin"
cp "$here/fake-claude" "$work/bin/claude"
chmod +x "$work/bin/claude"

script out "$(home "$work/out")" signedOut
home "$work/in" >/dev/null
printf '{"SessionToken":"example","ExpiresAt":"2099-01-01T00:00:00+00:00","TenantId":"00000000-0000-0000-0000-000000000001","PrincipalDisplay":"Ada Lovelace"}' \
  > "$work/in/.config/good-grief/session.json"
script in "$(home "$work/in")" signedIn
agents_env="$(home "$work/in" | sed "s|}\$|,\"GG_TAKE_COMMAND\":\"$work/bin/claude\",\"GG_SCREENSHOT_GG\":\"$gg\",\"GG_SCREENSHOT_COUNT\":\"$work/agents\"}|")"
script agents "$agents_env" agents

python3 "$here/shoot.py" "$work/out.json" "$work/shots"
python3 "$here/shoot.py" "$work/in.json" "$work/shots"
python3 "$here/shoot.py" "$work/agents.json" "$work/shots"
mkdir -p "$out"
cp "$work"/shots/*.svg "$out/"
echo "Screenshots written to public/screenshots/console/. Check them before committing."
