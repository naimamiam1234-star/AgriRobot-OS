import json
import unittest
from app.device_registry import DeviceRegistry, encode_frame, decode_frame


def assembly():
    return {'boards':[{'board_id':'sensor-board','firmware':'agri-sensor-1',
        'components':[{'id':'soil','port':'ANALOG_SOIL','unit':'raw'}]}]}


class DeviceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.now=0.
        self.registry=DeviceRegistry(assembly(),clock=lambda:self.now,ttl=3)
        self.registry.open_session('sensor-board','session-1')

    def frame(self,seq,kind,payload,session='session-1'):
        return encode_frame({'v':1,'board_id':'sensor-board','session':session,
                             'seq':seq,'type':kind,'payload':payload})

    def hello(self):
        self.registry.receive(self.frame(0,'hello',{'firmware':'agri-sensor-1'}))

    def test_crc_and_size(self):
        wire=self.frame(0,'hello',{'firmware':'agri-sensor-1'})
        self.assertEqual(decode_frame(wire)['seq'],0)
        with self.assertRaises(ValueError):decode_frame(wire.replace(b'agri-sensor',b'wrong-sensor'))
        with self.assertRaises(ValueError):decode_frame(b'x'*769)

    def test_duplicate_keys_and_nonfinite_rejected(self):
        with self.assertRaises(ValueError):decode_frame(b'{"body":"a","body":"b","crc32":"00000000"}\n')
        with self.assertRaises(ValueError):self.frame(1,'telemetry',{'component_id':'soil','value':float('nan'),'unit':'raw'})
        with self.assertRaises(ValueError):self.frame(True,'heartbeat',{})

    def test_handshake_required_and_replay_rejected(self):
        with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'heartbeat',{}))
        self.hello()
        with self.assertRaises(ValueError):self.hello()

    def test_board_cannot_claim_verified_component(self):
        self.hello()
        with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'telemetry',{
            'component_id':'soil','value':42,'unit':'raw','evidence':'verified'}))
        self.registry.receive(self.frame(1,'telemetry',{'component_id':'soil','value':42,'unit':'raw'}))
        ctx=self.registry.context()
        self.assertEqual(ctx['boards'][0]['components'][0]['evidence'],'observed')
        self.assertFalse(ctx['physical_output'])

    def test_expiry_and_heartbeat_do_not_refresh_old_measurement(self):
        self.hello()
        self.registry.receive(self.frame(1,'telemetry',{'component_id':'soil','value':42,'unit':'raw'}))
        self.now=4
        self.registry.receive(self.frame(2,'heartbeat',{}))
        c=self.registry.context()['boards'][0]['components'][0]
        self.assertEqual(c['evidence'],'stale');self.assertIsNone(c['value'])
        self.assertEqual(c['last_observation']['value'],42)

    def test_reconnect_clears_measurements_and_old_session(self):
        self.hello()
        self.registry.open_session('sensor-board','session-2')
        with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'heartbeat',{}))
        self.assertEqual(self.registry.context()['boards'][0]['link'],'awaiting_hello')
        with self.assertRaises(ValueError):self.registry.open_session('sensor-board','session-1')

    def test_conflicting_firmware_blocks_telemetry(self):
        self.registry.receive(self.frame(0,'hello',{'firmware':'different'}))
        with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'telemetry',{'component_id':'soil','value':2,'unit':'raw'}))
        self.assertEqual(self.registry.context()['boards'][0]['link'],'conflict')

    def test_unknown_component_and_wrong_unit_do_not_consume_sequence(self):
        self.hello()
        for component,unit in [('unknown','raw'),('soil','percent')]:
            with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'telemetry',{'component_id':component,'value':4,'unit':unit}))
        self.registry.receive(self.frame(1,'heartbeat',{}))

    def test_port_conflict_rejected(self):
        a=assembly();a['boards'][0]['components'].append({'id':'pump','port':'ANALOG_SOIL','unit':'ml'})
        with self.assertRaises(ValueError):DeviceRegistry(a)

    def test_disconnected_board_has_no_current_measurement(self):
        self.hello();self.now=4
        board=self.registry.context()['boards'][0]
        self.assertEqual(board['link'],'stale')
        self.assertIsNone(board['components'][0]['value'])

    def test_oversized_numeric_measurement_is_rejected(self):
        self.hello()
        with self.assertRaises(ValueError):self.registry.receive(self.frame(1,'telemetry',{
            'component_id':'soil','value':10**300,'unit':'raw'}))
