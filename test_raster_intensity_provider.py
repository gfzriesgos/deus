#!/usr/bin/env python3

"""
Testfile for testing
the intensity provider for rasters.
"""

import collections
import os
import unittest

import rasterintensityprovider


class TestRasterIntensityProvider(unittest.TestCase):
    """
    Test case for accessing the raster via intensity
    provider.
    """

    def test_raster_intensity_provider(self):
        """
        Takes the raster from the testinputs folder.
        Wrapps it into an intensity provider interface.
        Checks the values.
        """
        raster_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'testinputs',
            'fixedDEM_S_VEI_60mio_HYDRO_v10_EROSION_1600_0015_25res_4mom_25000s_MaxPressure_smaller.asc'
        )

        intensity = 'pressure'
        unit = 'p'
        na_value = 0.0
        PointsWithValue = collections.namedtuple(
            'PointsWithValue',
            'x y value'
        )

        eps = 0.1

        checks = [
            PointsWithValue(x=781687.171, y=9924309.372, value=4344.54),
            PointsWithValue(x=778845.3436538,y=9918842.5687882, value=0),
            PointsWithValue(x=773449.1072520,y=9917890.4097193, value=0),
        ]

        intensity_provider = rasterintensityprovider.RasterIntensityProvider.from_file(
            raster_file, intensity, unit, na_value
        )

        for check in checks:
            intensities, units = intensity_provider.get_nearest(lon=check.x, lat=check.y)

            self.assertLess(check.value - eps, intensities[intensity])
            self.assertLess(intensities[intensity], check.value + eps)
            self.assertEqual(unit, units[intensity])


if __name__ == '__main__':
    unittest.main()
