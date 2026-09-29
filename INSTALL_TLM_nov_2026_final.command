#!/bin/bash
# =============================================================================
#  THE LITTLE MERMAID - Plantagenet Hall
#  Mac installer: TLM_nov_2026_final (show) + Plantagenet_Players_Base_2026_r1 (venue base)
#
#  1. Downloads the build files (GitHub) and the three media zips (Google Drive).
#     The Drive zips are private: if a direct download is refused, the installer opens
#     each Drive link in your browser (where you are signed in) and waits for the
#     downloads to land in ~/Downloads, then carries on by itself.
#  2. Builds the show folder  TLM_nov_2026_final  and the venue base folder
#     Plantagenet_Players_Base_2026_r1  (the base is kept separate from the show)
#  3. Checks everything: checksums, QLab files, every media file, base <-> show
#  4. Only if every check passes: puts both folders on your Desktop
#     (anything already there with the same name is moved aside, never deleted)
#
#  Run it: double-click. If macOS blocks it, right-click > Open, or in Terminal:
#      bash ~/Downloads/INSTALL_TLM_nov_2026_final.command
#  Uses only what comes with macOS (curl, unzip, shasum, plutil, afinfo, sips).
# =============================================================================

set -u

REPO="98blakemorgan-collab/Plantagenet"
BRANCH="claude/show-edits-review-snjxpj"
SHOW="TLM_nov_2026_final"
BASE="Plantagenet_Players_Base_2026_r1"
# Drive media zips: file name | Drive file id | size (MB)
MEDIA="TLM_R13_1.zip|15OaT4PWi4Kgf6bBrPhzhQipV2eL7bsS0|73
TLM_R13_1_SFX.zip|1nKFlB8RKVpuyaXVGNRTq2_tCIRFtW8G7|114
TLM_Backdrops_R10.zip|1ARjIs_QDMkfSYMU5DLv4-ZBks7bHIoVq|99"

STAMP="$(date +%Y%m%d_%H%M%S)"
WORK="${TLM_WORK:-$HOME/Downloads/TLM_install_$STAMP}"
DESK="${TLM_DESKTOP:-$HOME/Desktop}"
REPORT="$WORK/INSTALL_REPORT.txt"
FAILS=0

mkdir -p "$WORK"
: > "$REPORT"
say()  { echo "$*" | tee -a "$REPORT"; }
ok()   { say "  OK    $*"; }
bad()  { say "  FAIL  $*"; FAILS=$((FAILS + 1)); }
warn() { say "  NOTE  $*"; }
step() { say ""; say "== $* =="; }
sha()  { if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1; else sha256sum "$1" | cut -d' ' -f1; fi; }
is_zip() { [ -s "$1" ] && [ "$(head -c 2 "$1")" = "PK" ] && unzip -tq "$1" >/dev/null 2>&1; }
pause_exit() {
  say ""; say "Report: $REPORT"
  [ -n "${NONINTERACTIVE:-}" ] || { echo "Press Return to close."; read -r _ || true; }
  exit "$1"
}

say "THE LITTLE MERMAID - installer for $SHOW + $BASE"
say "$(date)"
say "Working folder: $WORK"

# -----------------------------------------------------------------------------
step "1. This Mac"
[ "$(uname -s)" = "Darwin" ] && ok "macOS $(sw_vers -productVersion 2>/dev/null)" || warn "not macOS - the Mac-only checks are skipped"
for t in curl unzip shasum; do
  command -v "$t" >/dev/null 2>&1 && ok "$t" || { command -v sha256sum >/dev/null 2>&1 && [ "$t" = shasum ] && ok "sha256sum"; } || bad "$t is missing"
done
free_gb="$(df -g "$HOME" 2>/dev/null | awk 'NR==2 {print $4}')"
[ -n "$free_gb" ] && { [ "$free_gb" -ge 3 ] && ok "$free_gb GB free" || bad "only $free_gb GB free (need about 3 GB)"; }
[ -d "/Applications/QLab.app" ] && ok "QLab is installed" || warn "QLab.app not found in /Applications - install QLab 5 before the show"
[ "$FAILS" = 0 ] || pause_exit 1

# -----------------------------------------------------------------------------
step "2. Build files from GitHub ($REPO, $BRANCH)"
SRC_ZIP="$WORK/build_files.zip"
if [ -n "${TLM_SOURCE_ZIP:-}" ]; then
  cp "$TLM_SOURCE_ZIP" "$SRC_ZIP"
