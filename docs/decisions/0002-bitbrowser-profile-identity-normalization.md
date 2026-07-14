# ADR-0002: BitBrowser Profile Identity Normalization

- Status: Accepted
- Date: 2026-07-14
- Scope: M2 BitBrowser user and Browser Profile identity

## Context

The product baseline calls the BitBrowser-side identity `owner_user_id`, but the official Local API profile example exposes `userId`, `mainUserId`, and `operUserId` rather than a field literally named `ownerUserId`.

Official references:

- https://doc.bitbrowser.cn/api-jie-kou-wen-dang/liu-lan-qi-jie-kou
- https://doc.bitbrowser.net/api-docs/browser-profiles

The official API documents `POST /browser/list`, zero-based paging, and a maximum page size of 100. Its profile example uses `userId` for the profile user, `operUserId` for the operator metadata, and `mainUserId` for the main account.

Real C6 verification against the deployed BitBrowser Local API returned 37 Profiles under one `mainUserId` and two distinct `userId` values. This matches BitBrowser's main/sub-account permission tree: a main account can see Profiles created by itself and sub-accounts, while a sub-account can only see its own scope.

## Decision

- Agent normalizes BitBrowser `mainUserId` to the product field `main_user_id`.
- Agent normalizes BitBrowser `userId` to the product field `profile_user_id` for Profile/sub-account audit.
- `operUserId` is never treated as Profile ownership.
- `main_user_id` is the only BitBrowser-side root identity used for scan consistency and runtime environment verification.
- `profile_user_id` records which BitBrowser Profile/sub-account identity owns or created the Profile, but Cloud business authorization still uses Cloud user/Profile assignment.
- Agent scans `/browser/list` with zero-based pages and `pageSize=100` until the final short page.
- A scan is unverifiable if any Profile lacks `mainUserId`, if returned Profiles contain more than one `mainUserId`, if any Profile lacks `userId`, or if there are no Profiles and no separate authoritative account-identity endpoint is available.
- Multiple `profile_user_id` values are allowed when they share the same `main_user_id`.

## Consequences

Cloud receives separate normalized fields for the BitBrowser root account and Profile/sub-account identity. Product language is updated from the earlier `owner_user_id` placeholder to `main_user_id` plus `profile_user_id`; the Agent adapter owns external API naming. C6 validates the mapping against the deployed BitBrowser version and a controlled test account.
