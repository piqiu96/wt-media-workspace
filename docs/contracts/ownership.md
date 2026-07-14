# Contract Ownership

Principle: the interface provider owns the formal contract.

## Owners

| Contract Area | Owner Repository |
|---|---|
| Cloud API | `wt-media-cloud` |
| Cloud-Agent API | `wt-media-cloud` |
| Business schemas | `wt-media-cloud` |
| Task schemas | `wt-media-cloud` |
| Business enums | `wt-media-cloud` |
| Cloud error codes | `wt-media-cloud` |
| Local Agent API | `wt-media-agent` |
| Local event schemas | `wt-media-agent` |
| Local status enums | `wt-media-agent` |
| Local error codes | `wt-media-agent` |

Desktop consumes Cloud and Agent contracts. It does not define formal cross-repo contracts.
