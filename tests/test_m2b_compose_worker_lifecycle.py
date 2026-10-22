"""The local acceptance environment must not strand compose tasks."""

import io
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.dev import local_env as harness


REPO_ROOT = Path(__file__).resolve().parents[1]


class ComposeWorkerLifecycleTests(unittest.TestCase):
    def test_path_constants_match_the_new_location(self):
        self.assertEqual(harness.SCRIPTS_DIR, REPO_ROOT / "scripts")
        self.assertEqual(harness.WORKSPACE_DIR, REPO_ROOT)
        self.assertEqual(harness.WORKSPACE_DIR.name, "wt-media-workspace")
        self.assertEqual(harness.CLOUD_DIR, REPO_ROOT.parent / "wt-media-cloud")

    def test_up_and_all_build_and_start_the_compose_claim_loop(self):
        for command in ("up", "all"):
            with self.subTest(command=command), ExitStack() as stack:
                stack.enter_context(mock.patch.object(harness, "parse_args", return_value=SimpleNamespace(command=command, force_restart=False)))
                for name in (
                    "run_migrations", "start_cloud", "start_worker", "start_agent",
                    "start_web_dev", "start_desktop_dev", "verify_bitbrowser",
                    "build_dmg", "rebuild_cloud_dist", "verify_all", "verify_login", "launch_dmg",
                ):
                    stack.enter_context(mock.patch.object(harness, name))
                build = stack.enter_context(mock.patch.object(harness, "run"))
                launch = stack.enter_context(mock.patch.object(harness, "start_background"))

                self.assertEqual(harness.main(), 0)
                self.assertTrue(any(
                    "./cmd/compose-worker" in call.args[0]
                    for call in build.call_args_list
                ), f"{command} must build the compose worker")
                self.assertTrue(any(
                    call.args[0] == "compose-worker" and call.args[2] == harness.CLOUD_DIR
                    for call in launch.call_args_list
                ), f"{command} must start the compose worker as a managed process")

    def test_status_refuses_a_missing_compose_worker(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            pid_dir = Path(temp)
            for name in ("cloud", "agent", "worker", "web-dev", "desktop-dev"):
                (pid_dir / f"{name}.pid").write_text("123\n")
            stack.enter_context(mock.patch.object(harness, "PID_DIR", pid_dir))
            stack.enter_context(mock.patch.object(harness, "pid_alive", side_effect=lambda path: path.name != "compose-worker.pid"))
            stack.enter_context(mock.patch.object(harness, "http_json", return_value={}))
            stack.enter_context(mock.patch.object(harness, "dev_server_answers", return_value=True))
            output = io.StringIO()
            with redirect_stdout(output):
                code = harness.cmd_status()

        self.assertEqual(code, 1)
        self.assertIn("compose-worker: pid=- alive=no", output.getvalue())

    def test_verify_refuses_a_missing_compose_worker(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
            for name in (
                "wait_http", "verify_agent", "verify_worker", "verify_bitbrowser",
                "verify_assets", "verify_dev_servers", "verify_dmg",
            ):
                stack.enter_context(mock.patch.object(harness, name))
            with redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "[Cc]ompose worker"):
                    harness.verify_all()


if __name__ == "__main__":
    unittest.main()
