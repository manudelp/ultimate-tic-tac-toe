#!/usr/bin/env bash
# Shallow checkout of arnowaczynski/utttai (Apache-2.0). Used as the rules
# oracle and, once weights are present, as the NMCTS2 opponent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/third_party/utttai"
if [[ -d "$DEST/.git" ]]; then
  git -C "$DEST" pull --ff-only
else
  mkdir -p "$ROOT/third_party"
  git clone --depth 1 https://github.com/arnowaczynski/utttai.git "$DEST"
fi
echo "uttt.ai is at $DEST"
