import unittest
from pathlib import Path
from jinwu.core.teldef import Teldef


data_path = Path(__file__).parent / 'data' / 'swx20230701v001.teldef'


@unittest.skipUnless(data_path.exists(), "Regression teldef not present in test/data")
class TestTeldefRegression(unittest.TestCase):
    def test_basic_teldef_loading_and_conversion(self):
        tel = Teldef.from_file(data_path)
        # attempt to set sky center from CRVAL if present
        if getattr(tel, 'crval', None) is not None:
            ra, dec = tel.crval
        else:
            ra, dec = 0.0, 0.0
        # set q0 and rot0
        tel.setSkyCoordCenterInTeldef(ra, dec, 0.0)
        # try building focal->pixel xform if available
        if getattr(tel, 'align', None) is not None:
            tel.build_focal_to_pixel_xform()
        # try a sample conversion
        try:
            ra_out, dec_out = tel.convert_detector_to_sky(100.0, 100.0, ra_pnt=ra, dec_pnt=dec)
        except Exception as e:
            self.fail(f"convert_detector_to_sky raised: {e}")
        # try q-path
        q = [1.0, 0.0, 0.0, 0.0]
        try:
            tel.compute_det2sky_from_quaternion(q)
            _ = tel.repeat_detector_to_sky(100.0, 100.0)
        except Exception as e:
            self.fail(f"Quaternion det2sky path raised: {e}")


if __name__ == '__main__':
    unittest.main()
