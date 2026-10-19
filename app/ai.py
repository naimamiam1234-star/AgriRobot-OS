"""Optional local adapters. No downloads and no controller access."""
import json
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


class LocalAI:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def unavailable(reason):
        return {'status': 'unavailable', 'reason': reason}

    def chat(self, prompt):
        if not isinstance(prompt, str) or not 0 < len(prompt) <= 4000:
            raise ValueError('prompt_length_1_to_4000')
        model = self.config.get('language_model', '')
        if not model or not Path(model).is_file():
            return self.unavailable('language_model_not_installed')
        messages = [{'role': 'system', 'content': 'أجب باختصار من الملاحظات الموثقة فقط. لا تؤكد تشخيص مرض ولا تصدر أوامر للمضخات.'},
                    {'role': 'user', 'content': prompt}]
        body = json.dumps({'messages': messages, 'max_tokens': 160, 'temperature': 0.2,
                           'chat_template_kwargs': {'enable_thinking': False}}).encode()
        port = self.config.get('local_port', 8081)
        if type(port) is not int or not 1 <= port <= 65535:
            raise ValueError('invalid_local_port')
        # Disable proxy environment variables and redirects: inference stays local.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        transport = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions', body,
                                     {'Content-Type': 'application/json'})
        try:
            with transport.open(req, timeout=30) as response:
                raw = response.read(65537)
            if len(raw) > 65536:
                return {'status': 'error', 'reason': 'response_too_large'}
            value = json.loads(raw)['choices'][0]['message']['content']
            if not isinstance(value, str):
                raise ValueError('invalid_content')
            return {'status': 'ok', 'text': value, 'source': 'local_general_model'}
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            return {'status': 'error', 'reason': 'local_model_server_unavailable_or_invalid'}

    def transcribe(self, audio_path):
        model = self.config.get('whisper_model', '')
        exe = shutil.which('whisper-cli')
        if not exe or not model or not Path(model).is_file() or not Path(audio_path).is_file():
            return self.unavailable('whisper_or_audio_not_installed')
        with tempfile.TemporaryDirectory() as tmp:
            output = str(Path(tmp) / 'transcript')
            try:
                subprocess.run([exe, '-m', model, '-f', str(Path(audio_path).resolve()), '-l', 'ar',
                                '-otxt', '-of', output], timeout=60, check=True, capture_output=True)
                return {'status': 'ok', 'text': Path(output + '.txt').read_text()}
            except (OSError, subprocess.SubprocessError):
                return {'status': 'error', 'reason': 'transcription_failed'}

    def speak(self, text, output_path):
        if not isinstance(text, str) or not 0 < len(text) <= 4000:
            raise ValueError('invalid_speech_text')
        if self.config.get('speech_engine') == 'espeak-ng':
            exe = shutil.which('espeak-ng')
            if not exe: return self.unavailable('espeak_ng_not_installed')
            try:
                subprocess.run([exe, '-v', 'ar', '-w', str(Path(output_path).resolve()), '--stdin'],
                               input=text.encode(), timeout=60, capture_output=True, check=True)
                return {'status':'ok', 'path':str(output_path), 'engine':'espeak-ng_formant'}
            except (OSError, subprocess.SubprocessError):
                return {'status':'error', 'reason':'speech_failed'}
        model = self.config.get('piper_model', '')
        exe = shutil.which('piper')
        if not exe or not model or not Path(model).is_file():
            return self.unavailable('piper_or_voice_not_installed')
        try:
            subprocess.run([exe, '--model', model, '--output_file', str(Path(output_path).resolve())],
                           input=text.encode(), timeout=60, capture_output=True, check=True)
            return {'status': 'ok', 'path': str(output_path)}
        except (OSError, subprocess.SubprocessError):
            return {'status': 'error', 'reason': 'speech_failed'}

    def inspect_image(self, path):
        model = self.config.get('vision_model', '')
        if not model or not Path(model).is_file() or not Path(path).is_file():
            return self.unavailable('vision_model_or_image_not_installed')
        try:
            from .vision import inspect_image
            return inspect_image(model, path)
        except ImportError:
            return self.unavailable('onnx_runtime_or_opencv_not_installed')
        except Exception:
            return {'status': 'error', 'reason': 'vision_inference_failed'}
