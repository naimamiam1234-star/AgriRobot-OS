"""Bounded replay of recorded controller frames; no live hardware communication."""
import argparse
import json
from pathlib import Path
from .device_registry import DeviceRegistry, MAX_FRAME


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly',required=True)
    parser.add_argument('--board',required=True)
    parser.add_argument('--session',required=True)
    parser.add_argument('frames',help='JSONL frames, at most 10,000 lines, 768 bytes per frame')
    args=parser.parse_args()
    registry=DeviceRegistry(json.loads(Path(args.assembly).read_text()))
    registry.open_session(args.board,args.session)
    count=0
    try:
        with open(args.frames,'rb') as stream:
            while wire:=stream.readline(MAX_FRAME+1):
                if count >= 10000: raise ValueError('frame_count_limit')
                registry.receive(wire);count+=1
    except (ValueError,UnicodeError) as exc:
        parser.exit(2,'Frame rejected: '+str(exc)+'\n')
    result=registry.context()
    result.update(input_mode='file_replay_no_live_transport',accepted_frames=count)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
