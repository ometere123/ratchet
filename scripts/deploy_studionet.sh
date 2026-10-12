#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x ./node_modules/.bin/genlayer ]]; then
  echo 'Install local stable CLI: npm install' >&2; exit 1
fi
version=$(./node_modules/.bin/genlayer --version 2>&1)
if [[ "$version" != *"0.39.1"* ]]; then
  echo "REFUSING: local CLI is not 0.39.1: $version" >&2; exit 1
fi
if grep -R -n -E 'studio-dev|studio-next|61997|0\.40\.0rc' --include='*.json' --include='*.yaml' --include='*.py' contracts gltest.config.yaml package.json .env.example 2>/dev/null; then
  echo 'REFUSING: preview network marker found in deployment input' >&2; exit 1
fi
node scripts/assert_studionet.mjs
./node_modules/.bin/genlayer network set studionet
./node_modules/.bin/genlayer network info
cat <<'EOF'
VERIFY visually: network=studionet, RPC=https://studio.genlayer.com/api, chain=61999.
Press Enter to deploy. Ctrl-C aborts. Check account and balance before proceeding.
EOF
read -r _
./node_modules/.bin/genlayer deploy --contract contracts/ratchet.py --rpc https://studio.genlayer.com/api
