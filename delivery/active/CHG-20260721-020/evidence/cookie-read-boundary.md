# Cookie read task boundary

- Authenticated media-account Cookie read endpoint creates a `cookie_read_task` with account/Profile identifiers only.
- Cookie values are not placed in the Cloud task payload.
- Agent Cookie read executor consumes nested task payloads and reports lifecycle without returning Cookie values in the normal result message.
- Cookie write remains gated behind the sensitive permit path and is intentionally not implemented by copying plaintext into persistent task JSON.
