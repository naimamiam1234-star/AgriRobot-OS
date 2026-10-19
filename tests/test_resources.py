import hashlib
import tempfile
import unittest
from pathlib import Path
from app.resources import verify_record


class ResourceTests(unittest.TestCase):
    def test_valid_file_and_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.jpg';p.write_bytes(b'photo')
            row={'path':'x.jpg','sha256':hashlib.sha256(b'photo').hexdigest(),'license':'CC-BY-4.0','source_page':'https://example.org','attribution':'Author'}
            self.assertEqual(verify_record(Path(d),row),'ok')
            p.write_bytes(b'changed')
            self.assertEqual(verify_record(Path(d),row),'checksum_mismatch')

    def test_traversal_missing_license_and_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            row={'path':'../outside.jpg','sha256':'0'*64,'license':'CC0','source_page':'https://example.org','attribution':'Author'}
            self.assertEqual(verify_record(Path(d),row),'unsafe_path')
            row['path']='x.jpg'
            self.assertEqual(verify_record(Path(d),row),'missing_file')
            row['license']=''
            self.assertEqual(verify_record(Path(d),row),'missing_attribution_or_license')
