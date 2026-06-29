# BASH sites — project charter

## Goal

Serve the public BASH/HiveSec web presence and display validated HiveSec
Sentinel alerts without exposing private scanner or Butler data.

## Responsibilities

- Render the BASH and HiveSec brand variants on their configured domains.
- Accept versioned HiveSec public alerts through GitHub `repository_dispatch`.
- Validate and store a bounded public alert feed.
- Deploy the static site through the existing GitHub Actions/Cloudflare path.

## Boundaries

- The site receives only the `PublicAlert` contract from HiveSec Sentinel.
- It has no access to scanner outboxes, Butler, Aspasia or their credentials.
- Alert fields are rendered as text, never executable HTML.
- Invalid IDs, source names, types, lengths, severities or timestamps are rejected.

## Implemented changes — 2026-06-29

- Added the HiveSec Sentinel public alert panel and Telegram link.
- Added `repository_dispatch` handling for `security-alert`.
- Added strict server-side validation and bounded feed retention.
- Added tests for accepted alerts and invalid/private source rejection.
- Preserved the existing BASH/HiveSec domain-aware presentation.

## Operations

```bash
python3 .github/scripts/test_publish_alert.py
git status --short
```

## Success criteria

- Only alerts with `source=HiveSec Sentinel` enter the public feed.
- The browser never interprets alert content as HTML.
- Existing domains and the BASH site remain deployable when no alert exists.

## Next goals

1. Validate the first live HiveSec dispatch after dedicated credentials exist.
2. Confirm deployment and rendering on every configured public domain.
3. Add publication-latency monitoring if operational volume justifies it.
