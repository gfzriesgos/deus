#!/usr/bin/env python3

'''
Test classes to run deus as a command line tool.
'''
import os
import subprocess
import unittest

import exposure


class TestDeusCmdExecution(unittest.TestCase):
    '''
    Test class to run deus as a command line tool.
    '''

    def test_execute_deus_with_multiple_imt_shakemap(self):
        '''
        Runs deus with a shakemap with SA(1.0) and
        SA(0.3) values.
        '''
        schema = 'SARA_v1.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(
            testinput_dir,
            'shakemap_with_multiple_imts.xml'
        )
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_from_assetmaster.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_sara.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_multiple_imts.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_multiple_imts.json'
        )
        loss_output_filename = os.path.join(
            output_dir,
            'losses_multiple_imts.json'
        )
        merged_output_filename = os.path.join(
            output_dir,
            'merged_multiple_imts.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
                merged_output_filename,
                test_shakemap,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            updated_exposure_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)

    def test_execute_deus_with_ts_shakemap(self):
        '''
        Runs deus with a tsunami shakemap.
        '''
        schema = 'SARA_v1.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(testinput_dir, 'shakemap_tsunami.xml')
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_from_assetmaster.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_suppasri.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_ts.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_ts.json'
        )
        loss_output_filename = os.path.join(output_dir, 'losses_ts.json')
        merged_output_filename = os.path.join(output_dir, 'merged_ts.json')

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
                merged_output_filename,
                test_shakemap,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        exposure_data = exposure.ExposureCellList.from_file(
            'SUPPASRI2013_v2.0',
            updated_exposure_output_filename
        )
        for exposure_cell in exposure_data.exposure_cells:
            self.assertTrue(exposure_cell.taxonomies)

    def test_execute_deus_two_times(self):
        '''
        Runs deus two times (update the updated exposure model).
        '''
        schema = 'SARA_v1.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(testinput_dir, 'shakemap.xml')
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_from_assetmaster.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_sara.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions.json'
        )
        loss_output_filename = os.path.join(output_dir, 'losses.json')
        merged_output_filename = os.path.join(output_dir, 'merged.json')

        updated_exposure_output_filename2 = os.path.join(
            output_dir,
            'updated_exposure2.json'
        )
        transition_output_filename2 = os.path.join(
            output_dir,
            'transitions2.json'
        )
        loss_output_filename2 = os.path.join(
            output_dir,
            'losses2.json'
        )
        merged_output_filename2 = os.path.join(
            output_dir,
            'merged2.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
            updated_exposure_output_filename2,
            transition_output_filename2,
            loss_output_filename2,
            merged_output_filename2,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
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
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename2,
                '--transition_output_file',
                transition_output_filename2,
                '--loss_output_file',
                loss_output_filename2,
                '--merged_output_file',
                merged_output_filename2,
                test_shakemap,
                updated_exposure_output_filename,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

    def test_execute_deus_in_peru_for_schema_mapping_to_suppasri(self):
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
        schema = 'SARA_v1.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(
            testinput_dir,
            'shakemap_tsunami.xml'
        )
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_peru.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_suppasri.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_peru_suppasri.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_peru_suppasri.json'
        )
        loss_output_filename = os.path.join(
            output_dir,
            'losses_peru_suppasri.json'
        )
        merged_output_filename = os.path.join(
            output_dir,
            'merged_peru_suppasri.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
                merged_output_filename,
                test_shakemap,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            updated_exposure_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestDeusCmdExecutionInEcuador(unittest.TestCase):
    """
    Test class to run deus in ecuador from cmd.
    """

    def test_execute_deus_in_ecuador_for_lahar(self):
        schema = 'Mavrouli_et_al_2014'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(
            testinput_dir,
            'shakemap_lahar.xml'
        )
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_model_lahar.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_marvrouli.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_lahar.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_lahar.json'
        )
        loss_output_filename = os.path.join(
            output_dir,
            'losses_lahar.json'
        )
        merged_output_filename = os.path.join(
            output_dir,
            'merged_lahar.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
                merged_output_filename,
                test_shakemap,
                test_exposure_file,
                schema,
                test_fragility_file,
            ],
            check=True,
        )

        input_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            updated_exposure_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestVolcanoCmdExecution(unittest.TestCase):
    '''
    Test class to run volcanus as a command line tool.
    '''

    def test_execute_volcano_for_ecuador(self):
        """
        This is the testcase for running the computation
        for the ashfall data.
        """
        schema = 'Torres_Corredor_et_al_2017'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_intensity = os.path.join(
            testinput_dir,
            'ashfall_shapefile',
            'E1_AF_kPa_VEI4.shp'
        )
        test_intensity_column = 'FEB2008'
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_model_ashfall.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_torres.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_ecuador_torres.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_ecuador_torres.json'
        )
        loss_output_filename = os.path.join(
            output_dir,
            'losses_ecuador_torres.json'
        )
        merged_output_filename = os.path.join(
            output_dir,
            'merged_ecuador_torres.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            transition_output_filename,
            loss_output_filename,
            merged_output_filename,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'volcanus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
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
            schema,
            test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            updated_exposure_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)


