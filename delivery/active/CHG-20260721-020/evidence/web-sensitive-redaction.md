# Web sensitive-value redaction

- Account-opening Cookie preview no longer renders raw Cookie text or a truncated value; it shows only a row identifier.
- Web production build and all 8 API-client tests pass after the change.
- Cookie input remains transient in the current page and is not yet wired to the final sensitive-permit write path.
