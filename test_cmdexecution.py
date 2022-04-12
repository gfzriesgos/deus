#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""
Test classes to run deus as a command line tool.
"""
import os
import subprocess
import unittest

import geopandas
import pandas


class TestLowChange(unittest.TestCase):
    """Test changes that seem to be too low."""

    def test_execute_deus(self):
        """Run the test case with deus."""
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(
            testinput_dir, "shakemap_low_changes_testcase.xml"
        )
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_low_changes_testcase.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_low_changes_testcase.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_low_changes_testcase.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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


class TestDeusCmdExecution(unittest.TestCase):
    """
    Test class to run deus as a command line tool.
    """

    def test_execute_deus_with_multiple_imt_shakemap(self):
        """
        Runs deus with a shakemap with SA(1.0) and
        SA(0.3) values.
        """
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(
            testinput_dir, "shakemap_with_multiple_imts.xml"
        )
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_from_assetmaster.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_sara.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_multiple_imts.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema, test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema, merged_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)

        merged_output_data = geopandas.read_file(merged_output_filename)
        for _, row in merged_output_data.iterrows():
            transitions = row.transitions
            for key in [
                "n_buildings",
                "to_damage_state",
                "from_damage_state",
            ]:
                self.assertEqual(type(transitions[key]), list)
            expo = row.expo
            for key in ["Damage", "Taxonomy", "Buildings"]:
                self.assertEqual(type(expo[key]), list)

    def test_execute_deus_with_ts_shakemap(self):
        """
        Runs deus with a tsunami shakemap.
        """
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(testinput_dir, "shakemap_tsunami.xml")
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_from_assetmaster.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_suppasri.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(output_dir, "merged_ts.json")

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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

        # We want to check that we have taxonomies in the resulting exposure
        exposure_data = geopandas.read_file(merged_output_filename)
        has_taxonomies = False
        for _, row in exposure_data.iterrows():
            expo = pandas.DataFrame(row.expo)
            if "Taxonomy" in expo.columns and len(expo.Taxonomy) > 0:
                has_taxonomies = True
                break
        self.assertTrue(has_taxonomies)

    def test_execute_deus_two_times(self):
        """
        Runs deus two times (update the updated exposure model).
        """
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(testinput_dir, "shakemap.xml")
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_from_assetmaster.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_sara.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(output_dir, "merged.json")
        merged_output_filename2 = os.path.join(output_dir, "merged2.json")

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
            merged_output_filename2,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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
        subprocess.run(
            [
                "python3",
                "deus.py",
                "--merged_output_file",
                merged_output_filename2,
                test_shakemap,
                merged_output_filename,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

    def test_execute_deus_in_peru_for_schema_mapping_to_suppasri(
        self,
    ):
        """
        This is a test case for the schema mapping of the
        schema mapping for tsunamis with the peru
        exposure model.
        The interesting thing here is the taxonomy
        W-WWD-H1-2, that must be supported.
        For intensity measurements this case is
        useless, because the example tsunami shakemap
        just covers a event near Valparaiso.
        """
        schema = "SARA_v1.0"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(testinput_dir, "shakemap_tsunami.xml")
        test_exposure_file = os.path.join(testinput_dir, "exposure_peru.json")
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_suppasri.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_peru_suppasri.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema, test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema, merged_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestDeusCmdExecutionInEcuador(unittest.TestCase):
    """
    Test class to run deus in ecuador from cmd.
    """

    def test_execute_deus_in_ecuador_for_lahar(self):
        schema = "Mavrouli_et_al_2014"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_shakemap = os.path.join(testinput_dir, "shakemap_lahar.xml")
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_model_lahar.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_marvrouli.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(output_dir, "merged_lahar.json")

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

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

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema, test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema, merged_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestVolcanoCmdExecution(unittest.TestCase):
    """
    Test class to run volcanus as a command line tool.
    """

    def test_execute_volcano_for_ecuador(self):
        """
        This is the testcase for running the computation
        for the ashfall data.
        """
        schema = "Torres_Corredor_et_al_2017"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_intensity = os.path.join(
            testinput_dir, "ashfall_shapefile", "E1_AF_kPa_VEI4.shp"
        )
        test_intensity_column = "FEB2008"
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_model_ashfall.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_torres.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_ecuador_torres.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                "python3",
                "volcanus.py",
                "--merged_output_file",
                merged_output_filename,
                test_intensity,
                test_intensity_column,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema, test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema, merged_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestVolcanusAndThenDeus(unittest.TestCase):
    """
    Test case for running the lahar deus after
    the ashfall volcanus.
    """

    def test_execute_deus_two_times(self):
        """
        Runs deus two times (update the updated exposure model).
        """
        schema = "Torres_Corredor_et_al_2017"

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, "testinputs")
        test_intensity = os.path.join(
            testinput_dir, "ashfall_shapefile", "E1_AF_kPa_VEI4.shp"
        )
        test_intensity_column = "FEB2008"
        test_shakemap = os.path.join(testinput_dir, "shakemap_lahar.xml")
        test_exposure_file = os.path.join(
            testinput_dir, "exposure_model_ashfall.json"
        )
        test_fragility_file = os.path.join(
            testinput_dir, "fragility_torres.json"
        )

        test_fragility_file2 = os.path.join(
            testinput_dir, "fragility_marvrouli.json"
        )

        output_dir = os.path.join(current_dir, "testoutputs")

        merged_output_filename = os.path.join(
            output_dir, "merged_ecuador_torres_1.json"
        )
        merged_output_filename2 = os.path.join(
            output_dir, "merged_lahar_after_ash.json"
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            merged_output_filename,
            merged_output_filename2,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                "python3",
                "volcanus.py",
                "--merged_output_file",
                merged_output_filename,
                test_intensity,
                test_intensity_column,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema, test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema, merged_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)

        subprocess.run(
            [
                "python3",
                "deus.py",
                "--merged_output_file",
                merged_output_filename2,
                test_shakemap,
                merged_output_filename,
                schema,
                test_fragility_file2,
            ],
            check=True,
        )


def get_n_buildings_by_cell_gid(schema, exposure_file):
    """
    For testing that the number of building stays the
    same.
    """
    exposure_data = geopandas.read_file(exposure_file)

    buildings_by_cell_gid = {}
    for _, series in exposure_data.iterrows():
        expo = pandas.DataFrame(series.expo)
        gid = series["gid"]
        buildings = sum(expo["Buildings"])

    return buildings_by_cell_gid


if __name__ == "__main__":
    unittest.main()
