# Authorized proxy assignment

- Cloud validates the requesting user owns an active Profile and the proxy is active before creating `proxy_mutation_task`.
- Task payload carries both Cloud and BitBrowser Profile IDs; ordinary task detail views redact proxy credentials.
- Agent writes proxy settings to BitBrowser and requires host/port read-back before reporting success.
- Verified results project proxy host/port onto the Cloud Profile record.
- Cloud focused tests and Agent 46-test suite pass.
