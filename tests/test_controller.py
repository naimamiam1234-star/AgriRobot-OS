import math
import tempfile
import unittest
from pathlib import Path
from app.controller import Controller
from app.store import Store


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'events.db'
        self.store = Store(self.path)
        self.c = Controller(self.store)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_disabled_on_start_and_no_real_driver(self):
        self.assertEqual(self.c.state, 'disabled')
        with self.assertRaises(ValueError):
            self.c.request_dose('a', 'p1', 10, approved=True)
        with self.assertRaises(ValueError):
            self.c.enable_simulation(persistent=True, hardware=True)

    def test_invalid_volumes_never_reserved(self):
        self.c.enable_simulation(persistent=True)
        for value in [-1, 0, math.nan, math.inf, True, '12', 501]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.c.request_dose('bad', 'p1', value, approved=True)
        self.assertEqual(self.store.doses(), [])

    def test_approval_and_persistence_required(self):
        with self.assertRaises(ValueError):
            self.c.enable_simulation(persistent=False)
        self.c.enable_simulation(persistent=True)
        with self.assertRaises(ValueError):
            self.c.request_dose('a', 'p', 20)

    def test_duplicate_rejected_after_restart(self):
        self.c.enable_simulation(persistent=True)
        result = self.c.request_dose('a', 'p1', 10, approved=True)
        self.assertEqual(result['status'], 'simulated')
        self.store.close()
        self.store = Store(self.path)
        self.c = Controller(self.store)
        self.c.enable_simulation(persistent=True)
        with self.assertRaises(ValueError):
            self.c.request_dose('a', 'p1', 10, approved=True)
        self.assertEqual(len(self.store.doses()), 1)

    def test_stop_and_link_loss_require_explicit_enable(self):
        self.c.enable_simulation(persistent=True)
        self.c.stop('test')
        with self.assertRaises(ValueError):
            self.c.request_dose('a', 'p', 10, approved=True)
        self.c.enable_simulation(persistent=True)
        self.c.link_lost()
        self.assertEqual(self.c.state, 'stopped')

    def test_daily_limit_and_independent_channels(self):
        self.c.enable_simulation(persistent=True)
        for i in range(4):
            self.c.request_dose(str(i), 'p', 500, approved=True)
        with self.assertRaises(ValueError):
            self.c.request_dose('extra', 'p', 1, approved=True)
        with self.assertRaises(ValueError):
            self.c.request_dose('fert', 'p', 1, approved=True, channel='fertilizer')

    def test_pending_dose_blocks_enable(self):
        self.store.reserve('pending', 'p', 10, 'water')
        self.c = Controller(self.store)
        with self.assertRaises(ValueError):
            self.c.enable_simulation(persistent=True)

    def test_invalid_identifiers_and_nonboolean_approval(self):
        self.c.enable_simulation(persistent=True)
        for request_id, plant_id, approved in [('', 'p', True), ('x', '', True), ('x', 'p', 'yes')]:
            with self.assertRaises(ValueError):
                self.c.request_dose(request_id, plant_id, 10, approved=approved)
