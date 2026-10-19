#!/bin/bash
# Daily microstock pipeline wrapper (run by cron script-only).
set -uo pipefail
set -a
. /root/.hermes/.env 2>/dev/null
set +a

export N_ASSETS="${N_ASSETS:-10}"
cd /root/microstock || exit 1

LOG=/root/microstock/last_cron.log
DAY=$(date +%F)
OUT=/root/microstock/output/$DAY

python3 pipeline.py > "$LOG" 2>&1
rc=$?

if [ $rc -ne 0 ]; then
  echo "❌ Microstock pipeline GAGAL (exit $rc). Log: $LOG"
  tail -5 "$LOG"
  exit $rc
fi

# success: generated AND uploaded to Drive (pipeline exits 0 only after upload OK)
# -> safe to remove local copy to save VPS disk.
N=$(grep -cE "assets -> Drive folder" "$LOG" || true)
rm -rf "$OUT"
echo "✅ Microstock $DAY: $N aset ter-upload → Drive folder 'Microstock/$DAY'. Lokal dibersihkan."