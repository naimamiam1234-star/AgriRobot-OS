import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from app.assets import fetch_asset


class AssetTests(unittest.TestCase):
    def record(self, data=b'checked model'):
        return {'path':'models/test.bin','url':'https://example.org/test.bin',
                'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),
                'license':'test-fixture','source_page':'https://example.org'}

    def test_download_hash_and_cache(self):
        with tempfile.TemporaryDirectory() as d:
            row=self.record()
            self.assertEqual(fetch_asset(Path(d),row,opener=lambda _:io.BytesIO(b'checked model')),'downloaded')
            self.assertEqual(fetch_asset(Path(d),row,opener=lambda _:self.fail('cache should avoid network')),'cached')

    def test_corruption_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'models/test.bin';p.parent.mkdir();p.write_bytes(b'old')
            row=self.record(b'new')
            with self.assertRaises(ValueError):fetch_asset(root,row,opener=lambda _:io.BytesIO(b'bad'))
            self.assertEqual(p.read_bytes(),b'old')

    def test_paths_and_unlicensed_or_non_https_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for key,value in [('path','../outside.bin'),('license',''),('url','http://example.org/test'),('size',True)]:
                row=self.record();row[key]=value
                with self.subTest(key=key), self.assertRaises(ValueError):
                    fetch_asset(Path(d),row,opener=lambda _:self.fail('must reject before network'))

    def test_oversized_transfer_rejected_and_partial_removed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):fetch_asset(Path(d),self.record(),opener=lambda _:io.BytesIO(b'x'*100))
            self.assertFalse((Path(d)/'models/test.bin').exists())
            self.assertEqual(list(Path(d).rglob('*.part')),[])
