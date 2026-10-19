import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests.boot.run import boot


class BootEvidenceTests(unittest.TestCase):
    def test_old_ready_marker_cannot_pass_new_boot(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'boot-bios.log').write_text('AGRIROBOT_BOOT_READY\n')
            exe=root/'qemu-system-x86_64'
            exe.write_text('#!/bin/sh\nsleep 0.2\nexit 1\n');exe.chmod(0o755)
            with patch.dict(os.environ,{'PATH':str(root)+':/usr/bin:/bin'}):
                result=boot('bios','/missing.iso',root,timeout=1,poll_interval=.01)
            self.assertEqual(result['status'],'failed')
