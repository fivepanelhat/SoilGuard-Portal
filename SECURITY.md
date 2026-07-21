# Security Policy for SoilGuard-Portal

## Food Sovereignty & Infrastructure Warning
This portal manages physical agricultural telemetry and irrigation logic for Coastal Alpine Tech Limited. Access to the `main` branch is strictly restricted to authorized architects.

## Reporting a Vulnerability
We treat agricultural system vulnerabilities as critical. A flaw here impacts physical crops and food sovereignty. 
If you discover a vulnerability in SoilGuard's authentication, telemetry ingestion, or MQTT bridging, DO NOT open a public issue. 
Report it directly to the Chief Architect.

## Security Notifications

| Channel | Response |
| ------- | -------- |
| Dependabot | Weekly dependency PRs - prioritise `security` / high CVEs |
| Code scanning / SecOps / Red team | Fix-forward on `main`; never weaken actuator guards |
| Coastal-Alpine-Core advisories | Bump core pin; re-run portal tests |
| Org threat register | See coastal-alpine-stack `SECURITY.md` / `SECURITY_POSTURE_REPORT.md` |

## Active threat patches (2026-07)

| ID / finding | Mitigation |
| ------------ | ---------- |
| GHSA-f4xh-w4cj-qxq8 langsmith | Floor `>=0.8.18` via stack/Weaver pins |
| GHSA-4xgf-cpjx-pc3j pydantic-settings | Floor `>=2.14.2` |
| GHSA-f4j7-r4q5-qw2c chromadb | Local-only vector DB; no public bind |
| Prompt injection | Core `SecurityGuard` on all LLM prompts |
| GITHUB_TOKEN | CI workflows use `permissions: contents: read` |

## Quality gates

- Portal CI + SecOps (Bandit/Gitleaks) + red-team schedules.
- Actuator / irrigation / crop actions must remain fail-closed on guard failure.

## Fleet security principles

- **No silent exfiltration** of personal or tenant operational data
- Prefer **local-first** processing; third-party AI only with explicit operator configuration and UI/docs disclosure
- Report vulnerabilities via GitHub Security Advisories or the maintainer contact on the org profile
- High-stakes production changes require human approval (HITL)

