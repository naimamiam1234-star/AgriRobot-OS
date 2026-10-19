import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class AssistantCLITests(unittest.TestCase):
    def test_bundled_transcription_without_engine_on_path(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree('app',root/'app')
            (root/'config').mkdir();(root/'bin').mkdir();(root/'models').mkdir()
            (root/'models/tiny.bin').write_bytes(b'fixture')
            (root/'audio.wav').write_bytes(b'fixture')
            (root/'config/models.json').write_text(json.dumps({'whisper_model':'models/tiny.bin'}))
            exe=root/'bin/whisper-cli'
            exe.write_text('#!/usr/bin/python3\nimport sys\nfrom pathlib import Path\nPath(sys.argv[sys.argv.index("-of")+1]+".txt").write_text("bundled transcription")\n')
            exe.chmod(0o755)
            env=dict(os.environ,PATH='/usr/bin:/bin',PYTHONPATH=str(root))
            p=subprocess.run([sys.executable,'-m','app.assistant','transcribe',str(root/'audio.wav')],
                             cwd=root,env=env,text=True,capture_output=True,check=True)
            self.assertEqual(json.loads(p.stdout).get('text'),'bundled transcription')
