# Review Flow

## Source Priority

1. Local KB cache of the user's previous submission for the same problem
2. Browser-retrieved previous submission for the same problem
3. User's own notes, comments, or saved code snippets
4. Official solution/editorial
5. Canonical community explanation if no official editorial exists

## Retrieval Strategy

- Extract the problem `titleSlug` from the LeetCode URL.
- Run `scripts/kb.py lookup <problem-url-or-title-or-slug>` before any browser work.
- If lookup returns `found`, use the cached code immediately.
- If lookup returns `not_found`, use the fast logged-in browser workflow in `browser-submissions.md`, then write the extracted submission to the KB.
- If the user provides only a Chinese title, ask for or infer the LeetCode URL only when needed; direct URLs are fastest.
- Prefer accepted submissions and the most recent attempt if multiple versions exist.
- Record the retrieval result in the answer before explaining the algorithm.
- When reading code, infer the high-level idea from:
  - recursion shape
  - loop boundaries
  - state definitions
  - sorting or preprocessing steps
  - helper functions and naming

## Output Template

Use this structure:

1. Source status
2. Pattern
3. Old-submission idea or fallback idea
4. Why it works
5. Key implementation details
6. Pitfalls
7. Memory hook

## Source Labels

Use exactly one source label:

1. `user_submission_cache`: A past LeetCode submission was loaded from the local KB and inspected.
2. `user_submission`: A past LeetCode submission was retrieved from the browser, cached, and inspected.
3. `user_notes`: Local notes or saved code were found and inspected.
4. `official_editorial`: The official solution/editorial was used because no submission was available.
5. `canonical_solution`: A well-known standard solution was used because neither submission nor official editorial was available.
6. `inferred_without_submission`: The idea is inferred from common knowledge and no source was inspected.

Never call a section "Recovered idea" unless the source label is `user_submission_cache`, `user_submission`, or `user_notes`.

For fallback sources, write:

```text
Source status: no old submission inspected (<reason>). Fallback source: <label>.
```

For recovered submissions, write:

```text
Source status: old accepted submission inspected from <local KB/browser>. Source: <user_submission_cache/user_submission>.
```

Then continue with:

1. Pattern
2. Old-submission idea or fallback idea
3. Why it works
4. Key implementation details
5. Pitfalls
6. Memory hook

## Hint Style

- If the user's code is found, anchor every explanation to that code.
- If only the official solution is available, translate it into a practical reminder the user can reuse.
- Avoid large code dumps unless the user explicitly asks for code.
