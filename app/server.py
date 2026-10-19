"""Loopback-only by default. Experimental operator API, not a public server."""
import argparse
import hmac
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .controller import Controller
from .store import Store
from .runtime import readiness
from .device_registry import DeviceRegistry


def make_server(data_dir, token, port=8080, host='127.0.0.1', assembly=None):
    if not isinstance(token, str) or not token:
        raise ValueError('authentication_token_required')
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    store = Store(data_dir / 'events.db')
    controller = Controller(store)
    registry = DeviceRegistry(assembly if assembly is not None else {"boards": []})

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *args):
            pass  # Do not log tokens, prompts or headers.

        def send_json(self, status, value):
            body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            return hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token)

        def do_GET(self):
            if self.path == '/health':
                return self.send_json(200, {'status': 'ok', 'version': '0.1.0-dev'})
            if not self.authorized():
                return self.send_json(401, {'error': 'unauthorized'})
            if self.path == '/status':
                installed = readiness(Path(__file__).resolve().parent.parent,
                    json.loads((Path(__file__).resolve().parent.parent/'config/models.json').read_text()))
                return self.send_json(200, {
                    'state': controller.state, 'mode': 'development_simulation_only',
                     'hardware': 'not_implemented',
                    'models_bundled': all(v['status'] == 'installed_not_health_checked' for v in installed.values()),
                    'ai_installation': installed,
                    'sensors': {'soil_moisture': None, 'temperature': None,
                                'water_level': None, 'fertilizer_level': None},
                    'storage': 'operator_must_verify_persistence_on_live_usb'})
            if self.path == '/robot/context':
                return self.send_json(200, registry.context())
            if self.path == '/events':
                return self.send_json(200, {'events': store.events(), 'doses': store.doses()})
            return self.send_json(404, {'error': 'not_found'})

        def do_POST(self):
            if not self.authorized():
                return self.send_json(401, {'error': 'unauthorized'})
            if self.headers.get('Origin') or self.headers.get('Sec-Fetch-Site'):
                return self.send_json(403, {'error': 'browser_mutation_not_supported'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.send_json(415, {'error': 'json_required'})
            if self.headers.get('Transfer-Encoding'):
                return self.send_json(400, {'error': 'unsupported_transfer_encoding'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    return self.send_json(413, {'error': 'invalid_body_size'})
                obj = json.loads(self.rfile.read(size), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))
                if not isinstance(obj, dict):
                    raise ValueError('json_object_required')
                if self.path == '/stop':
                    controller.stop()
                    result = {'status': 'stopped', 'physical_output': False}
                elif self.path == '/simulation/enable':
                    controller.enable_simulation(persistent=True)
                    result = {'status': 'simulation_ready', 'physical_output': False}
                elif self.path == '/dose':
                    result = controller.request_dose(**obj)
                else:
                    return self.send_json(404, {'error': 'not_found'})
                self.send_json(200, result)
            except (ValueError, TypeError, UnicodeError):
                self.send_json(400, {'error': 'invalid_or_disallowed_request'})

    server = ThreadingHTTPServer((host, port), Handler)
    server.store = store
    server.controller = controller
    server.registry = registry
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='runtime')
    parser.add_argument('--assembly', help='Validated expected-device assembly JSON; no automatic probing')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    root = Path(args.data)
    root.mkdir(parents=True, exist_ok=True)
    token_file = root / 'operator.token'
    if not token_file.exists():
        fd = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(secrets.token_urlsafe(32))
    assembly = json.loads(Path(args.assembly).read_text()) if args.assembly else None
    server = make_server(root, token_file.read_text().strip(), args.port, args.host, assembly)
    print(f'AgriRobot API http://{args.host}:{server.server_port} — development, no physical actuation', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.store.close()


if __name__ == '__main__':
    main()
