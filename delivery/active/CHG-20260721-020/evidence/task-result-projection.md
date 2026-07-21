# Verified task result projection

- Successful `account_check_task` results update the authorized `media_accounts.login_status` and check timestamps.
- Successful `proxy_check_task` results update `proxy_configs.last_check_result` and check timestamps.
- Failed tasks or successful reports without a structured result do not project formal business state.
- Cloud full Go suite passes after the projection change.

Profile mutation projection still requires a domain-specific Cloud update after verified BitBrowser read-back; that remains active M2-B work.
