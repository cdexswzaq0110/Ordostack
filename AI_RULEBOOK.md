# AI Rulebook

## Accuracy First

- State only verified facts.
- If information is unknown, say unknown.
- Do not invent implementation details.
- If a mistake is found, replace it with the corrected version directly.

## Work Scope

- Do exactly the requested issue.
- Do not expand the task into future phases.
- Ask for clarification when a critical input, output, environment, or constraint is missing.
- Do not use paid APIs.

## Safety Rules

- Do not commit secrets, tokens, API keys, ClearML credentials, AWS credentials, or `.env`.
- Do not delete local or cloud files without explicit user approval.
- Before any deletion, explain in Traditional Chinese exactly what files would be deleted and wait for consent.
- Do not push directly to `main`.
- Do not remove tests to make CI pass.

## Implementation Workflow

1. Read the project specification.
2. Read the relevant issue.
3. Identify affected files.
4. Provide an implementation plan.
5. Implement the smallest working version.
6. Add or update tests when meaningful.
7. Run verification commands.
8. Update documentation.
9. Summarize what changed and what remains.

## Review Format

Use this format for code review requests:

```text
【品味評分】🟢/🟡/🔴
【致命問題】直接指出最糟那段
【改進方向】消除特殊情況 / 簡化資料結構 / 10 行變 3 行
```

