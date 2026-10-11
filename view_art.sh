#!/usr/bin/env bash
# ==============================================================================
#  CYBERPUNK RETRO GRID GIRL // FULL-BODY TERMINAL PHOSPHOR DISPLAY
# ==============================================================================
set -euo pipefail

PHOSPHOR_FG="\033[38;2;117;184;112m"
BRIGHT_FG="\033[1;38;2;160;235;155m"
RESET="\033[0m"

clear 2>/dev/null || true

printf "${PHOSPHOR_FG}"
cat << "HEADER"
╔══════════════════════════════════════════════════════════════════════════════════╗
║  [SYSTEM: NEURAL INTERFACE ONLINE]               GRID FREQ: 9PX PHOSPHOR METRIC  ║
║  TARGET: OPERATOR_09 // HEAD-TO-TOE FULL BODY    DISPLAY: FULL EDGE-TO-EDGE CRT  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
HEADER

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ART_FILE="${SCRIPT_DIR}/assets/braille_fullbody.txt"

if [ -f "$ART_FILE" ]; then
    printf "${PHOSPHOR_FG}"
    cat "$ART_FILE"
    printf "${RESET}\n"
else
    echo "Art file not found."
fi

printf "${PHOSPHOR_FG}"
cat << "FOOTER"
════════════════════════════════════════════════════════════════════════════════════
 [STATUS: FULL STANDING FIGURE // FEET & FLOOR ACTIVE] // PHOSPHOR CRT // READY
════════════════════════════════════════════════════════════════════════════════════
FOOTER
printf "${RESET}\n"
