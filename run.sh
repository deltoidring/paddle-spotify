#!/usr/bin/env bash

set -euo pipefail

TAG="local"
TARGET="${TARGET:-downloader}"

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cd "$SCRIPT_DIR"

echo "⏳  Building docker image"
docker build -q -t "$TAG" . >/dev/null
echo "✔️ Built docker image"

docker run -e SPOTIFY_CLIENT_ID="$SPOTIFY_CLIENT_ID" \
  -e SPOTIFY_CLIENT_SECRET="$SPOTIFY_CLIENT_SECRET" \
  --rm -v "$SCRIPT_DIR:/src" "$TAG" "paddle.${TARGET}" "$@"
