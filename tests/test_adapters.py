import tempfile
import unittest
from pathlib import Path
from app.ai import LocalAI


class AdapterTests(unittest.TestCase):
    def test_missing_executables_and_models_are_unavailable(self):
        ai = LocalAI({})
        self.assertEqual(ai.chat('hello')['status'], 'unavailable')
        self.assertEqual(ai.transcribe('/missing.wav')['status'], 'unavailable')
        self.assertEqual(ai.speak('hello','/tmp/out.wav')['status'], 'unavailable')
        self.assertEqual(ai.inspect_image('/missing.jpg')['status'], 'unavailable')

    def test_bad_prompt_rejected(self):
        with self.assertRaises(ValueError): LocalAI({}).chat('x'*5000)

    def test_no_shell_interpolation_and_missing_camera(self):
        with tempfile.TemporaryDirectory() as d:
            ai=LocalAI({'vision_model':str(Path(d)/'missing.pt')})
            self.assertEqual(ai.inspect_image('$(touch /tmp/should-not-exist)')['status'],'unavailable')

    def test_speech_fallback_is_explicit_and_validates_input(self):
        from unittest.mock import patch
        ai = LocalAI({'speech_engine':'espeak-ng'})
        with patch('app.ai.shutil.which',return_value='/usr/bin/espeak-ng'), patch('app.ai.subprocess.run') as run:
            result = ai.speak('مرحبا','/tmp/voice.wav')
            self.assertEqual(result.get('engine'),'espeak-ng_formant')
            self.assertEqual(run.call_args.args[0][1:3],['-v','ar'])
            self.assertEqual(run.call_args.kwargs['input'],'مرحبا'.encode())
        with self.assertRaises(ValueError): ai.speak('', '/tmp/voice.wav')
