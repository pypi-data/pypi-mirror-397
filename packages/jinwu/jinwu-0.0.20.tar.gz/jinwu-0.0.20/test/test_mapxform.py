import unittest
import numpy as np
from jinwu.core.teldef_helpers import MapXform, XFORM2D


class TestMapXform(unittest.TestCase):
    def test_apply_translation(self):
        # create 5x5 map with a single non-zero at center (i=2,j=2)
        dx = np.zeros((5,5), dtype=float)
        dy = np.zeros((5,5), dtype=float)
        dx[2,2] = 1.0
        dy[2,2] = -0.5
        origin_x = 0.0
        origin_y = 0.0
        scale_x = 1.0
        scale_y = 1.0
        m = MapXform(dx, dy, origin_x, scale_x, origin_y, scale_y)

        # translation by +1 in x (detector coords)
        xf = XFORM2D(matrix=np.eye(2), offset=np.array([1.0, 0.0]))
        m2 = m.apply_xform2d(xf)

        # new origin should be translated
        self.assertAlmostEqual(m2.origin_x, 1.0)
        self.assertAlmostEqual(m2.origin_y, 0.0)

        # the original center at (2,2) maps to detector coord (3,2) after translation
        sampled = m2.sample_delta_at_pixel(3.0, 2.0)
        self.assertAlmostEqual(sampled[0], 1.0)
        self.assertAlmostEqual(sampled[1], -0.5)


if __name__ == '__main__':
    unittest.main()
