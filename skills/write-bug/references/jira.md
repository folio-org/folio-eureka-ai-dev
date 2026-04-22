# Markdown → Jira Markup

When filing the bug in Jira (directly or via `mcp-atlassian_jira_create_issue`
with a text description), convert Markdown to Jira markup.

## Headers
| Markdown | Jira |
|----------|------|
| `# Header` | `h1. Header` |
| `## Subheader` | `h2. Subheader` |
| `### Sub-subheader` | `h3. Sub-subheader` |

## Text formatting
| Markdown | Jira |
|----------|------|
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `` `code` `` | `{{code}}` |

## Lists
| Markdown | Jira |
|----------|------|
| `- item` | `* item` (unordered) |
| `1. item` | `# item` (ordered) |
| Nested L2 | `**` unordered, `##` ordered |
| Nested L3 | `***` unordered, `###` ordered |

## Code blocks
| Markdown | Jira |
|----------|------|
| ` ```java ` | `{code:java}...{code}` |
| ` ```json ` | `{code:json}...{code}` |
| ` ``` ` | `{code}...{code}` |

## Collapsible blocks

Markdown `<details>` has no Jira equivalent — use a `{code}` block (Jira renders it as a scrollable panel).

## Special characters
- Escape curly braces in URLs or path params: `{id}` → `\{id\}`.
- Horizontal rule `---` → `----` (four dashes).
- `@` followed by a name triggers mentions — escape as `\@` if unintended.

## Example

**Markdown**
```markdown
## Actual result
- Toast shows `Unable to update due to a module error`.
- PUT `/settings/entries` returns **403 Forbidden**.
```

**Jira**
```
h2. Actual result
* Toast shows {{Unable to update due to a module error}}.
* PUT {{/settings/entries}} returns *403 Forbidden*.
```

## When using the Jira MCP

`mcp-atlassian_jira_create_issue` accepts a Markdown `description`. On modern
Jira Cloud tenants the MCP converts it to ADF for you; on Server/DC or when in
doubt, feed it Jira markup (above) to avoid formatting surprises.
