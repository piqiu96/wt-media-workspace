# CHG-20260924-061 Task 3 second segment — real object storage

- Date: 2026-09-27
- Repo: `wt-media-cloud`, branch `codex/m4-a-cloud`
- Commits: `34f965a` (config), `3dddbc0` (defect fix, see §5)
- Scope: real OSS acceptance for the preparation path plus one real end-to-end
  preparation. No credentials, cookies, signed URLs, local usernames or absolute
  paths appear in this record.

## 1. Configuration that was landed

`config/storage/object_storage.toml` and `config_online/storage/object_storage.toml`
now carry `bucket = 'data'`, `endpoint = 's3.oss.longyanyue.cn'`, `region = 'garage'`,
`prefix = 'dev/'` (`''` in `config_online`). The credential file stays in the
git-ignored `config/credentials/` path and is not committed.

The endpoint is not the one first supplied. Measured:

| Candidate | Reading |
|---|---|
| `data.bucket.oss.longyanyue.cn` | Garage `s3_web` read-only website: GET of an absent key answers `NoSuchKey`, PUT answers `InvalidRequest: HTTP method not supported` |
| `data.oss.longyanyue.cn` | NXDOMAIN — does not resolve |
| `s3.oss.longyanyue.cn` | resolves, is the Garage S3 API, and answers the whole probe below |

`region = 'garage'` was taken from Garage's own XML error body
(`<Region>garage</Region>`), not from the admin UI's per-bucket placement field,
which reads `default` and is not the S3 region string.

## 2. The three questions only a real endpoint answers

Throwaway probe, run from the worktree, deleted before the CHG closes (never
committed). Readings:

| Question | Expected | Actual | Status |
|---|---|---|---|
| Addressing style | path style, because the bucket name `data` equals the endpoint's first label and virtual-host style would build `data.data.bucket…` | presigned path is `/data/dev/materials/…` — path style | PASS |
| Does a presigned GET fetch the bytes we put | 200 and a matching digest | `PUT ok in 398ms`; `STAT size=1048576`; `PRESIGN GET status=200 bytes=1048576 sha256 match=true`; `REMOVE ok, Stat afterwards fails as expected` | PASS |
| Does a non-empty region keep `PresignGet` off the network (the claim in `internal/infra/storage/minio.go`) | 0 requests with a region, 1 without | `region="garage"` → `http_requests=0`; `region=""` → `http_requests=1` | PASS |

The probe prints only host and path of the signed URL, never the query string.

Bucket-level cross-check against the provider's own accounting, at the
7-object state: probe listing read 7 objects / 163,119,670 bytes = 155.56 MiB,
and the Garage admin UI for the same bucket read 7 objects / 155.56 MB.

## 3. AC-01 negative control, before the click

Material 153 after conversion, before any click:

- objects under the material's prefix: **0**
- `file_transfer_tasks` rows: **0**
- `material_usages` rows: **0**
- material 153: `video_status = not_downloaded`, object key / size / sha256 all NULL

So nothing is prepared or transferred until the click, which is what AC-01
asserts.

## 4. One real click, end to end

`POST /api/v1/materials/153/downloads` → 202, one `compose_input_prepare` task
(`execution_scope='cloud'`) and one dependent `user_download` task
(`execution_scope='local_agent'`). The worker ran against the real provider.

| Task | Scope | Status | Bytes |
|---|---|---|---|
| `compose_input_prepare` | cloud | success | 99,242,095 / 99,242,095 |
| `user_download` | local_agent | success | 99,242,095 / 99,242,095 |

Material 153 after: `video_status = ready`, `video_size_bytes = 99242095`,
`video_sha256 = e8acfe3e610fd44becbebf50e898a92ff483728bf1d35447cc61f200c6b71c6d`.

### Three-way reconciliation

| Surface | size | sha256 |
|---|---|---|
| object `dev/materials/153/e8acfe3e…c6d.mp4` | 99,242,095 | embedded in the key |
| file on the operator machine | 99,242,095 | `e8acfe3e610fd44b…c6d` |
| `file_transfer_tasks` row | `total_bytes` = `transferred_bytes` = 99,242,095 | `expected_sha256` = `integrity_sha256` = `e8acfe3e…c6d`, `integrity_bytes` = 99,242,095 |
| `materials` row | 99,242,095 | `e8acfe3e…c6d` |

