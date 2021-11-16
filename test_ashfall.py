#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

import os
import unittest

import ashfall


class TestAshfall(unittest.TestCase):
    """
    The testcase for the ashfall.
    """

    def test_ashfall_example_file(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_file_name = os.path.join(
            current_dir, "testinputs", "ashfall_shapefile", "E1_AF_kPa_VEI4.shp"
        )
        column = "FEB2008"

        intensity_provider = ashfall.Ashfall.from_file(
            input_file_name, column
        ).to_intensity_provider()

        intensities, units = intensity_provider.get_nearest(
            lon=-78.398558176, lat=-0.649429492
        )

        self.assertIn("LOAD", intensities.keys())
        self.assertIn("LOAD", units.keys())

        self.assertEqual(units["LOAD"], "kPa")

        self.assertLess(0.0062, intensities["LOAD"])
        self.assertLess(intensities["LOAD"], 0.0063)

        intensities2, units2 = intensity_provider.get_nearest(
            lon=-79.073127, lat=-0.747129
        )

        self.assertEqual(units, units2)

        self.assertLess(0.0049, intensities2["LOAD"])
        self.assertLess(intensities2["LOAD"], 0.0051)


if __name__ == "__main__":
    unittest.main()
