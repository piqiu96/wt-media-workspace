#!/usr/bin/env python3
"""Failure verification for AC-11's permanent test.

The test asserts that a new task type needs no change under `src/`. A test like
that can pass for the wrong reason -- for instance if the runner executed
*something* regardless of the registration. So each mutant here breaks one
thing the test claims to hold, and the test must go red.

Mutants touch the test file (to prove the assertions bite) and `runner.py` (to
prove the production path they describe is really the one being exercised).

Usage: python3 /tmp/ac11-mutants.py
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent")
TEST = ROOT / "tests/test_new_task_type.py"
RUNNER = ROOT / "src/wt_media_agent/runner/runner.py"

# (id, description, file, anchor, replacement, test that must go red)
MUTANTS = [
    (
        "M-01",
        "the slice never registers its factory (the runner would fail closed)",
        TEST,
        "            runner.register_executor(DEMO_TASK_TYPE, factory)",
        "            pass",
        "test_the_new_type_runs_end_to_end_and_is_checkpointed_like_the_builtins",
    ),
    (
        "M-02",
        "the executor stops using the new client",
        TEST,
        "        echoed = self.service.echo(str(task.get(\"payload\", \"\")))",
        "        echoed = \"HELLO\"",
        "test_the_new_type_runs_end_to_end_and_is_checkpointed_like_the_builtins",
    ),
    (
        "M-03",
        "the runner stops clearing the checkpoint on completion",
        RUNNER,
        "            self.store.remove_checkpoint(task_id)",
        "            pass",
        "test_the_new_type_runs_end_to_end_and_is_checkpointed_like_the_builtins",
    ),
    (
        "M-04",
        "the runner never marks the task as running in the checkpoint",
        RUNNER,
        '        cp.checkpoint_status = "running"',
        '        cp.checkpoint_status = "claimed"',
        "test_the_new_type_runs_end_to_end_and_is_checkpointed_like_the_builtins",
    ),
    (
        "M-05",
        "the factory is handed something other than the runner's own client",
        RUNNER,
        "            instance = executor(self.client, self.config.agent_id)",
        "            instance = executor(self.config, self.config.agent_id)",
        "test_the_factory_receives_the_runner_s_own_client_and_the_configured_agent_id",
    ),
    (
        "M-06",
        "an unregistered type is reported as succeeded instead of failing closed",
        RUNNER,
        '            self._report_failed(task_id, "no_executor")',
        '            self.client.report_task(task_id, self.config.agent_id, "succeeded", 100, "no_executor")',
        "test_the_new_type_cannot_run_until_it_is_registered",
    ),
]

CASE_RE = re.compile(r"^(?:FAIL|ERROR): (\S+)", re.M)

#: Applied before the real mutants, and required to come back "failed". Without
#: it, a detector that never reports failure (the first version of this file had
#: exactly that bug -- `^` without `re.M`) is indistinguishable from six mutants
#: that were all caught.
DETECTOR_SELF_CHECK = (
    "detector self-check: an unconditional failure must be seen",
    TEST,
    '        runner = self.build()\n\n        runner._poll_once()\n\n'
    '        self.assertEqual(self.service.calls, ["hello"], "the new client was actually used")',
    '        self.fail("detector self-check")\n'
    '        self.assertEqual(self.service.calls, ["hello"], "the new client was actually used")',
    "test_the_new_type_runs_end_to_end_and_is_checkpointed_like_the_builtins",
)


def run(test_name: str) -> tuple[str, str, str]:
    """Return (verdict, summary, full output) for one named test."""
    # Bytecode caches are keyed by (mtime, size) with one-second resolution, so
    # a mutation that keeps a file's length and lands in the same second as the
    # write before it is invisible to the interpreter -- the run would then test
    # the *previous* version. That happened here (M-05, whose neighbour M-04
    # swaps one 7-character string for another): the mutant came back
    # "SURVIVED" while the same edit applied by hand went red.
    for cache in ROOT.rglob("__pycache__"):
        subprocess.run(["rm", "-rf", str(cache)], check=False)
    proc = subprocess.run(
        [str(ROOT / ".venv/bin/python"), "-m", "unittest", f"tests.test_new_task_type.NewTaskTypeTests.{test_name}"],
        cwd=ROOT,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    if ran is None:
        # Distinguish "the test never ran" (an import or name problem) from a
        # real verdict: without this, a typo in a mutant's path would look like
        # a caught mutation.
        return "did_not_run", tail, out
    failed = {m.group(1) for m in CASE_RE.finditer(out)}
    if test_name in failed or tail == "FAILED":
        return "failed", tail, out
    return "passed", tail, out


def main() -> int:
    pristine = {path: path.read_text() for path in (TEST, RUNNER)}

    print("=" * 78)
    print("POSITIVE CONTROL (no mutation applied)")
    for name in sorted({m[5] for m in MUTANTS}):
        verdict, tail, out = run(name)
        print(f"  {verdict.upper():<12} {name}")
        if verdict != "passed":
            print(out[-3000:])
            print("\nHARD STOP: the positive control did not pass.")
            return 2

    print("\nDETECTOR SELF-CHECK (a deliberate failure must come back as FAILED)")
    _, path, anchor, replacement, test_name = DETECTOR_SELF_CHECK
    text = pristine[path]
    if text.count(anchor) != 1:
        print(f"HARD STOP: self-check anchor matched {text.count(anchor)} times")
        return 4
    path.write_text(text.replace(anchor, replacement))
    try:
        verdict, tail, _ = run(test_name)
    finally:
        path.write_text(pristine[path])
    print(f"  {verdict.upper():<12} {test_name}")
    if verdict != "failed":
        print("\nHARD STOP: the detector cannot report failure; every verdict below is meaningless.")
        return 4

    caught = survived = invalid = 0
    for mid, desc, path, anchor, replacement, test_name in MUTANTS:
        text = pristine[path]
        hits = text.count(anchor)
        if hits != 1:
            print(f"\nHARD STOP {mid}: anchor matched {hits} times, expected 1")
            print(f"  {anchor!r}")
            return 3
        path.write_text(text.replace(anchor, replacement))
        try:
            verdict, tail, _ = run(test_name)
        finally:
            path.write_text(pristine[path])

        if verdict == "failed":
            actual, caught = "CAUGHT", caught + 1
        elif verdict == "passed":
            actual, survived = "SURVIVED", survived + 1
        else:
            actual, invalid = f"INVALID ({verdict})", invalid + 1
        print(f"\n{mid}  {actual}")
        print(f"  {desc}")
        print(f"  <- {test_name}")

    for path in (TEST, RUNNER):
        path.write_text(pristine[path])

    print("\n" + "=" * 78)
    print(f"mutants run: {len(MUTANTS)}")
    print(f"  CAUGHT {caught}   SURVIVED {survived}   INVALID {invalid}")
    return 0 if survived == 0 and invalid == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
