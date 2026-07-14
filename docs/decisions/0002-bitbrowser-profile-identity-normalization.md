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

## Decision

- Agent normalizes BitBrowser `userId` to the product field `owner_user_id`.
- `operUserId` is never treated as Profile ownership.
- `mainUserId` and `operUserId` may be retained only as non-authoritative diagnostic metadata and must not drive authorization.
- Agent scans `/browser/list` with zero-based pages and `pageSize=100` until the final short page.
- A scan is unverifiable if any Profile lacks `userId`, if returned Profiles contain more than one `userId`, or if there are no Profiles and no separate authoritative account-identity endpoint is available.
- If actual deployed BitBrowser behavior contradicts this mapping, execution stops and this ADR is revised before formal data changes.

## Consequences

Cloud receives one normalized identity field and never guesses among multiple raw identifiers. Product language remains stable while the Agent adapter owns external API naming. C6 must validate the inference against the deployed BitBrowser version and a controlled test account.
