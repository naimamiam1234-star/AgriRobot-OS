import unittest
import numpy as np
from app.vision import decode_detections


class VisionTests(unittest.TestCase):
    def test_overlapping_boxes_are_suppressed_per_class(self):
        # Three YOLO candidates, xywh and two class probabilities. First two overlap.
        pred = np.array([[50,50,40,40,.9,.1], [51,51,40,40,.8,.1],
                         [50,50,40,40,.1,.85]], dtype=np.float32).T[None,:,:]
        out = decode_detections(pred, {0:'person',1:'car'}, (100,100), 1, (0,0))
        self.assertEqual([x['name'] for x in out], ['person','car'])
        self.assertEqual(out[0]['box'], [30.0,30.0,70.0,70.0])

    def test_empty_and_low_confidence_are_not_diagnoses(self):
        pred = np.array([[50,50,40,40,.1,.2]], dtype=np.float32).T[None,:,:]
        self.assertEqual(decode_detections(pred, {0:'person',1:'car'}, (100,100), 1,(0,0)), [])
