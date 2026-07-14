# Evidence: Local Acceptance

- CHG: `CHG-20260714-007`
- Task: `T-02`
- Date: 2026-07-14
- Type: command
- Status: PASS

## Commands

```text
python3 -m unittest discover -s tests
python3 scripts/verify_skills.py
python3 scripts/verify_m0_config.py
scripts/verify_m0_local.sh
```

## Results

```text
Ran 6 tests in 0.020s
OK
verified 8 skill source files
M0 config verification ok
wt-media-cloud health ok
wt-media-agent health ok
wt-media-desktop health ok
WT Media M0 local verification ok
```

## Notes

- `scripts/verify_m0_local.sh` binds local Cloud and Agent health ports, so elevated execution was required in the Codex sandbox.
- The Workspace unit suite now has 6 tests after making provider-path checks compatible with single-repo CI checkouts.
