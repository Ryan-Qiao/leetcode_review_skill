# Hot100 Warmup

Use this workflow to populate the local KB from LeetCode Hot100.

## Artifacts

Hot100 manifest:

```text
~/.leetcode-review/hot100.json
```

Coverage report:

```text
~/.leetcode-review/hot100-coverage.json
```

Cached submissions:

```text
~/.leetcode-review/submissions/<titleSlug>.json
```

## Browser Warmup Rules

- Use the official Hot100 page: `https://leetcode.cn/studyplan/top-100-liked/`.
- Parse `#__NEXT_DATA__` to collect the 100 problem records.
- For each problem not already cached, open `/problems/<slug>/submissions/`.
- Open the latest accepted submission detail when visible.
- Extract submitted code from the detail page tail after `全部提交记录` and `代码`.
- Save each recovered submission with `scripts/kb.py upsert` or equivalent JSON writes following the local KB schema.

## Coverage

Run:

```bash
scripts/kb.py coverage
```

The report includes `cached`, `lastStatus`, `reason`, and `detailUrl` for each problem. The expected result is not necessarily 100/100 because unsolved Hot100 problems have no accepted submission to cache, and a few accepted detail pages can fail code extraction if LeetCode changes page rendering.

Common statuses:

- `cached`: latest accepted submission was saved locally.
- `no_accepted_submission_visible`: Chrome did not show an accepted row for this problem.
- `submission_detail_code_unavailable`: an accepted detail page opened but the submitted code block could not be extracted.
- `browser_not_logged_in`: Chrome is not logged in to LeetCode CN.
