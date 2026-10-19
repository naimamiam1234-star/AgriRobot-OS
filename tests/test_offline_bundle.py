import tempfile
import unittest
from pathlib import Path
from app import runtime


class OfflineBundleTests(unittest.TestCase):
    def test_readiness_requires_weights_and_engine(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = {'language_model': 'models/chat.gguf', 'whisper_model': 'models/tiny.bin'}
            self.assertEqual(runtime.readiness(root, cfg)['language']['status'], 'unavailable')
            (root/'models').mkdir()
            (root/'models/chat.gguf').write_bytes(b'weight')
            self.assertEqual(runtime.readiness(root, cfg)['language']['status'], 'unavailable')
            (root/'bin').mkdir()
            p = root/'bin/llama-server';p.write_text('engine');p.chmod(0o755)
            self.assertEqual(runtime.readiness(root, cfg)['language']['status'], 'installed_not_health_checked')
            self.assertEqual(runtime.readiness(root, cfg)['speech_to_text']['status'], 'unavailable')

    def test_paths_cannot_escape_bundle(self):
        with tempfile.TemporaryDirectory() as d:
            state = runtime.readiness(Path(d), {'language_model':'../elsewhere.gguf'})
            self.assertEqual(state['language']['status'], 'unavailable')

    def test_vision_presence_alone_does_not_report_runtime_installed(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'vision.onnx').touch()
            with patch('importlib.util.find_spec',return_value=None):
                state=runtime.readiness(root,{'vision_model':'vision.onnx'})
            self.assertEqual(state.get('vision',{}).get('status'),'unavailable')
