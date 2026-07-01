# Browser Submission Retrieval

Use this workflow as the primary way to retrieve the user's past LeetCode submissions. It relies on the user's existing logged-in Chrome session instead of cookie-based direct API requests.

## Fast Path For LeetCode CN

Use this path when the user provides a LeetCode CN problem URL or a known `titleSlug`.

Performance rules:

- Avoid screenshots unless DOM extraction fails.
- Avoid exploratory clicking through tabs.
- Avoid dumping full page text.
- Use one browser session and direct navigation URLs.
- Extract only the first accepted submission link and the submitted code block.

1. Open the problem submission list:

```text
https://leetcode.cn/problems/<titleSlug>/submissions/
```

2. Parse the submission table from the DOM snapshot or a bounded read-only DOM evaluation.
   - Find the first link whose text includes `通过`.
   - Capture date, language, runtime, memory, and submission detail URL from that same link text.
   - Do not click rows one by one.

3. Open the submission detail URL directly.
   - Example path: `/problems/<titleSlug>/submissions/<submissionId>/`
   - Prefer direct `goto` over clicking the row.

4. Extract the code from a bounded DOM read.
   - Prefer code/pre blocks containing `class Solution`, `def `, `function`, `class Solution:`, or the submitted language's obvious solution wrapper.
   - Ignore problem examples, constraints, and the current editor stub.
   - If multiple identical code blocks are present, use one copy.

5. Use source label `user_submission`.
   - Include the submission date and language in source status.
   - Base the review on the extracted code structure.
   - Save the extracted submission to the local KB with `scripts/kb.py upsert` before answering.

## Slower Fallback

Use visible page navigation only when the fast path cannot locate the accepted link or submitted code block. Keep fallback bounded: inspect one submissions page and one detail page before reporting failure.

## Failure Handling

If no accepted row is visible, report `no accepted submission visible in browser`.

If the details page opens but no submitted code is visible, report `submission detail code unavailable`.

If the browser is not logged in, report `browser not logged in`.
