"""Local installation evidence; presence is never reported as successful inference."""
import os
from pathlib import Path


def readiness(root, config):
    root = Path(root).resolve()
    result = {}
    for name, key, engine in [('language', 'language_model', 'llama-server'),
                              ('speech_to_text', 'whisper_model', 'whisper-cli')]:
        model = (root / config.get(key, '__missing__')).resolve()
        binary = root / 'bin' / engine
        installed = (model.is_relative_to(root) and model.is_file()
                     and binary.is_file() and os.access(binary, os.X_OK))
        result[name] = {'status': 'installed_not_health_checked' if installed else 'unavailable'}
    return result
