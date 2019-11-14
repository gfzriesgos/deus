#!/usr/bin/env python3

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
            current_dir,
            'testinputs',
            'ashfall_shapefile',
            'E1_AF_kPa_VEI4.shp'
        )
        column = 'FEB2008'

        intensity_provider = ashfall.Ashfall.from_file(
            input_file_name, column
        ).to_intensity_provider()

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
