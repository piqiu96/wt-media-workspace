# Task payload redaction

- Cloud task detail responses now redact `password`, proxy password, Cookie, token, and SMS-token payload keys.
- Agent claim responses retain the execution payload because they are the controlled runtime channel.
- Cloud task/app tests pass after the redaction change.
