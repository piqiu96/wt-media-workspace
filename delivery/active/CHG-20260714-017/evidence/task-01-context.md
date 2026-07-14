# Evidence: C3 Context and External API Decision

- CHG: `CHG-20260714-017`
- Task: `T-01`
- Date: 2026-07-14
- Type: spike
- Status: PASS

## Purpose

Establish a verifiable external API mapping and resolve contract-provider conflict before implementation.

## Method

Reviewed product/engineering baselines, Cloud/Agent code, current provider trees, and official BitBrowser Local API documentation.

## Expected

C3 has a provider-owned integration boundary, an explicit identity mapping, and no hidden reliance on absent contracts.

## Actual

Official docs confirm `POST /browser/list`, page 0, max page size 100, and example fields `userId`, `operUserId`, and `mainUserId`. ADR-0002 maps only `userId` to product ownership. The Agent provider-definition gap is explicitly part of C3 and must be repaired before Workspace revisions advance.

## Follow-Up

- Generated context reports CHG-017 IMPLEMENTING with Workspace, Cloud, and Agent scope. Begin adapter TDD.
