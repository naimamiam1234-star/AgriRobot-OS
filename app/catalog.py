"""Offline reference-photo search. This is not an image classifier."""
import argparse
import json
from pathlib import Path
from .resources import verify_record

ROOT=Path(__file__).resolve().parent.parent
MANIFESTS=('plantdoc-sample-manifest.json','insect-sample-manifest.json')


def rows():
    records=[]
    for name in MANIFESTS:
        records.extend(json.loads((ROOT/'data'/name).read_text()))
    return records


def search(query):
    query=query.casefold().strip()
    return [r for r in rows() if 'path' in r and query in ' '.join(
        [r.get('label_original',''),r.get('label_ar','')]).casefold()]


def validate_all():
    failures=[]
    for row in rows():
        result=verify_record(ROOT,row)
        if result!='ok': failures.append({'path':row.get('path'),'error':result})
    return failures


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?',default='')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    result=validate_all() if args.verify else search(args.query)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.verify and result: raise SystemExit(1)


if __name__=='__main__': main()
