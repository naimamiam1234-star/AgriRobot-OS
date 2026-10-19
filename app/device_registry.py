"""Read-only controller evidence. No probing, serial writes or actuator access."""
import copy
import json
import math
import re
import secrets
import threading
import time
import zlib

MAX_FRAME = 768
_IDENTIFIER = re.compile(r'[A-Za-z0-9_.:-]{1,64}\Z')


def identifier(value):
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError('invalid_identifier')
    return value


def strict_json(text):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value: raise ValueError('duplicate_key')
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))


def validate_message(message):
    if not isinstance(message, dict) or set(message) != {'v','board_id','session','seq','type','payload'}:
        raise ValueError('invalid_message_fields')
    if type(message['v']) is not int or message['v'] != 1:
        raise ValueError('unsupported_protocol')
    identifier(message['board_id']); identifier(message['session'])
    if type(message['seq']) is not int or not 0 <= message['seq'] <= 0xffffffff:
        raise ValueError('invalid_sequence')
    if message['type'] not in ('hello','heartbeat','telemetry') or not isinstance(message['payload'],dict):
        raise ValueError('unsupported_message')
    return message


def encode_frame(message):
    validate_message(message)
    body = json.dumps(message,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    crc = f'{zlib.crc32(body.encode()):08x}'
    wire = (json.dumps({'body':body,'crc32':crc},ensure_ascii=False,separators=(',',':'))+'\n').encode()
    if len(wire) > MAX_FRAME: raise ValueError('frame_too_large')
    return wire


def decode_frame(wire):
    if not isinstance(wire, bytes) or not 0 < len(wire) <= MAX_FRAME or not wire.endswith(b'\n'):
        raise ValueError('invalid_frame_length_or_delimiter')
    envelope = strict_json(wire.decode('utf-8'))
    if not isinstance(envelope,dict) or set(envelope) != {'body','crc32'}:
        raise ValueError('invalid_envelope')
    body,crc = envelope['body'],envelope['crc32']
    if not isinstance(body,str) or not isinstance(crc,str) or not re.fullmatch('[0-9a-f]{8}',crc):
        raise ValueError('invalid_crc_fields')
    if f'{zlib.crc32(body.encode()):08x}' != crc: raise ValueError('crc_mismatch')
    return validate_message(strict_json(body))


def validate_assembly(assembly):
    if not isinstance(assembly,dict) or set(assembly) != {'boards'} or not isinstance(assembly['boards'],list) or len(assembly['boards']) > 8:
        raise ValueError('invalid_assembly')
    boards = {}
    for board in assembly['boards']:
        if not isinstance(board,dict) or set(board) != {'board_id','firmware','components'}:
            raise ValueError('invalid_board')
        bid=identifier(board['board_id']);identifier(board['firmware'])
        if bid in boards or not isinstance(board['components'],list) or len(board['components']) > 16:
            raise ValueError('duplicate_board_or_component_limit')
        ports=set();components=set()
        for c in board['components']:
            if not isinstance(c,dict) or set(c) != {'id','port','unit'}:
                raise ValueError('invalid_component')
            for value in c.values(): identifier(value)
            if c['port'] in ports or c['id'] in components: raise ValueError('port_or_component_conflict')
            ports.add(c['port']);components.add(c['id'])
        boards[bid]=copy.deepcopy(board)
    return boards


class DeviceRegistry:
    def __init__(self, assembly, clock=time.monotonic, ttl=3):
        if type(ttl) not in (int,float) or not math.isfinite(ttl) or not .1 <= ttl <= 60:
            raise ValueError('invalid_evidence_ttl')
        self.expected=validate_assembly(assembly)
        self.clock=clock;self.ttl=ttl;self.lock=threading.RLock()
        self.state={bid:{'session':None,'used_sessions':set(),'seq':-1,'hello':False,
                         'conflict':False,'last_heartbeat':None,'observations':{}}
                    for bid in self.expected}

    def open_session(self, board_id, session=None):
        with self.lock:
            identifier(board_id)
            if board_id not in self.state: raise ValueError('board_not_configured')
            session=identifier(session if session is not None else secrets.token_hex(12))
            state=self.state[board_id]
            if session in state['used_sessions'] or len(state['used_sessions']) >= 64:
                raise ValueError('session_reuse_or_session_budget_exhausted')
            state['used_sessions'].add(session)
            state.update(session=session,seq=-1,hello=False,conflict=False,
                         last_heartbeat=None,observations={})
            return session

    def receive(self, wire):
        message=decode_frame(wire)
        with self.lock:
            bid=message['board_id'];state=self.state.get(bid)
            if state is None or state['session'] is None or message['session'] != state['session']:
                raise ValueError('unknown_board_or_session')
            if message['seq'] <= state['seq']: raise ValueError('replayed_or_out_of_order_frame')
            kind,payload=message['type'],message['payload']
            now=self.clock()
            if kind == 'hello':
                if state['hello'] or message['seq'] != 0 or set(payload) != {'firmware'}:
                    raise ValueError('invalid_hello')
                identifier(payload['firmware'])
                state.update(hello=True,conflict=payload['firmware'] != self.expected[bid]['firmware'],
                             last_heartbeat=now)
            else:
                if not state['hello'] or state['conflict']: raise ValueError('handshake_missing_or_conflicting')
                if kind == 'heartbeat':
                    if payload: raise ValueError('invalid_heartbeat')
                    state['last_heartbeat']=now
                else:
                    if set(payload) != {'component_id','value','unit'}: raise ValueError('invalid_observation')
                    cid=identifier(payload['component_id'])
                    expected=next((c for c in self.expected[bid]['components'] if c['id']==cid),None)
                    value=payload['value']
                    if expected is None or payload['unit'] != expected['unit']:
                        raise ValueError('unknown_component_or_unit_mismatch')
                    if type(value) not in (int,float) or not -1e12 <= value <= 1e12 or not math.isfinite(value):
                        raise ValueError('invalid_measurement')
                    state['observations'][cid]={'value':value,'unit':payload['unit'],'received_at_monotonic':now,
                                               'source':'controller_report_unverified','session':state['session']}
            state['seq']=message['seq']
            return {'accepted':True,'physical_output':False}

    def context(self):
        with self.lock:
            now=self.clock();boards=[]
            for bid,expected in self.expected.items():
                state=self.state[bid]
                if state['conflict']: link='conflict'
                elif not state['hello']: link='awaiting_hello' if state['session'] else 'disconnected'
                elif now-state['last_heartbeat'] > self.ttl: link='stale'
                else: link='connected_report_unverified'
                components=[]
                for c in expected['components']:
                    observation=state['observations'].get(c['id'])
                    fresh=(observation is not None and link=='connected_report_unverified'
                           and now-observation['received_at_monotonic'] <= self.ttl)
                    item={**c,'evidence':'observed' if fresh else ('stale' if observation else 'declared'),
                          'value':observation['value'] if fresh else None,
                          'identity':'not_electronically_verified'}
                    if observation:
                        item['last_observation']={**observation,'age_seconds':max(0,now-observation['received_at_monotonic'])}
                    components.append(item)
                boards.append({'board_id':bid,'expected_firmware':expected['firmware'],
                               'link':link,'components':components})
            return copy.deepcopy({'boards':boards,'ttl_seconds':self.ttl,'physical_output':False,
                                  'scope':'read_only_controller_reports_not_hardware_verification'})
