"""Local installation evidence; presence is never reported as successful inference."""
import os
import importlib.util
import shutil
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
    vision = (root / config.get('vision_model','__missing__')).resolve()
    installed = (vision.is_relative_to(root) and vision.is_file()
                 and importlib.util.find_spec('onnxruntime') is not None
                 and importlib.util.find_spec('cv2') is not None)
    result['vision'] = {'status':'installed_not_health_checked' if installed else 'unavailable',
                        'scope':'general_objects_not_crop_diagnosis'}
    result['speech_output'] = {'status':'installed_not_health_checked' if
        config.get('speech_engine') == 'espeak-ng' and shutil.which('espeak-ng') else 'unavailable'}
    return result