else
  curl -fL --retry 3 --progress-bar -o "$SRC_ZIP" "https://codeload.github.com/$REPO/zip/refs/heads/$BRANCH"
fi
if is_zip "$SRC_ZIP"; then ok "downloaded ($(du -h "$SRC_ZIP" | cut -f1))"; else bad "could not download the build files - check the internet connection"; pause_exit 1; fi
unzip -q -o "$SRC_ZIP" -d "$WORK/src"
SRC="$(find "$WORK/src" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
[ -d "$SRC/package/$SHOW" ] && ok "show package found" || { bad "no package/$SHOW in the download"; pause_exit 1; }
[ -d "$SRC/base/$BASE" ] && ok "base package found" || { bad "no base/$BASE in the download"; pause_exit 1; }

# -----------------------------------------------------------------------------
step "3. Media zips from Google Drive"
PKG="$WORK/show_package"
mkdir -p "$PKG"
cp -R "$SRC/package/." "$PKG/"

# A copy already on this Mac: Downloads (also "name (1).zip" from a repeat download), next to this script
find_local() {  # $1 zip name -> path of a complete copy, or nothing
  stem="${1%.zip}"
  for f in "$HOME/Downloads/$1" "$HOME/Downloads/$stem ("*").zip" "$HOME/Downloads/$stem-"*.zip \
           "$(dirname "$0")/$1" "${TLM_MEDIA_DIR:-/nonexistent}/$1"; do
    is_zip "$f" && { echo "$f"; return 0; }
  done
  return 1
}
# Direct download - works when the Drive file is shared "Anyone with the link"
drive_get() {  # $1 id, $2 destination
  url="https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t"
  curl -fsL --retry 2 -c "$WORK/.cookies" -b "$WORK/.cookies" -o "$2.part" "$url" || return 1
  if ! is_zip "$2.part" && grep -q 'name="uuid"' "$2.part" 2>/dev/null; then   # large-file confirm page
    uuid="$(grep -o 'name="uuid" value="[^"]*"' "$2.part" | head -n 1 | sed 's/.*value="//; s/"$//')"
    curl -fsL --retry 2 -c "$WORK/.cookies" -b "$WORK/.cookies" -o "$2.part" "$url&uuid=$uuid" || return 1
  fi
  is_zip "$2.part" && mv "$2.part" "$2"
  rm -f "$2.part"
  [ -f "$2" ]
}

need=""
while IFS='|' read -r name id mb; do
  [ -z "$name" ] && continue
  if f="$(find_local "$name")"; then cp "$f" "$PKG/$name"; ok "$name (found on this Mac: $f)"; continue; fi
  say "  downloading $name (about $mb MB) ..."
  if drive_get "$id" "$PKG/$name"; then ok "$name downloaded ($(du -h "$PKG/$name" | cut -f1))"; else need="$need $name|$id|$mb"; fi
done <<EOF_MEDIA
$MEDIA
EOF_MEDIA

if [ -n "$need" ]; then
  say ""
  say "  These zips are private on Google Drive, so your browser has to fetch them"
  say "  (you are signed in there). For each tab that opens, click Download."
  say "  Leave the file in Downloads - do not let the browser unzip it."
  for item in $need; do
    name="${item%%|*}"; rest="${item#*|}"; id="${rest%%|*}"
    say "    $name   https://drive.google.com/file/d/$id/view"
    [ -n "${NONINTERACTIVE:-}" ] || open "https://drive.google.com/file/d/$id/view" 2>/dev/null
  done
  say "  Waiting for the downloads (checked every 5 s, up to 45 min) ..."
  tries=0
  while [ -n "$need" ] && [ "$tries" -lt "${TLM_WAIT_TRIES:-540}" ]; do
    left=""
    for item in $need; do
      name="${item%%|*}"
      if f="$(find_local "$name")"; then cp "$f" "$PKG/$name"; ok "$name arrived ($(du -h "$PKG/$name" | cut -f1))"; else left="$left $item"; fi
    done
    need="$left"
    [ -n "$need" ] && { sleep 5; tries=$((tries + 1)); }
  done
fi
for z in $(echo "$MEDIA" | cut -d'|' -f1); do
  is_zip "$PKG/$z" || { bad "$z not downloaded (or damaged)"; }
done
[ "$FAILS" = 0 ] || { say "Download the missing zip(s) from Drive into Downloads and run this again - it picks them up."; pause_exit 1; }

# -----------------------------------------------------------------------------
step "4. Build the show folder ($SHOW)"
NONINTERACTIVE=1 bash "$PKG/ASSEMBLE_$SHOW.command" > "$WORK/assemble.log" 2>&1
asm=$?
sed 's/^/    /' "$PKG/OUTPUT/ASSEMBLY_REPORT.txt" >> "$REPORT" 2>/dev/null
OUTSHOW="$PKG/OUTPUT/$SHOW"
[ "$asm" = 0 ] && ok "assembler finished: all media placed, show checksums OK" || bad "assembler reported problems (see the assembly report above)"

# -----------------------------------------------------------------------------
step "5. Build the venue base ($BASE)"
OUTBASE="$WORK/base_out/$BASE"
mkdir -p "$WORK/base_out"
cp -R "$SRC/base/$BASE" "$OUTBASE"
[ -f "$OUTBASE/$BASE.mtr" ] && [ -f "$OUTBASE/$BASE.qlab5" ] && ok "base files copied" || bad "base files missing"

# -----------------------------------------------------------------------------
step "6. Check everything"
json_sha() {  # $1 json file, $2 key -> 64-hex value
  grep -o "\"$2\": *\"[0-9a-f]\{64\}\"" "$1" | head -n 1 | grep -o "[0-9a-f]\{64\}"
}
# show checksums (independently of the assembler)
for k in qlab:"$SHOW.qlab5" mantra:"$SHOW.mtr"; do
  key="${k%%:*}"; f="${k#*:}"
  want="$(json_sha "$OUTSHOW/BUILD_METADATA.json" "$key")"
  [ -f "$OUTSHOW/$f" ] && [ "$(sha "$OUTSHOW/$f")" = "$want" ] && ok "show $f checksum" || bad "show $f checksum"
done
for k in mantra_base:"$BASE.mtr" qlab_base:"$BASE.qlab5"; do
  key="${k%%:*}"; f="${k#*:}"
  want="$(json_sha "$OUTBASE/BASE_METADATA.json" "$key")"
  [ "$(sha "$OUTBASE/$f")" = "$want" ] && ok "base $f checksum" || bad "base $f checksum"
done
# QLab workspaces are valid property lists
if command -v plutil >/dev/null 2>&1; then
  for f in "$OUTSHOW/$SHOW.qlab5" "$OUTBASE/$BASE.qlab5"; do
    plutil -lint -s "$f" >/dev/null 2>&1 && ok "$(basename "$f") opens as a valid QLab file" || bad "$(basename "$f") is not a valid plist"
  done
fi
# Mantra size footers
for f in "$OUTSHOW/$SHOW.mtr" "$OUTBASE/$BASE.mtr"; do
  want="$(tail -n 5 "$f" | grep '^Size=' | cut -d= -f2 | tr -d '\r')"
  have="$(wc -c < "$f" | tr -d ' ')"
  [ "$want" = "$have" ] && ok "$(basename "$f") size footer ($have bytes)" || bad "$(basename "$f") footer $want, file $have"
done
# the show is built on the base: shared sections must be identical
section() {  # $1 file, $2 exact section name -> its lines
  awk -v s="[$2]" '$0==s {p=1; next} /^\[/ {p=0} p' "$1"
}
same=0; diff_n=0
names="CustomFixtures Patch Network RigView RecentColours LiveScene"
for i in 0 1 2 3 4 5 6 7 8 9 100 101 102 103 104 105 106 107 108 109; do
  names="$names Memory$i $(grep -o "^\[Memory$i-Cue[0-9]*\]" "$OUTBASE/$BASE.mtr" | tr -d '[]' | tr '\n' ' ')"
done
for n in $names; do
  if [ "$(section "$OUTSHOW/$SHOW.mtr" "$n")" = "$(section "$OUTBASE/$BASE.mtr" "$n")" ]; then same=$((same + 1)); else diff_n=$((diff_n + 1)); say "        differs: [$n]"; fi
done
[ "$diff_n" = 0 ] && ok "show file matches the venue base in all $same shared sections (patch, fixtures, network, P1, 100-109)" || bad "$diff_n shared sections differ between show and base"
# every media file QLab uses is present and readable
man="$OUTSHOW/${SHOW}_MEDIA_MANIFEST.csv"
total=0; missing=0; unreadable=0
while IFS= read -r rel; do
  rel="$(printf '%s' "$rel" | tr -d '\r')"; [ -z "$rel" ] && continue
  total=$((total + 1)); f="$OUTSHOW/$rel"
  if [ ! -s "$f" ]; then missing=$((missing + 1)); say "        missing: $rel"; continue; fi
  case "$rel" in
    *.wav|*.mp3|*.aif*) command -v afinfo >/dev/null 2>&1 && ! afinfo "$f" >/dev/null 2>&1 && { unreadable=$((unreadable + 1)); say "        cannot read audio: $rel"; } ;;
    *.jpg|*.png) command -v sips >/dev/null 2>&1 && ! sips -g pixelWidth "$f" >/dev/null 2>&1 && { unreadable=$((unreadable + 1)); say "        cannot read image: $rel"; } ;;
    *.mp4|*.mov) head -c 16 "$f" | LC_ALL=C grep -q ftyp || { unreadable=$((unreadable + 1)); say "        not a video file: $rel"; } ;;
  esac
