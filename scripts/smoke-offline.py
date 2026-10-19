"""Run in a network namespace with loopback only; fail if real inference fails."""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

root = Path('/opt/agrirobot')
os.chdir(root)
sys.path.insert(0, str(root))
os.environ['PATH'] = str(root/'bin') + ':' + os.environ['PATH']
transport = urllib.request.build_opener(urllib.request.ProxyHandler({}))
report = {'network': 'isolated_namespace_loopback_only', 'tests': {}}
start = time.monotonic()
with tempfile.TemporaryFile() as log:
    proc = subprocess.Popen([str(root/'bin/llama-server'), '-m', 'models/Qwen3-0.6B-Q4_0.gguf',
                             '--host','127.0.0.1','--port','8081','-c','2048','-t','2','--jinja'],
                            stdout=log, stderr=log)
    try:
        for _ in range(180):
            if proc.poll() is not None:
                log.seek(0);raise RuntimeError(log.read().decode(errors='replace')[-8000:])
            try:
                with transport.open('http://127.0.0.1:8081/health', timeout=1) as res:
                    if res.status == 200: break
            except OSError: time.sleep(1)
        else: raise RuntimeError('language_model_startup_timeout')
        from app.ai import LocalAI
        ai = LocalAI(json.loads((root/'config/models.json').read_text()))
        result = ai.chat('قل مرحبا بجملة عربية قصيرة. /no_think')
        if result['status'] != 'ok' or not result.get('text','').strip():
            raise RuntimeError(str(result))
        report['tests']['language'] = {'status':'passed', 'seconds':round(time.monotonic()-start,2),
                                       'sample_output':result['text'], 'agronomic_accuracy':'not_evaluated'}
        begin = time.monotonic()
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [str(root/'bin/whisper-cli'), '-m', 'models/ggml-tiny.bin', '-f',
                   'data/inference-sample-jfk.wav', '-l','en','-otxt','-of',tmp+'/result']
            subprocess.run(cmd, check=True, timeout=180, capture_output=True)
            text = Path(tmp+'/result.txt').read_text().strip()
            if 'country' not in text.lower(): raise RuntimeError('speech_smoke_transcript_mismatch')
        report['tests']['speech_to_text'] = {'status':'passed','seconds':round(time.monotonic()-begin,2),
                                            'sample_output':text, 'arabic_accuracy':'not_evaluated'}
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp)/'speech.wav'
            speech = ai.speak('مرحبا، أنا مساعد الروبوت الزراعي.',wav)
            if speech['status'] != 'ok' or not wav.is_file() or wav.stat().st_size < 100:
                raise RuntimeError('speech_synthesis_failed')
            report['tests']['speech_output'] = {'status':'passed','engine':'espeak-ng_formant',
                                                'arabic_listening_quality':'not_evaluated'}
        begin = time.monotonic()
        image = next((root/'data/images').glob('*.jpg'))
        result = ai.inspect_image(image)
        if result['status'] != 'ok': raise RuntimeError(str(result))
        report['tests']['vision'] = {'status':'passed','seconds':round(time.monotonic()-begin,2),
                                    'scope':'COCO_general_detector_not_crop_diagnosis',
                                    'detections':result['detections']}
    finally:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill();proc.wait()
(root/'docs/offline-inference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
