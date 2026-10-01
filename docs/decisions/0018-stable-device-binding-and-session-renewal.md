# ADR-0018: Stable Desktop device binding with session-scoped Agent authorization

- Status: Accepted
- Date: 2026-09-30
- Scope: Desktop local execution, Cloud identity and runtime binding
- Refines: ADR-0003 (session-bound ticket and node credential remain in force)

## Context

The current Desktop sends the literal `desktop-local-device` as `device_id`, while Cloud creates a new node for each registration. The node credential is held only in Desktop and Agent process memory. Login replacement invalidates the old session, and Desktop startup does not register a node for the new session. The result is a repeated manual “bind Agent” prompt on the same computer. A transient node or session is therefore not a durable device identity.

The product now requires one explicitly bound operating computer per user, automatic renewal on the same computer after login or Agent restart, and manual unbind before another computer can be bound. BitBrowser `main_user_id` is a separate persistent user binding. Temporary dependency failures must not revoke either binding.

## Decision

1. Desktop creates one installation identity with a locally protected Ed25519 private key. Its public key fingerprint is the stable `device_id`. The private key never enters WebView, Agent, Cloud, logs or diagnostics. The identity survives normal application and OS restarts. Loss of the local identity is treated as a different installation and requires manual unbind and bind; hardware fingerprints are not used.
2. Cloud owns an auditable, at-most-one-active-device binding per user. First binding and rebinding require an explicit action in the Desktop personal-info page. Cloud verifies a signature over the current one-use binding ticket and a server-defined challenge context before accepting a node registration. A matching existing device may renew its session-scoped node authorization automatically; a different device is rejected while the old binding is active.
3. The existing one-use ticket, hashed node credential, active-session validation and single-session replacement remain. A new login invalidates the old node but does not revoke the device binding. On Desktop login, Agent restart and recovery, Desktop obtains a fresh ticket, proves the same device identity, registers a new node and reports current runtime health without asking the user to bind again. Any replaced node loses new-task rights.
4. User-initiated device unbind is a Cloud transaction: revoke the active device binding, invalidate its nodes and audit the action. It does not delete local files, local indexes, Cloud content/history or the user's confirmed BitBrowser `main_user_id`. A new device must be manually bound afterward. The old device cannot obtain another node while the new device is bound, even if it still has local files.
5. Cloud checks active device binding for node registration, runtime reports and local-task claim/assignment. The status shown in Desktop distinguishes device mismatch, missing session authorization, Agent health and BitBrowser identity/dependency health. A dependency error blocks the relevant execution but never silently unbinds the device.
6. The personal-info and unbind endpoints are reachable with a valid Cloud login even on an unbound or mismatched computer. This is necessary to recover when the old computer is unavailable. Cloud Web can display saved device facts and initiate unbind but cannot claim local runtime presence or bind a device.
7. Existing installations cannot be identified from the legacy constant `device_id`. After rollout, the first local use needs one explicit device enrollment. The saved BitBrowser main account remains, and normal subsequent restarts require no enrollment.

## Consequences

- Cloud owns device binding and task authorization; Desktop owns the installation key and automatic session renewal; Agent continues to hold only current node credentials and report local facts.
- The Cloud Agent registration contract must carry device public key and proof, and the Cloud user API must expose binding status, explicit bind/unbind and personal-info data. Providers change before Desktop and Agent consumers.
- Tests must prove same-device restart/re-login, different-device rejection, unbind/rebind, old-node rejection, BitBrowser mismatch, dependency outage and no deletion or migration of old local files.
