#!/usr/bin/env python3

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
Additional testcase for the intensity data wrappers.
"""

import os
import unittest

import geopandas

import intensitydatawrapper
import intensityprovider


class TestReadFromShapefile(unittest.TestCase):
    """
    Tests reading intensities from a shapefile.
    """

    def test_read_ashfall(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_file_name = os.path.join(
            current_dir,
            'testinputs',
            'ashfall_shapefile',
            'E1_AF_kPa_VEI4.shp'
        )
        column = 'FEB2008'

        geodata = geopandas.read_file(input_file_name)

        intensity_data_wrapper = \
            intensitydatawrapper.GeopandasDataFrameWrapperWithColumnUnit(
                geodata,
                column=column,
                name='LOAD',
                unit='kPa'
            )
        intensity_provider = intensityprovider.IntensityProvider(
            intensity_data_wrapper,
        )

        intensities, units = intensity_provider.get_nearest(
            lon=-78.398558176,
            lat=-0.649429492
        )

        self.assertIn('LOAD', intensities.keys())
        self.assertIn('LOAD', units.keys())

        self.assertEqual(units['LOAD'], 'kPa')

        self.assertLess(0.0062, intensities['LOAD'])
        self.assertLess(intensities['LOAD'], 0.0063)

        intensities2, units2 = intensity_provider.get_nearest(
            lon=-79.073127,
            lat=-0.747129
        )

        self.assertEqual(units, units2)

        self.assertLess(0.0049, intensities2['LOAD'])
        self.assertLess(intensities2['LOAD'], 0.0051)


if __name__ == '__main__':
    unittest.main()
