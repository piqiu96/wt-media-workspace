"""A failed old-mount detach must never launch stale Desktop bits."""
import json
import subprocess
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.dev import local_env as harness


class DesktopMountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        root = Path(self.temp.name)
        self.mount = root / 'mount'
        self.desktop = root / 'desktop'
        self.app = self.mount / 'Media.app'
        self.expected = self.desktop / 'target/release/bundle/macos/Media.app/Contents/Resources/versions.json'
        self.actual = self.app / 'Contents/Resources/versions.json'
        self.record = {'desktop_version':'local-new','frontend_build_version':'new-source','agent_version':'0.3.0'}
        for target in (self.expected, self.actual):
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(self.record))
        self.stack.enter_context(mock.patch.object(harness, 'DMG_MOUNT', self.mount))
        self.stack.enter_context(mock.patch.object(harness, 'DESKTOP_DIR', self.desktop))
        self.stack.enter_context(mock.patch.object(harness, 'current_dmg', return_value=root/'new.dmg'))
        self.stack.enter_context(mock.patch.object(harness, 'close_desktop_app'))
        self.stack.enter_context(mock.patch.object(harness.subprocess, 'run', return_value=SimpleNamespace(returncode=16)))
        self.run = self.stack.enter_context(mock.patch.object(harness, 'run'))
        self.handover = self.stack.enter_context(mock.patch.object(harness, 'hand_over_agent_port'))

    def test_busy_previous_mount_refuses_attach_and_open(self):
        self.stack.enter_context(mock.patch.object(Path, 'is_mount', return_value=True))
        self.run.side_effect = subprocess.CalledProcessError(16, 'hdiutil detach')
        with self.assertRaises(subprocess.CalledProcessError):
            harness.launch_dmg()
        self.assertEqual(self.run.call_args_list, [mock.call(['hdiutil','detach',str(self.mount)])])
        self.handover.assert_not_called()

    def test_reported_success_without_detach_refuses_overlay_mount(self):
        self.stack.enter_context(mock.patch.object(Path, 'is_mount', return_value=True))
        with self.assertRaisesRegex(RuntimeError, 'still mounted'):
            harness.launch_dmg()
        self.handover.assert_not_called()
        self.assertFalse(any(call.args[0][0]=='open' for call in self.run.call_args_list))

    def test_stale_bundle_record_refuses_handover_and_open(self):
        self.stack.enter_context(mock.patch.object(Path, 'is_mount', return_value=False))
        self.actual.write_text(json.dumps(dict(self.record,frontend_build_version='old-source')))
        with self.assertRaisesRegex(RuntimeError, 'mounted Desktop source differs'):
            harness.launch_dmg()
        self.handover.assert_not_called()
        self.assertFalse(any(call.args[0][0]=='open' for call in self.run.call_args_list))

    def test_matching_finalized_bundle_opens_after_verification(self):
        self.stack.enter_context(mock.patch.object(Path, 'is_mount', return_value=False))
        harness.launch_dmg()
        self.handover.assert_called_once_with()
        self.assertEqual(self.run.call_args_list[-1],mock.call(['open',str(self.app)]))