class TestVolcanusAndThenDeus(unittest.TestCase):
    """
    Test case for running the lahar deus after
    the ashfall volcanus.
    """

    def test_execute_deus_two_times(self):
        '''
        Runs deus two times (update the updated exposure model).
        '''
        schema = 'Torres_Corredor_et_al_2017'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_intensity = os.path.join(
            testinput_dir,
            'ashfall_shapefile',
            'E1_AF_kPa_VEI4.shp'
        )
        test_intensity_column = 'FEB2008'
        test_shakemap = os.path.join(
            testinput_dir,
            'shakemap_lahar.xml'
        )
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_model_ashfall.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_torres.json'
        )

        test_fragility_file2 = os.path.join(
            testinput_dir,
            'fragility_marvrouli.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_ecuador_torres_1.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_ecuador_torres_1.json'
        )
        loss_output_filename = os.path.join(
            output_dir,
            'losses_ecuador_torres_1.json'
        )
        merged_output_filename = os.path.join(
            output_dir,
            'merged_ecuador_torres_1.json'
        )
        updated_exposure_output_filename2 = os.path.join(
            output_dir,
            'updated_exposure_lahar_after_ash.json'
        )
        transition_output_filename2 = os.path.join(
            output_dir,
            'transitions_lahar_after_ash.json'
        )
        loss_output_filename2 = os.path.join(
            output_dir,
            'losses_lahar_after_ash.json'
        )
        merged_output_filename2 = os.path.join(
            output_dir,
            'merged_lahar_after_ash.json'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for output_filename in [
            updated_exposure_output_filename,
            updated_exposure_output_filename2,
            transition_output_filename,
            transition_output_filename2,
            loss_output_filename,
            loss_output_filename2,
            merged_output_filename,
            merged_output_filename2,
        ]:
            if os.path.exists(output_filename):
                os.unlink(output_filename)

        subprocess.run(
            [
                'python3',
                'volcanus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename,
                '--transition_output_file',
                transition_output_filename,
                '--loss_output_file',
                loss_output_filename,
                '--merged_output_file',
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
            schema,
            test_exposure_file
        )
        output_n_buildings = get_n_buildings_by_cell_gid(
            schema,
            updated_exposure_output_filename
        )

        self.assertEqual(input_n_buildings, output_n_buildings)

        subprocess.run(
            [
                'python3',
                'deus.py',
                '--updated_exposure_output_file',
                updated_exposure_output_filename2,
                '--transition_output_file',
                transition_output_filename2,
                '--loss_output_file',
                loss_output_filename2,
                '--merged_output_file',
                merged_output_filename2,
                test_shakemap,
                updated_exposure_output_filename,
                schema,
                test_fragility_file2,
            ],
            check=True,
        )


def get_n_buildings_by_cell_gid(schema, exposure_file):
    '''
    For testing that the number of building stays the
    same.
    '''
    exposure_data = exposure.ExposureCellList.from_file(
        schema,
        exposure_file,
    ).to_dataframe()

    buildings_by_cell_gid = {}
    for _, series in exposure_data.iterrows():
        gid = series['gid']
        buildings = sum(series['expo']['Buildings'])

    return buildings_by_cell_gid


if __name__ == '__main__':
    unittest.main()
