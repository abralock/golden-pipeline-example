#!/usr/bin/env bash
# Checks that apply to EVERY repo, including YAML/shell/IaC-only repos.
# Each check runs only if matching files exist, so no repo needs to "opt out".
set -uo pipefail

# Generated output and dependencies are never scanned (same list in gitleaks.toml / yamllint.yml).
prune=(-path ./.git -o -path ./node_modules -o -path ./vendor -o -path ./.venv -o -path ./.next
       -o -path ./dist -o -path ./build -o -path ./target -o -path ./.gradle -o -path ./reports)
rc=0
run() { echo "::: $*"; "$@" || rc=1; }

# 1. Secrets - always
gl_cfg="$(dirname "$0")/gitleaks.toml"
[[ -f .gitleaks.toml ]] && gl_cfg=.gitleaks.toml
run gitleaks dir . --redact --no-banner --config "$gl_cfg"

# 2. Shell scripts
mapfile -d '' sh_files < <(find . \( "${prune[@]}" \) -prune -o -type f -name '*.sh' -print0)
(( ${#sh_files[@]} )) && run shellcheck --severity=warning "${sh_files[@]}"

# 3. YAML (pipelines, k8s manifests, config)
if [[ -n "$(find . \( "${prune[@]}" \) -prune -o -type f \( -name '*.yml' -o -name '*.yaml' \) -print -quit)" ]]; then
  cfg="${YAMLLINT_CONFIG:-$(dirname "$0")/yamllint.yml}"
  [[ -f .yamllint || -f .yamllint.yml ]] && cfg=""   # repo may override with a stricter config
  run yamllint ${cfg:+-c "$cfg"} .
fi

# 4. IaC security (Terraform, Bicep, Helm, K8s, Dockerfiles)
if [[ -n "$(find . \( "${prune[@]}" \) -prune -o -type f \( -name '*.tf' -o -name '*.bicep' \
      -o -name 'Chart.yaml' -o -name 'kustomization.yaml' -o -name 'Dockerfile' \) -print -quit)" ]]; then
  run checkov -d . --compact --quiet --skip-download --skip-path node_modules --skip-path .next
fi

# Rollout phase 1: QG_MODE=warn reports findings but never blocks.
if (( rc )) && [[ "${QG_MODE:-enforce}" == "warn" ]]; then
  echo "WARN: static checks failed - not blocking because QG_MODE=warn (will block after cut-over date)"
  exit 0
fi
exit $rc
