#!/usr/bin/env python3

'''
Test classes to run deus as a command line tool.
'''
import os
import subprocess
import unittest


class TestCmdExecution(unittest.TestCase):
    '''
    Test class to run deus as a command line tool.
    '''

    def test_execute_deus_two_times(self):
        '''
        Runs deus two times (update the updated exposure model).
        '''
        schema = 'SARA.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs')
        test_shakemap = os.path.join(testinput_dir, 'shakemap.xml')
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_sara.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_sara.json'
        )
        test_loss_file = os.path.join(
            testinput_dir,
            'loss_sara.json'
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
                test_loss_file
            ],
            check=True
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
                test_loss_file
            ],
            check=True
        )


if __name__ == '__main__':
    unittest.main()
