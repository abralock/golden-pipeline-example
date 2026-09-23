#!/usr/bin/env bash
# Verify the repo implements the Makefile contract.
# Every code repo must expose these targets, whatever the language.
set -euo pipefail

REQUIRED_TARGETS=(setup lint test coverage build)

if [[ ! -f Makefile ]]; then
  echo "ERROR: Makefile missing. Copy a starter from ci-templates/contract/ and adapt it." >&2
  exit 1
fi

# Dump make's rule database once. A target only counts if it has a recipe
# (being listed in .PHONY alone is not enough; that fooled a naive `make -n` check).
db="$(make -pRrq -f Makefile : 2>/dev/null || true)"

has_recipe() {
  awk -v t="$1" '
    $0 ~ "^"t":" { inblk=1; next }
    inblk && /^$/ { inblk=0 }
    inblk && /recipe to execute/ { found=1 }
    END { exit !found }' <<<"$db"
}

missing=()
for t in "${REQUIRED_TARGETS[@]}"; do
  has_recipe "$t" || missing+=("$t")
done

if (( ${#missing[@]} )); then
  echo "ERROR: Makefile is missing required targets: ${missing[*]}" >&2
  exit 1
fi

echo "OK: Makefile contract satisfied (${REQUIRED_TARGETS[*]})"
