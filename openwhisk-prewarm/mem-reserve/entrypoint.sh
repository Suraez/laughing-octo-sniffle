#!/bin/sh
set -eu

# Start a background Python process that holds PREWARM_RESERVE_MIB in RAM
if [ "${PREWARM_RESERVE_MIB:-0}" -gt 0 ] 2>/dev/null; then
  python /prewarm.py "${PREWARM_RESERVE_MIB}" &
fi

# Hand off to the standard OpenWhisk runtime proxy
exec /bin/proxy
