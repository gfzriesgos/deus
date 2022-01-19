#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

import unittest

import shakemap


class TestReadShakemapGridData(unittest.TestCase):
    """
    This is the test class for reading
    the content from the grid_data text.
    """

    def test_one_row_ints(self):
        """
        Test with one row of integers.
        """
        raw_data = "15 16 17"

        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual([15, 16, 17], result)

    def test_two_rows_ints(self):
        """
        Test with two rows of integers.
        Here we use a real newline.
        """
        raw_data = "15 16 17\n18 19 20"

        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual([15, 16, 17, 18, 19, 20], result)

    def test_two_rows_without_newline_ints(self):
        """
        Simulates the usage of two rows (2x3 values)
        but the newline was replaced by a simple space.
        """
        raw_data = "15 16 17 18 19 20"

        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual([15, 16, 17, 18, 19, 20], result)

    def test_negative(self):
        """
        Test with some negative numbers.
        """
        raw_data = "15 -16 17 18 19 -20"

        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual([15, -16, 17, 18, 19, -20], result)

    def test_quoted(self):
        """
        Test with quoted values (double quotes).
        """
        raw_data = (
            '"0 1" 1 -71.4786 -33.0123 4 0 0.0 0.0 '
            + '"0 2" 2 -71.5396 -33.0543 48 0 0.0 0.0'
        )
        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual(
            [
                "0 1",
                1,
                -71.4786,
                -33.0123,
                4,
                0,
                0.0,
                0.0,
                "0 2",
                2,
                -71.5396,
                -33.0543,
                48,
                0,
                0.0,
                0.0,
            ],
            result,
        )

    def test_quoted_single(self):
        """
        Test with quoted values (single quotes).
        """
        raw_data = (
            "'0 1' 1 -71.4786 -33.0123 4 0 0.0 0.0 "
            + "'0 2' 2 -71.5396 -33.0543 48 0 0.0 0.0"
        )
        result = list(shakemap.read_shakemap_data_from_str(raw_data))

        self.assertEqual(
            [
                "0 1",
                1,
                -71.4786,
                -33.0123,
                4,
                0,
                0.0,
                0.0,
                "0 2",
                2,
                -71.5396,
                -33.0543,
                48,
                0,
                0.0,
                0.0,
            ],
            result,
        )


class TestShakemap(unittest.TestCase):
    def test_read_ts_shakemap(self):
        shake_map_ts = shakemap.Shakemaps.from_file(
            "./testinputs/shakemap_tsunami.xml"
        )
        ts_provider = shake_map_ts.to_intensity_provider()

        ts_intensity, ts_units = ts_provider.get_nearest(
            lon=-71.547, lat=-32.9857
        )

        self.assertEqual("m", ts_units["INUN_MEAN_POLY"])

        self.assertLess(1.598, ts_intensity["INUN_MEAN_POLY"])
        self.assertLess(ts_intensity["INUN_MEAN_POLY"], 1.6)

    def test_read_shakemap(self):
        """
        Reads a normal shakemap (as it is the output of shakyground.
        :return: None
        """
        shake_map_eq = shakemap.Shakemaps.from_file(
            "./testinputs/shakemap.xml"
        )
        eq_provider = shake_map_eq.to_intensity_provider()

        self.assertIsNotNone(eq_provider)

        eq_intensity, eq_units = eq_provider.get_nearest(
            lon=-72.7, lat=-31.6416666667
        )

        self.assertEqual("g", eq_units["PGA"])

        self.assertLess(0.028835543, eq_intensity["PGA"])
        self.assertLess(eq_intensity["PGA"], 0.028835545)

    def test_lahar_shakemap(self):
        """
        Reads a lahar shakemap.
        """

        shake_map_lahar = shakemap.Shakemaps.from_file(
            "./testinputs/shakemap_lahar.xml"
        )
        lh_provider = shake_map_lahar.to_intensity_provider()

        lh_intensity, lh_units = lh_provider.get_nearest(
            lon=-78.64682219, lat=-0.864361486349
        )

        self.assertEqual("m/s", lh_units["MAXVELOCITY"])
        self.assertLess(3.28, lh_intensity["MAXVELOCITY"])
        self.assertLess(lh_intensity["MAXVELOCITY"], 3.30)


if __name__ == "__main__":
    unittest.main()
