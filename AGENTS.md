# Repository Guidelines

## Purpose

This repository is a skills registry for FOLIO AI-assisted workflows. The main
deliverables are installable skills under `skills/`, role-based install commands
in `README.md`, and onboarding documentation under `docs/onboarding/`.

## Skills Ecosystem

Keep this repository compatible with the `skills` CLI and skills.sh discovery.
When changing skill structure, metadata, or installation docs, check the current
documentation first:

- https://www.skills.sh/docs
- https://www.skills.sh/docs/cli
- https://agentskills.io/specification

## Skill Changes

When adding, renaming, or removing a skill under `skills/`:

- Update the `README.md` available skills list.
- Update role-based install commands in `README.md` when the skill belongs to a role preset.
- Update relevant onboarding docs if the skill changes setup or expected workflows.
- Explicitly document why a public skill is excluded from role presets if it should not be installed by any role.
- Keep `skill-feedback` in every role preset.

## Skill Authoring

When creating or substantially editing a skill, use the `writing-skills` skill if
it is available. If it is not available, follow the Agent Skills specification
and existing repository patterns.

Each skill must live under `skills/<skill-name>/` and include `SKILL.md`. The
`name` frontmatter must match the directory name and use lowercase hyphenated
naming. The `description` should be specific enough for agents to know when to
load the skill.

Keep `SKILL.md` focused. Move large examples, templates, or domain references
into the skill's `references/` directory.

## Validation

Before completing skill or installation-doc changes:

- Run `npx skills add . --list` to confirm the local checkout exposes the expected skills through the skills CLI.
- Check that every skill name used in role install commands exists under `skills/`.
- Review the diff for stale install instructions or onboarding text.

After changes are merged, use `npx skills add folio-org/folio-eureka-ai-dev --list`
if you need to confirm the published GitHub source is discoverable.
