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
Test classes to run deus for performance reasons.
"""
import os
import datetime
import subprocess
import unittest


class TestPerformance(unittest.TestCase):
    """
    Test class to run deus as a command line tool.
    """

    def test_deus_with_ts_shakemap_for_performance(self):
        """
        Runs deus with a tsunami shakemap.
        The important point here is how long it takes.
        (And maybe we need to speed things up).
        """
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs", "performance")
        test_shakemap = os.path.join(testinput_dir, "shakemap_ts.xml")
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_so_far.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_suppasri.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_ts_perf.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(merged_output_filename):
            os.unlink(merged_output_filename)

        start = datetime.datetime.now()

        subprocess.run(
            [
                "python3",
                "deus.py",
                "--merged_output_file",
                merged_output_filename,
                test_shakemap,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        end = datetime.datetime.now()

        delta = end - start

        total_seconds = delta.total_seconds()

        time_ok_seconds = 60

        self.assertLess(total_seconds, time_ok_seconds)


if __name__ == "__main__":
    unittest.main()
