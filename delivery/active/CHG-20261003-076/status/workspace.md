# Workspace status

- Product RC3 Tag `v0.1.0-rc.3` → `d961aa9e6132a46ae4dd8a50c97ed07b62f0426b` correctly stopped before package/publish when Windows Desktop failed.
- RC5 run `37089104559` passed all jobs, but GitHub renamed non-ASCII asset names and broke post-download checksum lookup; the invalid Release was deleted while the Tag/run remained.
- RC6 Manifest prepared for Cloud `v0.1.0-rc.3`, Agent `v0.2.2-rc.2`, Desktop `v0.1.0-rc.3`, staging origin `https://wt.longyanyue.cn`, and the three Desktop platforms.
- Verification: RC6 manifest validation and 7 release unit tests passed, including ASCII normalization of Desktop public assets and post-publish checksum planning; governance check passed.
- RC6 run `37091241538`: all source/build jobs passed and seven controlled artifacts exist; `package` was not started because GitHub account payments/spending limit blocked the job.
- Remaining: account owner fixes GitHub billing/spending limit, reruns failed jobs for run `37091241538`, then verify the actual Pre-release download/checksums and finish the trial report.
