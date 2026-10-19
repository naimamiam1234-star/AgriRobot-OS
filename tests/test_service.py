import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from app.server import make_server


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = make_server(Path(self.tmp.name), token='test-secret', port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server.store.close()
        self.tmp.cleanup()

    def req(self, method, path, obj=None, auth=False, headers=None):
        c = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        h = {'Content-Type': 'application/json'}
        if auth: h['Authorization'] = 'Bearer test-secret'
        h.update(headers or {})
        c.request(method, path, body=None if obj is None else json.dumps(obj), headers=h)
        r = c.getresponse()
        out = (r.status, json.loads(r.read()))
        c.close()
        return out

    def test_health_local_and_status_authenticated(self):
        self.assertEqual(self.req('GET', '/health')[0], 200)
        self.assertEqual(self.req('GET', '/status')[0], 401)
        status, data = self.req('GET', '/status', auth=True)
        self.assertEqual(status, 200)
        self.assertIsNone(data['sensors']['soil_moisture'])
        self.assertEqual(data['hardware'], 'not_implemented')
        self.assertFalse(data['models_bundled'])

    def test_no_unauthorized_or_browser_mutations(self):
        self.assertEqual(self.req('POST', '/stop', {})[0], 401)
        self.assertEqual(self.req('POST', '/stop', {}, True, {'Origin':'https://evil.example'})[0], 403)

    def test_simulation_and_duplicate(self):
        self.assertEqual(self.req('POST', '/dose', {'request_id':'one','plant_id':'p','volume_ml':20,'approved':True}, True)[0], 400)
        self.assertEqual(self.req('POST', '/simulation/enable', {}, True)[0], 200)
        obj={'request_id':'one','plant_id':'p','volume_ml':20,'approved':True}
        self.assertEqual(self.req('POST', '/dose', obj, True)[1]['status'], 'simulated')
        self.assertEqual(self.req('POST', '/dose', obj, True)[0], 400)

    def test_oversized_and_nonobject_json(self):
        self.assertEqual(self.req('POST', '/stop', ['bad'], True)[0], 400)
        self.assertEqual(self.req('POST', '/stop', {}, True, {'Content-Length':'20000'})[0], 413)

    def test_no_physical_endpoint(self):
        self.assertEqual(self.req('POST', '/hardware/enable', {}, True)[0], 404)

    def test_robot_context_is_authenticated_read_only_and_unconfigured(self):
        self.assertEqual(self.req('GET','/robot/context')[0],401)
        status,data=self.req('GET','/robot/context',auth=True)
        self.assertEqual(status,200)
        self.assertEqual(data['boards'],[])
        self.assertFalse(data['physical_output'])
        self.assertEqual(self.req('POST','/robot/context',{},True)[0],404)
