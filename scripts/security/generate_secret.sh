#!/usr/bin/env bash
set -euo pipefail
bytes="${1:-32}"
if ! [[ "$bytes" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 [byte-length]" >&2
    exit 1
fi
python3 -c "import secrets; print(secrets.token_urlsafe(${bytes}))"