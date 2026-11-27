#!/usr/bin/env bash
# Copy the data the server needs from this repo into a server checkout, then print the RE commit
# so the server commit can name what it was copied from.
# usage: tools/sync-server.sh [<server-checkout>]   (default: ../pinata next to this repo)
set -euo pipefail
re=$(cd "$(dirname "$0")/.." && pwd)
server=${1:-$re/../pinata}
[ -d "$server" ] || { echo "no server checkout at $server" >&2; exit 1; }
! grep -rlq "^version https://git-lfs" "$re/Files/Server/2016/9Data" || { echo "9Data holds LFS pointers: run git lfs pull" >&2; exit 1; }
mkdir -p "$server/original-data/9Data" "$server/test/fixtures"
for d in Shine ServerInfo; do
  rm -rf "${server:?}/original-data/9Data/$d"
  cp -R "$re/Files/Server/2016/9Data/$d" "$server/original-data/9Data/$d"
done
cp "$re/docs/protocol/opcodes.json" "$server/test/fixtures/opcodes.json"
echo "copied from pinata-re $(git -C "$re" rev-parse HEAD)$(git -C "$re" diff --quiet HEAD -- Files/Server/2016/9Data docs/protocol/opcodes.json || echo ' (with uncommitted changes)')"
