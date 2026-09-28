#!/bin/bash
# Builds dist/TLM_R13_1_Package.zip from package/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$ROOT/dist" "$STAGE/TLM_R13_1_Package"
cp -a "$ROOT/package/." "$STAGE/TLM_R13_1_Package/"
chmod +x "$STAGE/TLM_R13_1_Package/ASSEMBLE_R13_1.command"
rm -f "$ROOT/dist/TLM_R13_1_Package.zip"
(cd "$STAGE" && zip -qrX "$ROOT/dist/TLM_R13_1_Package.zip" TLM_R13_1_Package)
echo "$ROOT/dist/TLM_R13_1_Package.zip"
