#!/usr/bin/env python3

import random
import unittest

from yolox.data.data_augment import sample_rotation_angle


class TestRotationAugment(unittest.TestCase):
    def test_legacy_float_degrees(self):
        random.seed(0)
        for _ in range(100):
            angle = sample_rotation_angle(10.0)
            self.assertGreaterEqual(angle, -10.0)
            self.assertLessEqual(angle, 10.0)

    def test_single_range(self):
        random.seed(0)
        for _ in range(100):
            angle = sample_rotation_angle((-5.0, 5.0))
            self.assertGreaterEqual(angle, -5.0)
            self.assertLessEqual(angle, 5.0)

    def test_multi_range_buckets(self):
        ranges = [(-10.0, 10.0), (-100.0, -80.0), (80.0, 100.0)]
        random.seed(0)
        for _ in range(300):
            angle = sample_rotation_angle(ranges)
            in_small = -10.0 <= angle <= 10.0
            in_neg90 = -100.0 <= angle <= -80.0
            in_pos90 = 80.0 <= angle <= 100.0
            self.assertTrue(in_small or in_neg90 or in_pos90, msg=angle)


if __name__ == "__main__":
    unittest.main()
