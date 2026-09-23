#!/usr/bin/env bash
# Validate an MR/PR title. With squash-merge the title becomes the commit
# message on main, so this is the only commit message we need to police.
#
# Format:  <type>(<scope>)?: <summary> <work-item>
# Example: feat(payment): add refund API AB#12345
#          fix: null check on customer lookup PAY-812
set -euo pipefail

title="${1:-}"
types='feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert'
# Azure Boards (AB#123) or Jira-style key (PAY-123)
workitem='(AB#[0-9]+|[A-Z][A-Z0-9]+-[0-9]+)'

fail=0
if [[ ! "$title" =~ ^($types)(\([a-z0-9._-]+\))?!?:\ .{5,} ]]; then
  echo "ERROR: title must start with '<type>(<scope>): <summary>'  (types: ${types//|/, })" >&2
  fail=1
fi
if [[ ! "$title" =~ $workitem ]]; then
  echo "ERROR: title must reference a work item, e.g. AB#12345 or PAY-812" >&2
  fail=1
fi
if (( ${#title} > 100 )); then
  echo "ERROR: title is ${#title} chars, max 100" >&2
  fail=1
fi

if (( fail )); then
  echo "Title was: '$title'" >&2
  exit 1
fi
echo "OK: '$title'"
