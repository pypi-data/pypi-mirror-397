"""Integration tests between Teldef and teldef_helpers XFORM."""
import unittest
import numpy as np
from jinwu.core.teldef import Teldef


class TestTeldefXform(unittest.TestCase):
    def test_focal_to_pixel_equivalence(self):
        # create a simple teldef-like object
        t = Teldef()
        # build a small rotation: 5 degrees about Z
        theta = np.radians(5.0)
        c = np.cos(theta)
        s = np.sin(theta)
        align = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        t.align = align
        t.focal_length = 1000.0
        t.det_xscl = 0.05
        t.det_yscl = 0.05
        t.optaxis = (512.0, 512.0)

        # build xform
        t.build_focal_to_pixel_xform()
        xf = t.focal_to_pixel_xform

        # choose a test sky point by synthesizing focal mm coords
        x_mm = 1.23
        y_mm = -4.56
        # manual compute following sky_to_det_with_pointing's internal math
        inv_align = t.align.T
        vec_det = inv_align @ np.array([x_mm, y_mm, t.focal_length])
        x_pix_manual = vec_det[0] / t.det_xscl + t.optaxis[0]
        y_pix_manual = vec_det[1] / t.det_yscl + t.optaxis[1]

        x_pix_xf, y_pix_xf = xf.apply(x_mm, y_mm)

        self.assertAlmostEqual(x_pix_manual, x_pix_xf, places=12)
        self.assertAlmostEqual(y_pix_manual, y_pix_xf, places=12)

    def test_det2sky_with_mapxform(self):
        from jinwu.core.teldef_helpers import MapXform
        t = Teldef()
        theta = np.radians(2.0)
        c = np.cos(theta); s = np.sin(theta)
        t.align = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        t.focal_length = 1000.0
        t.det_xscl = 0.05
        t.det_yscl = 0.05
        t.optaxis = (512.0, 512.0)

        # create a small 3x3 map with non-zero deltas centered around optaxis
        deltax = np.zeros((3,3), float)
        deltay = np.zeros((3,3), float)
        deltax[1,1] = 1.0  # shift center by +1 pixel
        deltay[1,1] = -2.0 # shift center by -2 pixels
        origin_x = 511.0
        origin_y = 511.0
        scale_x = 1.0
        scale_y = 1.0
        mapx = MapXform(deltax, deltay, origin_x, scale_x, origin_y, scale_y)
        t.raw_map = mapx

        # build det2sky using a pointing
        t._build_and_cache_det2sky(180.0, 45.0)
        # pick pixel at center (512,512) -> map delta should be (1,-2)
        ra_nl, dec_nl = t.det2sky.apply(512.0, 512.0)
        # compute without nonlinear by removing raw_map temporarily
        rawmap_saved = t.raw_map
        t.raw_map = None
        t._build_and_cache_det2sky(180.0, 45.0)
        ra_nom, dec_nom = t.det2sky.apply(512.0, 512.0)
        t.raw_map = rawmap_saved
        # the transformed coordinates should differ because of applied pixel shifts
        self.assertNotAlmostEqual(ra_nl, ra_nom)
        self.assertNotAlmostEqual(dec_nl, dec_nom)

    def test_convert_detector_to_sky_and_repeat(self):
        t = Teldef()
        theta = np.radians(3.0)
        c = np.cos(theta); s = np.sin(theta)
        t.align = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        t.focal_length = 1500.0
        t.det_xscl = 0.03
        t.det_yscl = 0.03
        t.optaxis = (200.0, 300.0)

        # test values
        x_pix = 210.5
        y_pix = 295.25
        ra_pnt = 180.0
        dec_pnt = 45.0

        ra1, dec1 = t.convert_detector_to_sky(x_pix, y_pix, ra_pnt=ra_pnt, dec_pnt=dec_pnt)
        # repeating should give same result
        ra2, dec2 = t.repeat_detector_to_sky(x_pix, y_pix)
        self.assertAlmostEqual(ra1, ra2, places=12)
        self.assertAlmostEqual(dec1, dec2, places=12)

    def test_compute_det2sky_from_quaternion(self):
        t = Teldef()
        theta = np.radians(4.0)
        c = np.cos(theta); s = np.sin(theta)
        t.align = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        t.focal_length = 1200.0
        t.det_xscl = 0.02
        t.det_yscl = 0.02
        t.optaxis = (256.0, 256.0)

        # build quaternion pointing (use helper)
        from jinwu.core import teldef_helpers as th
        q = th.radecroll_to_quat(180.0, 30.0, 0.0)

        # build det2sky via quaternion helper
        t.compute_det2sky_from_quaternion(q)
        # test a pixel
        x_pix = 260.0
        y_pix = 250.0
        ra_a, dec_a = t.det2sky_func(x_pix, y_pix)
        # also exercise det2sky object if present
        if hasattr(t, 'det2sky'):
            ra_o, dec_o = t.det2sky.apply(x_pix, y_pix)
            self.assertAlmostEqual(ra_a, ra_o, places=12)
            self.assertAlmostEqual(dec_a, dec_o, places=12)

        # and via convert_detector_to_sky with q path
        ra_b, dec_b = t.convert_detector_to_sky(x_pix, y_pix, q=q)

        self.assertAlmostEqual(ra_a, ra_b, places=12)
        self.assertAlmostEqual(dec_a, dec_b, places=12)


if __name__ == '__main__':
    unittest.main()


import gdt.core.coords