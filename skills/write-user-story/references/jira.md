# JIRA Markup Conversion

When creating user stories in JIRA, convert Markdown formatting to JIRA markup syntax:

## Headers
| Markdown | JIRA |
|----------|------|
| `# Header` | `h1. Header` |
| `## Subheader` | `h2. Subheader` |
| `### Sub-subheader` | `h3. Sub-subheader` |

## Text Formatting
| Markdown | JIRA |
|----------|------|
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `` `code` `` | `{{code}}` |

## Lists
| Markdown | JIRA |
|----------|------|
| `- item` | `* item` (unordered) |
| `1. item` | `# item` (ordered) |
| Nested (2nd level) | `**` for unordered, `##` for ordered |
| Nested (3rd level) | `***` for unordered, `###` for ordered |

## Code Blocks
| Markdown | JIRA |
|----------|------|
| ` ```java ` | `{code:java}...{code}` |
| ` ```json ` | `{code:json}...{code}` |
| ` ``` ` (plain) | `{code}...{code}` |

## Special Characters
- Escape curly braces in URLs: `{id}` → `\{id\}`
- Horizontal rules: `---` → `----` (four dashes)

## Example Conversion

**Markdown:**
```markdown
## Requirements
**Functional Requirements:**
- System shall store `audit_date` field
- API returns timestamps in ISO 8601 format
```

**JIRA:**
```
h2. Requirements
*Functional Requirements:*
* System shall store {{audit_date}} field
* API returns timestamps in ISO 8601 format
```
