#!/bin/bash
# THE LITTLE MERMAID - R13.1 show folder assembler
#
# Builds one complete TLM_R13_REBUILT_Show_Files folder from:
#   - the edited R13.1 control files shipped in this package (always win)
#   - the three media zips from the Drive folder TLM_R13:
#       TLM_R13_1.zip, TLM_R13_1_SFX.zip, TLM_Backdrops_R10.zip
#
# Usage: put the three zips in the same folder as this script, then
# double-click it (or run:  bash ASSEMBLE_R13_1.command).
# Nothing outside this folder is changed.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
SHOW="TLM_R13_REBUILT_Show_Files"
CONTROL="$HERE/$SHOW"
OUT="$HERE/OUTPUT/$SHOW"
WORK="$HERE/.assemble_work"
REPORT="$HERE/OUTPUT/ASSEMBLY_REPORT.txt"
ZIPS="TLM_R13_1.zip TLM_R13_1_SFX.zip TLM_Backdrops_R10.zip"

QLAB_SHA="5dca0842f16f9c12c096e4389d939a564bca6a3d874619dd3fa97eda1bcb86ab"
MTR_SHA="95cf3c690c2cef573c58e761f27eb54491f3e102684a1ab3f597a232fcae24c2"

say() { echo "$*" | tee -a "$REPORT"; }
sha() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1; else sha256sum "$1" | cut -d' ' -f1; fi; }
finish() { echo; echo "Report: $REPORT"; echo "Press Return to close."; read -r _ || true; exit "$1"; }

if [ -e "$OUT" ]; then
  echo "OUTPUT/$SHOW already exists. Move or delete the OUTPUT folder and run again."
  finish 1
fi
mkdir -p "$HERE/OUTPUT"
: > "$REPORT"
say "TLM R13.1 assembly - $(date)"
say "Package folder: $HERE"
say ""

# 1. Check the source zips are present.
missing_zip=0
for z in $ZIPS; do
  if [ -f "$HERE/$z" ]; then say "found   $z"; else say "MISSING $z"; missing_zip=1; fi
done
if [ "$missing_zip" = 1 ]; then
  say ""
  say "Download the missing zip(s) from the Drive folder TLM_R13 into this folder"
  say "(see SOURCE_ZIPS.csv), then run this again."
  finish 1
fi

# 2. Extract each zip into its own work folder.
rm -rf "$WORK"; mkdir -p "$WORK"
for z in $ZIPS; do
  say "extracting $z ..."
  if ! unzip -q -o "$HERE/$z" -d "$WORK/${z%.zip}"; then
    say "ERROR: could not extract $z (is the download complete?)"
    finish 1
  fi
done
# Drop macOS metadata.
find "$WORK" -name "__MACOSX" -type d -prune -exec rm -rf {} + 2>/dev/null
find "$WORK" -name ".DS_Store" -type f -delete 2>/dev/null

# 3. Layer the folders. Edited control files go in first; later layers never
#    overwrite a file that is already there (cp -n), so the edited QLab/Mantra
#    files and the newest media always win.
mkdir -p "$OUT"
cp -R "$CONTROL/." "$OUT/"

merge_tree() {  # $1 = extracted zip root
  local root="$1" base
  # Prefer a TLM_R13_REBUILT_Show_Files folder; else any folder holding media/;
  # else the zip root itself.
  base="$(find "$root" -type d -name "$SHOW" | head -n 1)"
  if [ -z "$base" ]; then
    base="$(find "$root" -type d -name media | head -n 1)"
    [ -n "$base" ] && base="$(dirname "$base")"
  fi
  [ -z "$base" ] && return 0
  say "merging $(echo "${base#$WORK/}")"
  (cd "$base" && find . -type d) | while IFS= read -r d; do mkdir -p "$OUT/$d"; done
  (cd "$base" && find . -type f) | while IFS= read -r f; do
    [ -e "$OUT/$f" ] || cp -p "$base/$f" "$OUT/$f"
  done
}
for z in $ZIPS; do merge_tree "$WORK/${z%.zip}"; done

# 4. Place every manifest file at its exact path. Anything still missing is
#    looked up by file name anywhere in the extracted zips.
say ""
say "Checking the 80 media files QLab uses (R13_MEDIA_MANIFEST.csv) ..."
placed=0; found_by_name=0; missing=0
tail -n +2 "$OUT/R13_MEDIA_MANIFEST.csv" | tr -d '\r' | while IFS= read -r rel; do
  [ -z "$rel" ] && continue
  if [ -f "$OUT/$rel" ]; then echo "ok"; continue; fi
  name="$(basename "$rel")"
  src="$(find "$WORK" -type f -name "$name" | head -n 1)"
  [ -z "$src" ] && src="$(find "$WORK" -type f -iname "$name" | head -n 1)"
  if [ -n "$src" ]; then
    mkdir -p "$OUT/$(dirname "$rel")"; cp -p "$src" "$OUT/$rel"
    echo "moved"; echo "  placed by name: $rel" >> "$REPORT"
  else
    echo "missing"; echo "  MISSING: $rel" >> "$REPORT"
  fi
done > "$WORK/results.txt"
placed=$(grep -c '^ok$' "$WORK/results.txt")
found_by_name=$(grep -c '^moved$' "$WORK/results.txt")
missing=$(grep -c '^missing$' "$WORK/results.txt")
say "  in place: $placed   found by name: $found_by_name   missing: $missing"

# 5. The spare Q063-5 finale sound (optional cue) - place it if supplied.
spare="media/audio/06_Magic/Q063-5_SFX_Finale_Transition_Magic.wav"
if [ ! -f "$OUT/$spare" ]; then
  src="$(find "$WORK" -type f -name "$(basename "$spare")" | head -n 1)"
  [ -n "$src" ] && mkdir -p "$OUT/$(dirname "$spare")" && cp -p "$src" "$OUT/$spare"
fi

# 6. Verify the show control files are the checked R13.1 versions.
say ""
q="$(sha "$OUT/TLM_Show_R13_1.qlab5")"; m="$(sha "$OUT/TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr")"
if [ "$q" = "$QLAB_SHA" ]; then say "QLab   TLM_Show_R13_1.qlab5 - checksum OK"; else say "QLab   checksum MISMATCH ($q)"; missing=$((missing+1)); fi
if [ "$m" = "$MTR_SHA" ];  then say "Mantra .mtr - checksum OK"; else say "Mantra checksum MISMATCH ($m)"; missing=$((missing+1)); fi

# 7. Warn about the old R11 folder (old aliases in the workspace can find it).
for d in "$HOME/Desktop/TLM_R11_FLASHY_Show_Files" "$HOME/TLM_R11_FLASHY_Show_Files"; do
  [ -d "$d" ] && say "Note: $d still exists. R13.1 no longer uses it, but renaming it avoids confusion."
done

rm -rf "$WORK"
say ""
if [ "$missing" = 0 ]; then
  say "DONE. Complete show folder: OUTPUT/$SHOW"
  say "Next: move it to your Desktop (named exactly $SHOW),"
  say "open TLM_Show_R13_1.qlab5 and follow 00_START_HERE.txt from step 3."
  finish 0
else
  say "INCOMPLETE: $missing problem(s) listed above. Nothing was deleted;"
  say "fix the source zip(s) and run again after removing the OUTPUT folder."
  finish 1
fi
