"""Fetch explicitly licensed, version-pinned assets with size and SHA256 checks."""
import argparse
import hashlib
import json
import os
import re
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


def file_hash(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def fetch_asset(root, record, opener=None):
    root=Path(root).resolve()
    target=(root/record.get('path','')).resolve()
    size=record.get('size')
    digest=record.get('sha256','')
    url=record.get('url','')
    if (not target.is_relative_to(root) or target==root or not record.get('license')
        or not record.get('source_page') or type(size) is not int or size<=0
        or not re.fullmatch('[a-f0-9]{64}',digest)
        or urllib.parse.urlsplit(url).scheme!='https'):
        raise ValueError('invalid_asset_record')
    if target.is_file() and target.stat().st_size==size and file_hash(target)==digest:
        return 'cached'
    target.parent.mkdir(parents=True,exist_ok=True)
    if opener is None:
        opener=lambda uri:urllib.request.urlopen(urllib.request.Request(uri,headers={'User-Agent':'AgriRobot-Assets/0.2'}),timeout=60)
    fd,name=tempfile.mkstemp(prefix=target.name+'.',suffix='.part',dir=target.parent)
    try:
        h=hashlib.sha256();received=0
        with os.fdopen(fd,'wb') as out, opener(url) as response:
            if hasattr(response,'geturl') and urllib.parse.urlsplit(response.geturl()).scheme!='https':
                raise ValueError('insecure_redirect')
            while True:
                block=response.read(1024*1024)
                if not block:break
                received+=len(block)
                if received>size:raise ValueError('oversized_asset')
                h.update(block);out.write(block)
            out.flush();os.fsync(out.fileno())
        if received!=size or h.hexdigest()!=digest:raise ValueError('asset_integrity_failure')
        os.replace(name,target)
        return 'downloaded'
    finally:
        Path(name).unlink(missing_ok=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',default='config/assets.lock.json')
    parser.add_argument('--root',default='.')
    args=parser.parse_args()
    records=json.loads(Path(args.manifest).read_text())['assets']
    for record in records:
        print(record['path'],fetch_asset(Path(args.root),record),flush=True)


if __name__=='__main__':main()
