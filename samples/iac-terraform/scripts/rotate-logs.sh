#!/usr/bin/env bash
set -euo pipefail
retention_days="${1:-30}"
find /var/log/app -name '*.log' -mtime +"$retention_days" -print -delete
