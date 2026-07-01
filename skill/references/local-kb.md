# Local Knowledge Base

The local KB stores recovered user submissions so repeated reviews do not need browser access.

## Location

Default root:

```text
~/.leetcode-review
```

Submission records:

```text
~/.leetcode-review/submissions/<titleSlug>.json
```

Override the root with `LEETCODE_REVIEW_HOME` when needed.

## Commands

Look up a problem before browser work:

```bash
scripts/kb.py lookup https://leetcode.cn/problems/longest-substring-without-repeating-characters/
```

Write a browser-retrieved submission:

```bash
scripts/kb.py upsert < submission.json
```

List cached submissions:

```bash
scripts/kb.py list
```

Normalize cached code blocks after browser warmup:

```bash
scripts/kb.py normalize
```

Report Hot100 cache coverage:

```bash
scripts/kb.py coverage
```

Persist a browser warmup failure or success state:

```bash
scripts/kb.py mark-status <titleSlug> <status> --reason "..." --detail-url "..."
```

## Record Fields

Use these fields when saving a browser-retrieved submission:

```json
{
  "slug": "longest-substring-without-repeating-characters",
  "frontendId": "3",
  "titleCn": "无重复字符的最长子串",
  "source": "user_submission",
  "sourceUrl": "https://leetcode.cn/problems/longest-substring-without-repeating-characters/submissions/715083761/",
  "submissionId": "715083761",
  "status": "通过",
  "language": "Java",
  "runtime": "5 ms",
  "memory": "44.9 MB",
  "submittedAt": "2026.04.04 15:44",
  "code": "class Solution { ... }"
}
```

The script automatically adds aliases from the slug, title, and frontend id.

## Review Behavior

If `lookup` returns `found`, do not open Chrome. Use the cached `record.code` and source label `user_submission_cache`.

If `lookup` returns `not_found`, retrieve the submission through Chrome, save it with `upsert`, then review it with source label `user_submission`.

`lookup` also supports long input containing a cached title or slug. This is useful when the user pastes a problem statement instead of a clean URL.
