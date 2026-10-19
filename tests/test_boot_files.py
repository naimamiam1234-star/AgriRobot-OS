import subprocess
import tempfile
import unittest
from pathlib import Path


class BootFilesTests(unittest.TestCase):
    def test_versioned_boot_files_work_without_root_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';boot=root/'boot';boot.mkdir(parents=True)
            dest=Path(d)/'image'/'casper'
            for version in ['6.8.0-9-generic','6.8.0-147-generic']:
                (boot/('vmlinuz-'+version)).write_text('kernel-'+version)
                (boot/('initrd.img-'+version)).write_text('initrd-'+version)
            p=subprocess.run(['bash','scripts/copy-boot.sh',str(root),str(dest)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual((dest/'vmlinuz').read_text(),'kernel-6.8.0-147-generic')
            self.assertEqual((dest/'initrd').read_text(),'initrd-6.8.0-147-generic')

    def test_missing_matching_initrd_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'root';boot=root/'boot';boot.mkdir(parents=True)
            (boot/'vmlinuz-6.8.0-147-generic').touch()
            dest=Path(d)/'out'
            p=subprocess.run(['bash','scripts/copy-boot.sh',str(root),str(dest)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertFalse((dest/'vmlinuz').exists())
