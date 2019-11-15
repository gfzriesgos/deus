#!/usr/bin/env python3

'''
Test classes to run deus as a command line tool.
'''
import os
import subprocess
import unittest

import exposure


class TestCmdExecution(unittest.TestCase):
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

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(updated_exposure_output_filename):
            os.unlink(updated_exposure_output_filename)

        if os.path.exists(transition_output_filename):
            os.unlink(transition_output_filename)

        if os.path.exists(loss_output_filename):
            os.unlink(loss_output_filename)

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

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(updated_exposure_output_filename):
            os.unlink(updated_exposure_output_filename)

        if os.path.exists(transition_output_filename):
            os.unlink(transition_output_filename)

        if os.path.exists(loss_output_filename):
            os.unlink(loss_output_filename)

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

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(updated_exposure_output_filename):
            os.unlink(updated_exposure_output_filename)

        if os.path.exists(transition_output_filename):
            os.unlink(transition_output_filename)

        if os.path.exists(loss_output_filename):
            os.unlink(loss_output_filename)

        if os.path.exists(updated_exposure_output_filename2):
            os.unlink(updated_exposure_output_filename2)

        if os.path.exists(transition_output_filename2):
            os.unlink(transition_output_filename2)

        if os.path.exists(loss_output_filename2):
            os.unlink(loss_output_filename2)

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

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(updated_exposure_output_filename):
            os.unlink(updated_exposure_output_filename)

        if os.path.exists(transition_output_filename):
            os.unlink(transition_output_filename)

        if os.path.exists(loss_output_filename):
            os.unlink(loss_output_filename)

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
