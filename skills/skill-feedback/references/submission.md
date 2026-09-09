# Submission

How to publish an already approved feedback report. This reference covers transport only. The approved repository, label, title, and body are decided before you get here.

## 1. Normal path

Use an available GitHub issue-creation tool (connector, MCP server, or equivalent) for `folio-org/folio-eureka-ai-dev`.

- Read access is not evidence of write access.
- If no create capability exists, or its permission denial for this operation is already reliably known in the current context, skip it. Do not send a probe issue to find out.

## 2. Explicit denial

`403: Resource not accessible by integration` means the authentication path you used is not permitted to create the issue.

- Do not repeat the same create call after that response.
- Explain it briefly and correctly: the denial belongs to the connector's authentication path. A local `gh` install can use different credentials and permissions, so it may still succeed.
- Try an already configured `gh` when one is available.
- Do not try to repair permissions from this skill.

## 3. Do not generalize HTTP 403

Not every 403 is a permission denial. A rate-limit response is a throttling signal.

- Do not describe a rate limit as a connector permission failure.
- Do not work around a rate limit by immediately writing through another path.

## 4. CLI availability

A read-only check is acceptable when you need one:

```sh
gh auth status --active --hostname github.com
```

- Never pass `--show-token`.
- Authentication success, or a token that lists the `repo` scope, still does not guarantee issue creation in a specific repository.
- Do not run `auth login`, `auth refresh`, or `auth switch`. Do not change tokens, scopes, or settings. Do not print credentials.

## 5. Payload

Repository, label, title, and body must match the approved preview exactly.

- Do not append a footer, diagnostics, or new metadata on the fallback path.
- Do not silently drop the `skill-feedback` label because a tool makes it awkward.

## 6. Passing the body

Use structured arguments, or safely piped stdin. A temporary file is not a standard step; multi-line Markdown alone is not a reason to write one.

```sh
# approved_title and approved_body contain the already approved literal values.
printf '%s' "$approved_body" |
  gh issue create \
    --repo folio-org/folio-eureka-ai-dev \
    --label skill-feedback \
    --title "$approved_title" \
    --body-file -
```

Pass these values as data. Never use `eval` and never interpolate the Markdown as a shell program. Preserve Unicode, quotes, backticks, and line breaks exactly.

Write a file only when the available transport concretely requires one, or when the user separately asks to keep a copy of the artifact. In the first case use a unique path and delete only the file you created.

## 7. Uncertain write outcome

A timeout or a lost response does not tell you whether the issue was created.

1. Verify first through an available read path.
2. Check the repository, the full title and body, and the timing of the recent attempt — not just a similar-looking title.
3. If creation is confirmed, return the URL you found. Do not submit again.
4. If the outcome is still unknown, stop writing. Say the outcome is uncertain and hand over the approved artifact with a warning to check existing issues before submitting manually.

An empty search result immediately after a timeout is not conclusive evidence that no issue exists.

## 8. Manual fallback

When the available paths definitely did not create the issue, give the user the repository, label, title, and body for manual submission, and say plainly that the issue was not created.

- Never invent a URL.
- Do not repeat the approve/edit/cancel menu.

## 9. Success

Claim the issue was created only on a confirming tool result or read verification, and return the real URL.

## References

- `gh issue create`: https://cli.github.com/manual/gh_issue_create
- `gh auth status`: https://cli.github.com/manual/gh_auth_status
- GitHub REST error troubleshooting: https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api
