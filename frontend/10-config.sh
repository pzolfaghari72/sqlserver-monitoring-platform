#!/bin/sh
set -eu
cat > /usr/share/nginx/html/config.runtime.js <<EOF
window.MONITORING_API_KEY = "${MONITORING_API_KEY}";
EOF