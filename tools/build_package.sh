#!/bin/bash
# Builds dist/TLM_nov_2026_final.zip (the show package) from package/. The venue base is
# a separate zip, dist/Plantagenet_Players_Base_2026_r1.zip (tools/build_base_package.py).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$ROOT/dist" "$STAGE/TLM_nov_2026_final_Package"
cp -a "$ROOT/package/." "$STAGE/TLM_nov_2026_final_Package/"
chmod +x "$STAGE/TLM_nov_2026_final_Package/ASSEMBLE_TLM_nov_2026_final.command"
rm -f "$ROOT/dist/TLM_nov_2026_final.zip"
(cd "$STAGE" && zip -qrX "$ROOT/dist/TLM_nov_2026_final.zip" TLM_nov_2026_final_Package)
echo "$ROOT/dist/TLM_nov_2026_final.zip"
