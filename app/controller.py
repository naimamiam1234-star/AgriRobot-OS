"""Fail-closed simulation controller. Physical actuation is not implemented."""
import math
import re
import threading


class Controller:
    def __init__(self, store):
        self.store = store
        self.state = 'disabled'
        self.lock = threading.RLock()

    def enable_simulation(self, *, persistent=False, hardware=False):
        with self.lock:
            if persistent is not True or hardware is not False:
                raise ValueError('simulation_requires_persistent_storage_no_hardware')
            if self.store.pending():
                raise ValueError('pending_dose_needs_manual_review')
            self.state = 'simulation_ready'
            self.store.record_event({'type': 'simulation_enabled'})

    def request_dose(self, request_id, plant_id, volume_ml, *, approved=False, channel='water'):
        with self.lock:
            if self.state != 'simulation_ready' or approved is not True:
                raise ValueError('disabled_or_not_approved')
            if channel != 'water':
                raise ValueError('fertilizer_requires_validated_recipe_not_implemented')
            for value in (request_id, plant_id):
                if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
                    raise ValueError('invalid_identifier')
            if type(volume_ml) not in (int, float) or not math.isfinite(volume_ml) or not 0 < volume_ml <= 500:
                raise ValueError('invalid_volume_simulation_limit_500ml')
            self.store.reserve(request_id, plant_id, volume_ml, channel)
            self.store.finish_simulation(request_id)
            result = {'status': 'simulated', 'request_id': request_id, 'volume_ml': volume_ml,
                      'physical_output': False}
            self.store.record_event(result)
            return result

    def stop(self, reason='operator'):
        with self.lock:
            self.state = 'stopped'
            self.store.record_event({'type': 'stop', 'reason': reason})

    def link_lost(self):
        self.stop('link_lost')
