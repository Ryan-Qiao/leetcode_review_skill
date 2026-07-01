#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.codex/skills/leetcode-review"
mkdir -p "$HOME/.leetcode-review"

rsync -a --delete "$repo_dir/skill/" "$HOME/.codex/skills/leetcode-review/"
rsync -a --delete "$repo_dir/kb/" "$HOME/.leetcode-review/"

echo "Installed leetcode-review skill to $HOME/.codex/skills/leetcode-review"
echo "Installed LeetCode review KB to $HOME/.leetcode-review"
