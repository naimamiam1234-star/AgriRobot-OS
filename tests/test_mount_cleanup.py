import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class MountCleanupTests(unittest.TestCase):
    def test_recursive_unmount_required_and_failure_blocks_packaging(self):
        helper=Path('scripts/mount-cleanup.sh').resolve()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            exe=root/'umount'
            exe.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$LOG"\nexit "${FAIL:-0}"\n')
            exe.chmod(0o755)
            env={**os.environ,'PATH':d+':'+os.environ['PATH'],'LOG':str(root/'log'),'FAIL':'1'}
            command='source "$1"; mounts=(/tmp/rootfs/dev /tmp/rootfs/proc); cleanup_mounts && touch "$2"'
            p=subprocess.run(['bash','-c',command,'test',str(helper),str(root/'packaged')],env=env,capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertFalse((root/'packaged').exists())
            self.assertEqual((root/'log').read_text().splitlines(),['--recursive /tmp/rootfs/proc','--recursive /tmp/rootfs/dev'])
            env['FAIL']='0'
            p=subprocess.run(['bash','-c',command,'test',str(helper),str(root/'packaged')],env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0)
            self.assertTrue((root/'packaged').exists())
