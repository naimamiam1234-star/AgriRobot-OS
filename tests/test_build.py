import subprocess
import unittest
from pathlib import Path


class BuildTests(unittest.TestCase):
    def test_preflight_reports_capability_or_missing_tools(self):
        p=subprocess.run(['bash','scripts/preflight.sh'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('MISSING',p.stdout)

    def test_builder_no_arguments_does_not_mutate(self):
        p=subprocess.run(['bash','iso/build.sh'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('--build',p.stdout+p.stderr)
        self.assertFalse(Path('iso/work').exists())
