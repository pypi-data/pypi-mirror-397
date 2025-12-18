"""Basic tests for quaternion helpers."""
import unittest
import math
import numpy as np
from jinwu.core import teldef_helpers as th


class TestQuatHelpers(unittest.TestCase):
    def test_axis_angle_rotation(self):
        # rotate (1,0,0) by 90 deg about Z -> (0,1,0)
        q = th.quat_from_axis_angle([0,0,1], math.pi/2)
        v = np.array([1.0, 0.0, 0.0])
        v2 = th.rotate_vector_by_quat(q, v)
        self.assertAlmostEqual(v2[0], 0.0, places=6)
        self.assertAlmostEqual(v2[1], 1.0, places=6)
        self.assertAlmostEqual(v2[2], 0.0, places=6)

    def test_quat_norm_and_mul(self):
        q1 = th.quat_from_axis_angle([1,0,0], math.pi/3)
        q2 = th.quat_from_axis_angle([0,1,0], math.pi/4)
        q = th.quat_mul(q1, q2)
        # product should be normalized (within tol)
        self.assertAlmostEqual(np.linalg.norm(q), 1.0, places=7)

    def test_radecroll_roundtrip(self):
        for ra in (0.0, 23.5, 180.0, 359.9):
            for dec in (-45.0, 0.0, 45.0):
                for roll in (-30.0, 0.0, 30.0, 123.4):
                    q = th.radecroll_to_quat(ra, dec, roll)
                    ra2, dec2, roll2 = th.quat_to_radecroll(q)
                    # normalize angles (wrap ra)
                    dra = ((ra2 - ra + 180.0) % 360.0) - 180.0
                    self.assertAlmostEqual(dra, 0.0, places=6)
                    self.assertAlmostEqual(dec2, dec, places=6)
                    # roll modulo 360
                    droll = ((roll2 - roll + 180.0) % 360.0) - 180.0
                    self.assertAlmostEqual(droll, 0.0, places=6)


if __name__ == '__main__':
    unittest.main()
