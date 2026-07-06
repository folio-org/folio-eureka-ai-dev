# FOLIO Developer Resource Map

All URLs fetched and verified 2026-07-04.

## dev.folio.org (developer portal)

| URL | Contents |
| --- | --- |
| https://dev.folio.org/guidelines/ | Contribution guidelines: GitHub Flow, PR checklists, naming conventions, breaking-changes policy, release procedures, Officially Supported Technologies per release, Code of Conduct |
| https://dev.folio.org/guides/ | Guide index: setup, getting started, API reference docs, module development bases (Stripes FE, BE frameworks), development tips, DevOps, community |
| https://dev.folio.org/source-code/map/ | Full repo map with the prefix taxonomy: `ui-`, `ui-plugin-`, `ui-handler-`, `stripes-`, `platform-`, `mod-`, `mgr-`, `app-`, `edge-` and what each category contains |
| https://dev.folio.org/guidelines/naming-conventions/ | Module/interface/permission/JSON/endpoint naming rules; 31-byte module name limit; version tag format |
| https://dev.folio.org/community/ | Community channels: Slack signup, issue tracker, GitHub org, wiki, SIG list |

## FOLIO wiki (folio-org.atlassian.net, Confluence)

| URL | Contents |
| --- | --- |
| https://folio-org.atlassian.net/wiki/spaces/PLATFORM/pages/193134643 | **Eureka Platform Overview**: Kong, Keycloak, Quarkus sidecars, the three managers, application formalization, roles/capabilities model |
| https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/866811992 | **Introduction to the Architecture** (Eureka): core components, Kafka event-driven communication, sidecar ingress/egress |
| https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/509149215 | **folio-module-sidecar** deep dive: bootstrap sequence, runtime Kafka events, the 9 ingress filters, module prefix strategies, signing key rotation. Note: plain HTTP fetch returns only page chrome — use the Confluence API/MCP to read content |
| https://folio-org.atlassian.net/wiki/spaces/FOLIJET/overview | **Development Teams space**: directory of teams (Spitfire, Firebird, Thunderjet, Folijet, …) with POs/Team Leads, technical guides |
| https://folio-org.atlassian.net/wiki/spaces/REL/pages/5210256 | **Responsibility matrix** (Module / JIRA project / Team / PO / Dev Lead) — the authoritative "which team owns which module" table; also flags per-module BE framework, DB/Kafka usage, Eureka-vs-Okapi status |
| https://folio-org.atlassian.net/wiki/spaces/TC/overview | **Technical Council**: standards, decision records, RFC process |

Known dead link: `…/wiki/display/REL/Team+vs+module+responsibility+matrix` (legacy
display-style URL, still referenced from several wiki pages) → use the
`/spaces/REL/pages/5210256` URL above instead.

## Source code

| URL | Contents |
| --- | --- |
| https://github.com/folio-org | FOLIO GitHub org (~465 repos) |
| https://github.com/folio-org/folio-module-sidecar | Sidecar source + README (env vars, security flows) |
| https://github.com/folio-org/applications-poc-tools | Shared Eureka backend libs (folio-auth-openid, folio-backend-common/-testing, secret store) |
| https://github.com/folio-org/eureka-platform-bootstrap | Docker-based minimal Eureka platform for local runs |
| https://github.com/folio-org/folio-eureka-ai-dev | This skill registry: AI agent skills + team guidelines |

## Community / support

- Slack: workspace `folio-project.slack.com`, self-invite at https://slack-invitation.folio.org
- Issue tracker (Jira): https://folio-org.atlassian.net/jira
- SIGs (Special Interest Groups): listed under the Product Council wiki

## Lookup recipes

- "Which team owns mod-X?" → responsibility matrix (REL/5210256).
- "How does auth/routing actually work?" → Eureka Platform Overview, then the
  sidecar page for filter-level detail.
- "What does prefix Y mean / where is the repo for Z?" → source-code map.
- "What are the platform coding/naming rules?" → dev.folio.org guidelines.
