#!/usr/bin/env python3

# Copyright © 2021-2022 Helmholtz Centre Potsdam GFZ German Research Centre for
# Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Testclasses for the loss.
"""

import os
import glob
import unittest

import loss


class TestLoss(unittest.TestCase):
    """
    Test class for the loss.
    """

    def test_read_loss_from_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        loss_data_dir = os.path.join(current_dir, "loss_data")
        files = glob.glob(os.path.join(loss_data_dir, "*.json"))

        loss_provider = loss.LossProvider.from_files(files, "$")

        replacement_cost = loss_provider.get_fallback_replacement_cost(
            schema="SUPPASRI2013_v2.0", taxonomy="MIX"
        )

        self.assertLess(11999.0, replacement_cost)
        self.assertLess(replacement_cost, 12001.0)

        loss_value = loss_provider.get_loss(
            schema="SUPPASRI2013_v2.0",
            taxonomy="MIX",
            from_damage_state=0,
            to_damage_state=3,
            replacement_cost=replacement_cost,
        )

        self.assertLess(0.0, loss_value)

    def test_loss_computation(self):
        """
        Test for the loss computation.
        :return: None
        """
        loss_data = {
            "SUPPASRI2013_v2.0": {
                "data": {
                    "steps": {
                        "1": 500 / 800,
                        "2": 600 / 800,
                        "3": 700 / 800,
                        "4": 1,
                    },
                    "replacementCosts": {
                        "URM": 800,
                    },
                }
            }
        }

        loss_provider = loss.LossProvider(loss_data)
        replacement_cost = loss_provider.get_fallback_replacement_cost(
            schema="SUPPASRI2013_v2.0",
            taxonomy="URM",
        )

        self.assertLess(799, replacement_cost)
        self.assertLess(replacement_cost, 801)

        loss_value = loss_provider.get_loss(
            schema="SUPPASRI2013_v2.0",
            taxonomy="URM",
            from_damage_state=0,
            to_damage_state=3,
            replacement_cost=replacement_cost,
        )

        self.assertEqual(700, loss_value)

    def test_combine_losses(self):
        """Test the combine_losses function."""
        test_cases = [
            ((0, "usd", 0, "usd"), (0, "usd")),
            ((130, "usd", 25, "usd"), (155, "usd")),
            ((100.1, "usd", 24.2, "usd"), (124.3, "usd")),
            ((130, "usd", 0, None), (130, "usd")),
        ]
        for test_case in test_cases:
            inputs, expected_outputs = test_case

            outputs = loss.combine_losses(*inputs)
            self.assertEqual(outputs, expected_outputs)

    def test_combine_losses_with_non_compatible_units(self):
        """Test what happens if we use non compatible units."""
        with self.assertRaises(Exception):
            loss.combine_losses(0, "unit 1", 0, "unit 2")


if __name__ == "__main__":
    unittest.main()
