# Precise retry controls

- Cloud supports `POST /api/v1/cloud-agent/tasks/:task_id/retry`.
- Only failed or cancelled tasks can create a new pending attempt; running and succeeded tasks are rejected.
- The retry preserves the structured business payload but uses a new task ID and idempotency key.
- Web Tasks page exposes retry for failed/cancelled rows.
- Web tests (8) and Cloud task/app tests pass.
