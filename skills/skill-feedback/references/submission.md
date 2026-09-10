# Submission

Transport only. The repository, label, title, and body were approved before you got
here; send exactly that, unchanged. Do not append a footer, diagnostics, or new
metadata on any path, and do not drop the `skill-feedback` label because a tool makes
it awkward.

## Choosing a path

Use an available GitHub issue-creation tool for `folio-org/folio-eureka-ai-dev`. Skip
it when no create capability exists, or when its denial for this operation is already
reliably known in this session — do not send a probe issue to find out. Read access is
not evidence of write access. Otherwise use an already configured `gh`.

`403: Resource not accessible by integration` means that authentication path may not
create the issue. Do not repeat the same call. Explain it briefly and correctly: the
denial belongs to that path, and a local `gh` can use different credentials, so it may
still succeed. A rate-limit 403 is a different thing — it is throttling, not a
permission problem, and not a reason to write through another path immediately.

`gh auth status --active --hostname github.com` is an acceptable read-only check;
never pass `--show-token`. Do not run `auth login`, `auth refresh`, or `auth switch`,
do not change tokens, scopes, or settings, and do not print credentials. Authentication
success still does not guarantee issue creation in a specific repository.

## Sending the body

Pass the body as data — structured arguments or piped stdin. Never use `eval` and never
interpolate the Markdown as a shell program. Preserve Unicode, quotes, backticks, and
line breaks exactly. A temporary file is not a standard step; multi-line Markdown is not
a reason to write one.

```sh
# approved_title and approved_body contain the already approved literal values.
printf '%s' "$approved_body" |
  gh issue create \
    --repo folio-org/folio-eureka-ai-dev \
    --label skill-feedback \
    --title "$approved_title" \
    --body-file -
```

## When the outcome is unclear

A timeout or a lost response does not tell you whether the issue was created. Verify by
reading first, matching the repository, the full title and body, and the timing of the
attempt — not just a similar-looking title. An empty result right after a timeout is not
conclusive. If creation is confirmed, return that URL and do not submit again. If the
outcome is still unknown, stop writing, say it is uncertain, and hand over the approved
artifact with a warning to check existing issues before submitting manually.

When no available path created the issue, give the user the repository, label, title,
and body, and say plainly that the issue was not created. Never invent a URL, and do not
repeat the approve/edit/cancel menu. Claim success only on a confirming tool result or
read verification, and return the real URL.

## References

- `gh issue create`: https://cli.github.com/manual/gh_issue_create
- `gh auth status`: https://cli.github.com/manual/gh_auth_status
- GitHub REST error troubleshooting: https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api
