# Profile ID boundary and formal projection

- Cloud mutation payloads now carry both the Cloud Profile ID and the BitBrowser `bit_profile_id`.
- Agent sends only the BitBrowser ID to BitBrowser and returns the Cloud ID in its verified result.
- Verified open/close/update results project `bit_status` back to the Cloud `browser_profiles` record.
- Cloud Profile, task, and Agent tests pass; Agent suite remains 46/46.
