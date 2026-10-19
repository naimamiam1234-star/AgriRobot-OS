import hashlib
from pathlib import Path


def verify_record(root, record):
    if not all(record.get(k) for k in ('license','source_page','attribution')):
        return 'missing_attribution_or_license'
    base=Path(root).resolve()
    candidate=(base/record.get('path','')).resolve()
    if not candidate.is_relative_to(base) or candidate==base:
        return 'unsafe_path'
    if not candidate.is_file():
        return 'missing_file'
    digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
    return 'ok' if digest==record.get('sha256') else 'checksum_mismatch'