done < <(tail -n +2 "$man")
[ "$total" = 80 ] && [ "$missing" = 0 ] && [ "$unreadable" = 0 ] && ok "all 80 media files present and readable" || bad "media: $total listed, $missing missing, $unreadable unreadable"
# the base is not inside the show folder
leak="$(find "$OUTSHOW" -maxdepth 2 \( -name "$BASE*" -o -name "BASE_SHOW_2026*" \) | head -n 1)"
[ -z "$leak" ] && ok "no venue base files inside the show folder" || bad "base file inside the show folder: $leak"
# no old-named show files carried in from the Drive zips
old="$(find "$OUTSHOW" -maxdepth 1 \( -name "TLM_Show_R13_1.qlab5" -o -name "TLM_SHOW_2026_R13_FLASHY_SCENE_SPLIT.mtr" -o -name "R13_*" \) | head -n 1)"
[ -z "$old" ] && ok "no superseded R13 control files in the show folder" || bad "old control file in the show folder: $old"

if [ "$FAILS" != 0 ]; then
  say ""; say "NOT INSTALLED: $FAILS check(s) failed. Nothing on the Desktop was changed."
  say "The built folders are in $WORK for inspection."
  pause_exit 1
fi

# -----------------------------------------------------------------------------
step "7. Put both folders on the Desktop"
mkdir -p "$DESK"
for pair in "$OUTSHOW|$SHOW" "$OUTBASE|$BASE"; do
  src="${pair%%|*}"; name="${pair#*|}"
  if [ -e "$DESK/$name" ]; then
    mkdir -p "$DESK/Old_TLM_versions"
    mv "$DESK/$name" "$DESK/Old_TLM_versions/${name}_before_$STAMP"
    warn "moved the old $name to Desktop/Old_TLM_versions/${name}_before_$STAMP"
  fi
  mv "$src" "$DESK/$name" && ok "Desktop/$name" || bad "could not move $name to the Desktop"
done
# re-check the control files where they now live
[ "$(sha "$DESK/$SHOW/$SHOW.qlab5")" = "$(json_sha "$DESK/$SHOW/BUILD_METADATA.json" qlab)" ] && ok "show workspace checked on the Desktop" || bad "show workspace changed during the move"
[ "$(sha "$DESK/$BASE/$BASE.mtr")" = "$(json_sha "$DESK/$BASE/BASE_METADATA.json" mantra_base)" ] && ok "venue base checked on the Desktop" || bad "base changed during the move"
cp "$REPORT" "$DESK/$SHOW/INSTALL_REPORT.txt" 2>/dev/null

say ""
if [ "$FAILS" = 0 ]; then
  say "INSTALLED AND CHECKED."
  say "  Desktop/$SHOW   open $SHOW.qlab5; follow 00_START_HERE.txt from step 3"
  say "  Desktop/$BASE   venue base: docs/${BASE}_Guide.pdf"
  say "The downloads are in $WORK (safe to delete once you are happy)."
  [ -n "${NONINTERACTIVE:-}" ] || open "$DESK/$SHOW" 2>/dev/null
  pause_exit 0
fi
pause_exit 1
