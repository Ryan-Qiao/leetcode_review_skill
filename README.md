# leetcode-review

Personal Codex skill and local LeetCode review knowledge base.

This repository contains:

- `skill/`: the Codex skill, review strategy, browser workflow, and KB script.
- `kb/`: cached Hot100 submission records and warmup status files.

## Install on another computer

Clone the repository, then run:

```bash
./install.sh
```

The script copies:

- `skill/` to `~/.codex/skills/leetcode-review`
- `kb/` to `~/.leetcode-review`

## Verify

```bash
~/.codex/skills/leetcode-review/scripts/kb.py list
~/.codex/skills/leetcode-review/scripts/kb.py coverage
```

## Update from the current machine

After adding more local submissions:

```bash
rsync -a --delete ~/.codex/skills/leetcode-review/ ./skill/
rsync -a --delete ~/.leetcode-review/ ./kb/
git status
git add skill kb
git commit -m "Update leetcode review data"
git push
```
