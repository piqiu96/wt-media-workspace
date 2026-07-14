# ADR-0004: Sensitive Profile task locking and uncertain expiry

- Status: Accepted
- Date: 2026-07-14
- Change: CHG-20260714-019

Sensitive browser actions can create external effects that Cloud cannot infer from a lost heartbeat. Therefore a sensitive task needs both a Cloud Profile permit and a local Agent Profile mutex. The permit is granted only for an existing Cloud-authorized task assigned to the bound node/user/Profile and only while the C4 runtime presence is fresh and ownership matches.

An active conflicting permit means waiting. An expired permit that was not explicitly released means the external result is uncertain, so the lock enters `review_required` and is not automatically reassigned. Permit secrets are returned once and stored only as hashes. These rules apply before future publication/interaction/account executors and do not themselves implement those operations.
