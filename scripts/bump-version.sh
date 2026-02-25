#!/usr/bin/env bash
# Auto-bump date-based version if unchanged from HEAD.
# Called by pre-commit hook — modifies pyproject.toml + uv.lock so the
# commit fails on first attempt; re-stage and commit again to proceed.
# [Created with AI: Claude Code with Opus 4.6]
set -euo pipefail

head_ver=$(git show HEAD:pyproject.toml 2>/dev/null | grep '^version = ' | cut -d'"' -f2) || head_ver=""
curr_ver=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [ "$head_ver" = "$curr_ver" ]; then
  new_ver=$(TZ=America/Los_Angeles date '+%Y.%m.%d.%H%M')
  sed -i "s/^version = .*/version = \"$new_ver\"/" pyproject.toml
  uv sync --dev >/dev/null 2>&1
  echo "Auto-bumped version to $new_ver — run: git add pyproject.toml uv.lock && git commit"
fi
