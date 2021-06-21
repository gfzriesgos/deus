#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

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
            'fixedDEM_S_VEI_60mio_HYDRO_v10_EROSION_1600_0015_25res' +
            '_4mom_25000s_MaxPressure_smaller.asc'
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
            PointsWithValue(x=778845.3436538, y=9918842.5687882, value=0),
            PointsWithValue(x=773449.1072520, y=9917890.4097193, value=0),
        ]

        intensity_provider = (
            rasterintensityprovider.RasterIntensityProvider.from_file(
                raster_file, intensity, unit, na_value
            )
        )

        for check in checks:
            intensities, units = intensity_provider.get_nearest(
                lon=check.x,
                lat=check.y
            )

            self.assertLess(check.value - eps, intensities[intensity])
            self.assertLess(intensities[intensity], check.value + eps)
            self.assertEqual(unit, units[intensity])


if __name__ == '__main__':
    unittest.main()
