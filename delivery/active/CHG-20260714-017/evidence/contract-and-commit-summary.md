# Contract and commit summary

## Contract advance

- Workspace contract state: `m2_bitbrowser_profile_binding`.
- Cloud API/business schema/business enum/error revisions: `2026.07.14.3`.
- Agent Local API/event/status/error revisions: `2026.07.14.6`.
- Release matrix entry: `0.2.2-m2-bitbrowser-profile-binding`.
- The governance data was changed before the verifier and the old verifier rejected the new state/revisions as expected; the updated verifier then passed.

## Independent repository commits

- Agent: `14e51be feat: add secret-safe bitbrowser profile scanner`.
- Agent: `f0257b5 feat: expose local bitbrowser profile scans`.
- Cloud: `bba30ef feat: add staged browser profile binding`.
- Cloud: `727ad9e feat: expose browser profile confirmation flow`.
- Workspace start: `0bb7ba8 docs: start chg-017 bitbrowser profile binding`.

## Boundary

C3 proves external BitBrowser identity consistency and explicit Cloud confirmation, but does not attest which registered Agent node owns the runtime. C4 adds node/Profile ownership and runtime reporting; C5 adds lock/preflight enforcement. Consequently C3 data alone does not authorize a sensitive task.
