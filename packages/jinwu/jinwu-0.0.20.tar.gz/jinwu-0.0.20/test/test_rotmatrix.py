"""Tests for rotation matrix and XFORM2D helper."""
import unittest
import numpy as np
import math
from jinwu.core import teldef_helpers as th


class TestRotMatrix(unittest.TestCase):
    def test_quat_to_rot_orthonormal(self):
        q = th.quat_from_axis_angle([1, 1, 0], math.radians(23))
        R = th.quat_to_rotmatrix(q)
        # R @ R.T == I
        I = R @ R.T
        self.assertTrue(np.allclose(I, np.eye(3), atol=1e-12))

    def test_rotmatrix_to_xform2d_apply(self):
        q = th.quat_from_axis_angle([0, 0, 1], math.pi/4)
        R = th.quat_to_rotmatrix(q)
        xf = th.rotmatrix_to_xform2d(R, focal_length=100.0)
        # apply to focal-plane point (10, 0) mm
        xout, yout = xf.apply(10.0, 0.0)
        # Compare against explicit multiplication by R (first two rows)
        v = R[:2, :2] @ np.array([10.0, 0.0]) + R[:2, 2] * 100.0
        self.assertAlmostEqual(xout, v[0], places=12)
        self.assertAlmostEqual(yout, v[1], places=12)


if __name__ == '__main__':
    unittest.main()
