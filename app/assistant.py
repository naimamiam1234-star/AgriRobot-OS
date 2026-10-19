"""Offline assistant CLI. Run from /opt/agrirobot with venv/bin/python -m app.assistant."""
import argparse
import json
from pathlib import Path
from .ai import LocalAI
from .runtime import readiness


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['status','chat','transcribe','speak','inspect'])
    parser.add_argument('input',nargs='?',default='')
    parser.add_argument('--output',default='/tmp/agrirobot-speech.wav')
    args=parser.parse_args()
    root=Path(__file__).resolve().parent.parent
    config=json.loads((root/'config/models.json').read_text())
    for key in ['language_model','whisper_model','vision_model','piper_model']:
        if config.get(key):config[key]=str(root/config[key])
    ai=LocalAI(config)
    if args.action=='status':result=readiness(root,config)
    elif args.action=='chat':result=ai.chat(args.input)
    elif args.action=='transcribe':result=ai.transcribe(args.input)
    elif args.action=='speak':result=ai.speak(args.input,args.output)
    else:result=ai.inspect_image(args.input)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
