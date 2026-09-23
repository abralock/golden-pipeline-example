#!/usr/bin/env bash
# Decide which quality profile a repo gets.
#   code    -> full gates: contract, unit tests, coverage, build
#   iac     -> lint + IaC security scan, no coverage gate
#   scripts -> shellcheck + secret scan, no coverage gate
#   config  -> yamllint + secret scan, no coverage gate
#
# Priority: explicit "kind:" in repo.yaml  >  auto-detection by files.
# Output: prints PROFILE=<value> and writes it to ${PROFILE_FILE:-profile.env}
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

declared=""
if [[ -f repo.yaml ]]; then
  declared="$(awk -F':[[:space:]]*' '/^kind:/{print $2; exit}' repo.yaml | awk '{print $1}')"
fi

# Build manifests that mean "this repo contains application code"
code_markers=(pom.xml build.gradle build.gradle.kts settings.gradle settings.gradle.kts package.json
              go.mod pyproject.toml setup.py '*.csproj' Cargo.toml)

has_file() {  # has_file <pattern...> : true if any match within depth 4
  local args=() p
  for p in "$@"; do args+=(-name "$p" -o); done
  unset 'args[${#args[@]}-1]'
  [[ -n "$(find . -maxdepth 4 \( -path ./node_modules -o -path ./.git -o -path ./vendor \) -prune \
            -o -type f \( "${args[@]}" \) -print -quit)" ]]
}

detected="config"
if   has_file "${code_markers[@]}";                   then detected="code"
elif has_file '*.tf' '*.bicep' 'Chart.yaml' 'kustomization.yaml'; then detected="iac"
elif has_file '*.sh' '*.ps1';                         then detected="scripts"
fi

profile="${declared:-$detected}"

case "$profile" in
  service|library|code) profile="code" ;;
  iac|scripts|config)   ;;
  *) echo "ERROR: unknown kind '$profile' in repo.yaml (use service|library|iac|scripts|config)" >&2; exit 2 ;;
esac

if [[ -z "$declared" ]]; then
  echo "WARN: no repo.yaml found - using auto-detected profile '$profile'. Please add repo.yaml." >&2
elif [[ "$profile" != "$detected" && "$detected" == "code" ]]; then
  # Someone declared iac/scripts but the repo has build manifests -> possible gate dodging.
  echo "ERROR: repo.yaml says '$declared' but build manifests were found. Code repos cannot opt out of coverage." >&2
  exit 3
fi

echo "PROFILE=$profile"
echo "PROFILE=$profile" > "${PROFILE_FILE:-profile.env}"
