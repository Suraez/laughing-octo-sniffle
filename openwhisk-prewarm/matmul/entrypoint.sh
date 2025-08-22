#!/bin/sh
set -eu

# Run the NumPy prewarm once; it will keep A, B, C referenced and resident.
python /prewarm.py &

# Hand off to the standard OpenWhisk runtime proxy
exec /bin/proxy
