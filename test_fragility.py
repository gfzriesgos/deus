#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

import unittest

import fragility


class TestFragility(unittest.TestCase):
    def test_read_schema_from_fragility_file(self):
        """
        Reads the schema from the fragility file.
        """

        fr_file = fragility.Fragility.from_file(
            "./testinputs/fragility_sara.json"
        )
        fr_provider = fr_file.to_fragility_provider()

        schema = fr_provider.schema

        self.assertEqual("SARA_v1.0", schema)

        fr_file2 = fragility.Fragility.from_file(
            "./testinputs/fragility_suppasri.json"
        )
        fr_provider2 = fr_file2.to_fragility_provider()

        schema2 = fr_provider2.schema

        self.assertEqual("SUPPASRI2013_v2.0", schema2)


class TestLogncdfFactory(unittest.TestCase):
    """Test cases for the LogncdfFactory."""

    def test_example_sara_MUR_ADO_H1_2_D2_3(self):
        """Test with the sara MUR-ADO-H1-2 data."""
        mean = -0.644
        stddev = 0.328
        intensity_value = 0.65  # 0.65 times the gravity constant
        fun_factory = fragility.LogncdfFactory()
        fun = fun_factory(mean, stddev)
        result = fun(intensity_value)
        self.assertAlmostEqual(result, 0.74217071095185)


class TestNormCdfFactory(unittest.TestCase):
    """Test cases for the NormCdfFactory."""

    def test_example(self):
        """Test with some dummy values."""
        mean = 0.65
        stddev = 0.2
        intensity_value = 0.4
        fun_factory = fragility.NormCdfFactory()
        fun = fun_factory(mean, stddev)
        result = fun(intensity_value)
        self.assertAlmostEqual(result, 0.10564977366685535)


if __name__ == "__main__":
    unittest.main()
