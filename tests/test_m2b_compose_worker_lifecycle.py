"""The local acceptance environment must not strand compose tasks."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.dev import local_env as harness


REPO_ROOT = Path(__file__).resolve().parents[1]


class ComposeWorkerLifecycleTests(unittest.TestCase):
    def test_restart_stops_same_cloud_compose_worker_left_by_other_runtime_dir(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            cloud = Path(temp) / "wt-media-cloud"
            lock = cloud / ".compose" / "compose-worker.lock"
            binary = cloud / ".cache" / "wt-media-compose-worker"
            lock.parent.mkdir(parents=True)
            binary.parent.mkdir(parents=True)
            lock.touch()
            binary.touch()
            stack.enter_context(mock.patch.object(harness, "CLOUD_DIR", cloud))
            stack.enter_context(mock.patch.object(harness, "COMPOSE_WORKER_BIN", binary))
            run = stack.enter_context(mock.patch.object(harness.subprocess, "run", side_effect=[
                SimpleNamespace(stdout="4512\n"),
                SimpleNamespace(stdout=f"{os.getuid()} {binary}\n"),
            ]))
            kill = stack.enter_context(mock.patch.object(harness.os, "kill"))
            stack.enter_context(mock.patch.object(harness, "process_alive", return_value=False))

            harness.stop_orphan_compose_worker()

            self.assertEqual(run.call_count, 2)
            kill.assert_called_once_with(4512, harness.signal.SIGTERM)

    def test_restart_refuses_to_stop_unrelated_lock_holder(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            cloud = Path(temp) / "wt-media-cloud"
            lock = cloud / ".compose" / "compose-worker.lock"
            lock.parent.mkdir(parents=True)
            lock.touch()
            stack.enter_context(mock.patch.object(harness, "CLOUD_DIR", cloud))
            stack.enter_context(mock.patch.object(harness.subprocess, "run", side_effect=[
                SimpleNamespace(stdout="4512\n"),
                SimpleNamespace(stdout=f"{os.getuid()} /tmp/some-other-worker\n"),
            ]))
            kill = stack.enter_context(mock.patch.object(harness.os, "kill"))

            with self.assertRaisesRegex(RuntimeError, "unrecognized process"):
                harness.stop_orphan_compose_worker()

            kill.assert_not_called()

    def test_agent_source_override_keeps_chg_worktree_in_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, "-c", "from scripts.dev.local_env import AGENT_DIR; print(AGENT_DIR)"],
                cwd=REPO_ROOT,
                env={**os.environ, "WT_MEDIA_AGENT_SOURCE_DIR": temp},
                capture_output=True,
                text=True,
                check=True,
            )
        self.assertEqual(result.stdout.strip(), temp)

    def test_force_restart_checks_for_orphan_after_stopping_pid_workers(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "close_desktop_app"))
            stack.enter_context(mock.patch.object(harness, "stop_listener"))
            stack.enter_context(mock.patch.object(harness, "wait_port_free"))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
            cleanup = stack.enter_context(mock.patch.object(harness, "stop_orphan_compose_worker"))

            harness.stop_started()

            cleanup.assert_called_once_with()

    def test_path_constants_match_the_new_location(self):
        self.assertEqual(harness.SCRIPTS_DIR, REPO_ROOT / "scripts")
        self.assertEqual(harness.WORKSPACE_DIR, REPO_ROOT)
        self.assertEqual(harness.WORKSPACE_DIR.name, "wt-media-workspace")
        self.assertEqual(harness.CLOUD_DIR, REPO_ROOT.parent / "wt-media-cloud")

    def test_up_and_all_build_and_start_the_compose_claim_loop(self):
        for command in ("up", "all"):
            with self.subTest(command=command), ExitStack() as stack:
                stack.enter_context(mock.patch.object(harness, "parse_args", return_value=SimpleNamespace(command=command, force_restart=False)))
                stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
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

    def test_managed_agent_runs_formal_bootstrap_and_transfer_runner_without_token_argv(self):
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
            stack.enter_context(mock.patch.object(harness, "close_desktop_app"))
            stack.enter_context(mock.patch.object(harness, "wait_http"))
            stack.enter_context(mock.patch.dict(os.environ, {"WT_MEDIA_AGENT_RUNTIME_TOKEN": "test-runtime-token"}))
            launch = stack.enter_context(mock.patch.object(harness, "start_background"))
            harness.start_agent()
            name, command, cwd, env = launch.call_args.args
            self.assertEqual(name, "agent")
            self.assertEqual(command, [str(harness.AGENT_PYTHON), "-m", "wt_media_agent.local_main"])
            self.assertEqual(cwd, harness.AGENT_DIR)
            self.assertEqual(env["WT_MEDIA_AGENT_RUN_RUNNER"], "true")
            self.assertEqual(env["WT_MEDIA_LOCAL_API_HOST"], harness.AGENT_HOST)
            self.assertEqual(env["WT_MEDIA_LOCAL_API_PORT"], harness.AGENT_PORT)
            self.assertEqual(env["WT_MEDIA_CLOUD_BASE_URL"], harness.CLOUD_BASE_URL)
            self.assertEqual(env["WT_MEDIA_AGENT_RUNTIME_TOKEN"], "test-runtime-token")
            self.assertNotIn("test-runtime-token", " ".join(command))
            self.assertNotIn("--auth-token", command)

    def test_default_up_and_all_manage_compose_scheduler_but_not_discovery_scheduler(self):
        for command in ("up", "all"):
            with self.subTest(command=command), ExitStack() as stack:
                stack.enter_context(mock.patch.object(harness, "parse_args", return_value=SimpleNamespace(command=command, force_restart=False)))
                stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
                for name in ("run_migrations", "start_cloud", "start_worker", "start_compose_worker", "start_agent", "start_web_dev", "start_desktop_dev", "verify_bitbrowser", "build_dmg", "rebuild_cloud_dist", "verify_all", "verify_login", "launch_dmg"):
                    stack.enter_context(mock.patch.object(harness, name))
                build = stack.enter_context(mock.patch.object(harness, "run"))
                launch = stack.enter_context(mock.patch.object(harness, "start_background"))
                self.assertEqual(harness.main(), 0)
                self.assertTrue(any("./cmd/compose-scheduler" in call.args[0] for call in build.call_args_list))
                self.assertFalse(any("./cmd/discovery-scheduler" in call.args[0] for call in build.call_args_list))
                self.assertTrue(any(call.args[0] == "compose-scheduler" and call.args[2] == harness.CLOUD_DIR for call in launch.call_args_list))

    def test_scheduler_rebuild_replaces_stale_process_before_launch(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            binary = Path(temp) / "scheduler"
            binary.write_text("compiled")
            pid_file = Path(temp) / "compose-scheduler.pid"
            pid_file.write_text("4321\n")
            os.utime(pid_file, (100, 100))
            os.utime(binary, (200, 200))
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "COMPOSE_SCHEDULER_BIN", binary))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=True))
            stack.enter_context(mock.patch.object(harness, "run"))
            stack.enter_context(mock.patch.object(harness, "process_alive", side_effect=[True, False, False]))
            stack.enter_context(mock.patch.object(harness.time, "sleep"))
            events = []
            kill = stack.enter_context(mock.patch.object(harness.os, "kill", side_effect=lambda *args: events.append("stop")))
            stack.enter_context(mock.patch.object(harness, "start_background", side_effect=lambda *args: events.append("start")))
            harness.start_compose_scheduler()
            self.assertEqual(events, ["stop", "start"])
            kill.assert_called_once_with(4321, harness.signal.SIGTERM)
            self.assertFalse(pid_file.exists())

    def test_scheduler_rebuild_refuses_duplicate_when_old_process_will_not_stop(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            binary = Path(temp) / "scheduler"
            binary.write_text("compiled")
            pid_file = Path(temp) / "compose-scheduler.pid"
            pid_file.write_text("4321\n")
            os.utime(pid_file, (100, 100))
            os.utime(binary, (200, 200))
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "COMPOSE_SCHEDULER_BIN", binary))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=True))
            stack.enter_context(mock.patch.object(harness, "run"))
            stack.enter_context(mock.patch.object(harness.os, "kill"))
            stack.enter_context(mock.patch.object(harness, "process_alive", return_value=True))
            stack.enter_context(mock.patch.object(harness.time, "time", side_effect=[0, 11]))
            launch = stack.enter_context(mock.patch.object(harness, "start_background"))
            with self.assertRaisesRegex(RuntimeError, "scheduler.*still running"):
                harness.start_compose_scheduler()
            launch.assert_not_called()
            self.assertEqual(pid_file.read_text().strip(), "4321")

    def test_status_refuses_a_missing_compose_scheduler(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            pid_dir = Path(temp)
            for name in ("cloud", "agent", "worker", "compose-worker", "web-dev", "desktop-dev"):
                (pid_dir / f"{name}.pid").write_text("123\n")
            stack.enter_context(mock.patch.object(harness, "PID_DIR", pid_dir))
            stack.enter_context(mock.patch.object(harness, "pid_alive", side_effect=lambda path: path.name != "compose-scheduler.pid"))
            stack.enter_context(mock.patch.object(harness, "http_json", return_value={}))
            stack.enter_context(mock.patch.object(harness, "dev_server_answers", return_value=True))
            output = io.StringIO()
            with redirect_stdout(output):
                code = harness.cmd_status()
        self.assertEqual(code, 1)
        self.assertIn("compose-scheduler: pid=- alive=no", output.getvalue())

    def test_verify_refuses_a_missing_compose_scheduler(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=False))
            for name in ("wait_http", "verify_agent", "verify_worker", "verify_compose_worker", "verify_bitbrowser", "verify_assets", "verify_dev_servers", "verify_dmg"):
                stack.enter_context(mock.patch.object(harness, name))
            with redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "[Cc]ompose scheduler"):
                    harness.verify_all()

    def test_stop_terminates_managed_scheduler_and_removes_pid(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            pid_dir = Path(temp)
            pid_file = pid_dir / "compose-scheduler.pid"
            pid_file.write_text("4321\n")
            stack.enter_context(mock.patch.object(harness, "PID_DIR", pid_dir))
            stack.enter_context(mock.patch.object(harness, "pid_alive", side_effect=lambda path: path == pid_file))
            for name in ("close_desktop_app", "stop_listener", "wait_port_free", "stop_orphan_compose_worker"):
                stack.enter_context(mock.patch.object(harness, name))
            alive = stack.enter_context(mock.patch.object(harness, "process_alive", return_value=False))
            kill = stack.enter_context(mock.patch.object(harness.os, "kill"))
            harness.stop_started()
            kill.assert_called_once_with(4321, harness.signal.SIGTERM)
            alive.assert_any_call(4321)
            self.assertFalse(pid_file.exists())

    def test_stop_refuses_to_forget_a_scheduler_that_did_not_exit(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            pid_dir = Path(temp)
            pid_file = pid_dir / "compose-scheduler.pid"
            pid_file.write_text("4321\n")
            stack.enter_context(mock.patch.object(harness, "PID_DIR", pid_dir))
            stack.enter_context(mock.patch.object(harness, "pid_alive", side_effect=lambda path: path == pid_file))
            for name in ("close_desktop_app", "stop_listener", "wait_port_free", "stop_orphan_compose_worker"):
                stack.enter_context(mock.patch.object(harness, name))
            stack.enter_context(mock.patch.object(harness.os, "kill"))
            stack.enter_context(mock.patch.object(harness, "process_alive", return_value=True))
            stack.enter_context(mock.patch.object(harness.time, "time", side_effect=[0, 11]))
            with self.assertRaisesRegex(RuntimeError, "scheduler.*still running"):
                harness.stop_started()
            self.assertEqual(pid_file.read_text().strip(), "4321")

    def test_verify_rejects_scheduler_started_before_latest_binary(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            binary = Path(temp) / "scheduler"
            binary.write_text("compiled")
            pid_file = Path(temp) / "compose-scheduler.pid"
            pid_file.write_text("123\n")
            os.utime(pid_file, (100, 100))
            os.utime(binary, (200, 200))
            stack.enter_context(mock.patch.object(harness, "PID_DIR", Path(temp)))
            stack.enter_context(mock.patch.object(harness, "COMPOSE_SCHEDULER_BIN", binary))
            stack.enter_context(mock.patch.object(harness, "pid_alive", return_value=True))
            check = stack.enter_context(mock.patch.object(harness, "check_fresh"))
            with self.assertRaisesRegex(RuntimeError, "[Ss]tale|restart"):
                harness.verify_compose_scheduler()
            self.assertEqual(check.call_args.args[0], binary)
            os.utime(pid_file, (300, 300))
            harness.verify_compose_scheduler()

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