Column names differ from the plan's text: the transfer table has
`transferred_bytes` / `integrity_sha256` / `integrity_bytes`, not
`completed_bytes` / `checksum_sha256`. Recorded as measured.

### Provider-side read-back of the prepared object

`ossprobe stat 153`:

```
STAT key=materials/153/e8acfe3e610fd44becbebf50e898a92ff483728bf1d35447cc61f200c6b71c6d.mp4 size=99242095 etag=2a472d0faf929089196035071f49fc94-6 content_type=video/mp4
OBJECT COUNT=1
```

Object size equals `video_size_bytes`; `content_type=video/mp4` shows the mime
reached the provider; exactly one object exists under the material's prefix.

Bucket totals moved from 7 objects / 163,119,670 bytes to 8 objects /
262,361,765 bytes — a delta of 99,242,095 bytes, exactly the prepared material.

## 5. Correction: the plan's ETag assertion was wrong

The plan's acceptance text said the object's `ETag` should agree with
`materials.video_sha256`. It cannot, and the implementation is right to refuse
the comparison. The measured ETag `2a472d0f…-6` carries a `-6` suffix, i.e. this
was a six-part upload and the ETag is the store's multipart digest, not the
sha256 of the bytes.

`internal/jobs/material_prepare.go:440-443` already documents exactly this:
`Stat` answers a size and an ETag, "and the ETag is the store's own digest under
a different algorithm — comparing it with this sha256 would be comparing two
different sums and calling the match meaningful."

So the sha256 linkage is carried by the object **key** (which embeds the digest)
and by the byte-level read-back, not by ETag. The corrected reading is PASS on
size and content type, and ETag explicitly declared not comparable. The code was
not changed: the plan's phrasing was the wrong side of the disagreement.

## 6. Defect found and fixed in this segment

`PreparationSource` returned `ContentID: material.SourceContentID` — this
database's `source_contents.id` — and the worker sends that value to the provider
as the video id. The provider answers "video does not exist", which is the same
answer a genuinely removed video gets, so the fault was silent until a real run.

Observed as: every real preparation failed with
`source_detail_failed / douyin API rejected request`, while eight identical
by-hand calls succeeded. A recording server on the provider's address captured
the true request body: `id=873`, the local row id, where the provider knows
`platform_content_id`.

Fixed in `3dddbc0`: `platform_content_id` is projected onto the material
(`json:"-"`, worker plumbing rather than a UI field) and `PreparationSource`
resolves from it, refusing anything that is not a positive integer instead of
falling back to the row id. After the fix the worker sends
`id=7463510597309664566` and material 153 reaches `ready`.

## 7. Boundary check while the run was live

Positive control first, so a zero is a reading and not a broken matcher:
the same pattern matched against its own text returns 1.

| Surface | Pattern | Hits | Denominator |
|---|---|---|---|
| `materials` (key, error, title, snapshot) | scratch dir name | 0 | 149 rows |
| `file_transfer_tasks` (title, key, name, error, dedupe) | scratch dir name | 0 | 12 rows |
| both tables | `/Users/` and `/tmp/` shapes | 0 | same |
| `logs/access.log`, `logs/external.log`, `logs/job.log`, `logs/panic.log` | `/Users/`, `/tmp/`, scratch name | 0 | 606 / 6 / 6 / 2 lines |

One disclosure: `.cache/wt-media-cloud.log` (git-ignored) carries five lines with
an absolute path, because GORM's default logger prints the caller's Go source
file on error. Those are repo paths, not the operator's download directory, and
the file is not a Cloud business log. Recorded rather than omitted, since a
zero elsewhere is only meaningful next to this.

Those five lines are also the first sighting of two pre-existing defects outside
this CHG's scope, registered separately rather than patched here.

## Result

PASS — a real source video was re-resolved from the provider, streamed through
the worker, landed in real object storage, and downloaded to the operator
machine; object, disk and both database rows agree byte for byte, and the
provider's own read-back agrees on size. One CHG-blocking defect was found by
running it, fixed and committed. One plan assertion (ETag vs sha256) was found
to be wrong and is corrected here instead of being forced onto the code.
