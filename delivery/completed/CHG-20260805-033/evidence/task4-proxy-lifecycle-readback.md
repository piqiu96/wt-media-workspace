# Task 4 Proxy lifecycle read-back

- Command: `python3 -m unittest discover -s tests -v` in `wt-media-agent`.
  Expected: assignment, mismatch rejection and `noproxy` unbind tests pass without returning credentials.
  Actual: 77 tests passed, including `test_unbind_writes_no_proxy_and_requires_no_proxy_readback`.
- Command: `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1` in `wt-media-cloud`.
  Expected: new proxy is read back before a replacement relation is switched; formal relation is only cleared after unbind read-back.
  Actual: both packages passed. Route tests cover replacement and unbind behaviour.
- External-effect limitation: these commands use controlled doubles. Real BitBrowser proxy replacement and unbind remain an M2-C end-to-end acceptance item and need a writable real proxy.
