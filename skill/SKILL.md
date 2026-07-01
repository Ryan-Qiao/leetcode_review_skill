---
name: leetcode-review
description: Analyze LeetCode or Codetop problems by first looking up the user's local LeetCode submission knowledge base, then using the user's logged-in Chrome browser only to fill missing cache entries, reviewing recovered code logic when available, and explicitly falling back to official/editorial explanations only after local and browser submission retrieval fail. Use when the user asks to review, revisit, recall, or explain a LeetCode problem they have solved before, especially when they want fast hints grounded in their previous code and clear source attribution.
---

# Leetcode Review

## Goal

Recover the reasoning behind the user's old accepted solution whenever possible. Never imply that an idea came from the user's history unless a prior submission was actually retrieved and inspected.

## Workflow

1. Identify the problem precisely.
   - Capture the title, number, URL, and any visible tags or constraints.
   - Extract the LeetCode `titleSlug` from URLs such as `/problems/longest-substring-without-repeating-characters/`.

2. Look up the local knowledge base first.
   - Run `scripts/kb.py lookup <problem-url-or-title-or-slug>`.
   - If the record is found and contains code, review that code immediately. Do not open Chrome.
   - Use source label `user_submission_cache`.

3. If the local KB misses, retrieve the user's submission with Chrome and cache it.
   - Use the fast logged-in Chrome/browser workflow in `references/browser-submissions.md`.
   - When the user provides a LeetCode URL, go directly to the submissions URL and parse the latest accepted detail link without interactive clicking.
   - After extracting submitted code, write it to the local KB with `scripts/kb.py upsert`.
   - Do not use cookie-based direct GraphQL fetching as the primary path.
   - Prefer the latest accepted submission for the same problem.

4. If user code is available, review it through the user's logic.
   - Explain the idea in the user's own terms when possible.
   - Point out invariants, transitions, edge cases, and why the code works.
   - Do not jump straight to a fresh solution if a past solution can be recovered.

5. If no usable submission can be found, say why before using fallback sources.
   - Examples: browser not logged in, submission list unavailable, no accepted submission found, submission detail code unavailable.
   - Do not use the label "Recovered idea" for fallback content.

6. Use official or canonical references only after the local KB and browser retrieval attempts.
   - Read the official explanation/editorial first when available.
   - If there is no official editorial, use the most authoritative canonical explanation available.
   - Convert the source into hints, not a verbatim solution dump.

7. Return output in this order.
   - Source status
   - Problem type and key pattern
   - Old-submission idea or fallback idea
   - Why it works
   - Critical implementation details
   - Common pitfalls
   - A short memory hook for future recall

## Hinting Rules

- Prefer hints that point the user toward the next missing insight.
- Escalate from light hint to direct explanation only when the user asks for more detail.
- If the user's old code has a bug, explain the bug relative to their own structure rather than rewriting everything immediately.
- If the problem is already familiar, keep the review terse and focus on the non-obvious part.
- Always label the source as one of: `user_submission_cache`, `user_submission`, `user_notes`, `official_editorial`, `canonical_solution`, or `inferred_without_submission`.
- If the source is neither `user_submission_cache` nor `user_submission`, explicitly state that no old submission was inspected.

## References

- See [review-flow.md](references/review-flow.md) for the fallback order and output template.
- See [browser-submissions.md](references/browser-submissions.md) for the logged-in Chrome submission retrieval workflow.
- See [local-kb.md](references/local-kb.md) for the local knowledge-base schema and commands.
- See [warmup-hot100.md](references/warmup-hot100.md) for the Hot100 prefetch workflow and coverage report.
