import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from app.ai import LocalAI


class TransportTests(unittest.TestCase):
    def test_local_reply_malformed_and_redirect(self):
        class Handler(BaseHTTPRequestHandler):
            mode='ok'
            redirected=False
            def log_message(self,*args): pass
            def do_GET(self):
                Handler.redirected=True
                self.send_response(200);self.end_headers();self.wfile.write(b'{}')
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                if Handler.mode=='redirect':
                    self.send_response(302);self.send_header('Location','/cloud');self.end_headers()
                else:
                    self.send_response(200);self.end_headers()
                    self.wfile.write(b'not-json' if Handler.mode=='bad' else json.dumps({'choices':[{'message':{'content':'local answer'}}]}).encode())
        server=HTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                model=Path(d)/'test.gguf';model.touch()
                ai=LocalAI({'language_model':str(model),'local_port':server.server_port})
                self.assertEqual(ai.chat('hello').get('text'),'local answer')
                Handler.mode='bad'
                self.assertEqual(ai.chat('hello')['status'],'error')
                Handler.mode='redirect'
                self.assertEqual(ai.chat('hello')['status'],'error')
                self.assertFalse(Handler.redirected)
        finally:
            server.shutdown();server.server_close()
