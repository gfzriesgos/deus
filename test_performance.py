#!/usr/bin/env python3

'''
Test classes to run deus for performance reasons.
'''
import os
import datetime
import subprocess
import unittest

import exposure


class TestPerformance(unittest.TestCase):
    '''
    Test class to run deus as a command line tool.
    '''

    def test_deus_with_ts_shakemap_for_performance(self):
        '''
        Runs deus with a tsunami shakemap.
        The important point here is how long it takes.
        (And maybe we need to speed things up).
        '''
        schema = 'SARA_v1.0'

        current_dir = os.path.dirname(os.path.abspath(__file__))

        testinput_dir = os.path.join(current_dir, 'testinputs', 'performance')
        test_shakemap = os.path.join(testinput_dir, 'shakemap_ts.xml')
        test_exposure_file = os.path.join(
            testinput_dir,
            'exposure_so_far.json'
        )
        test_fragility_file = os.path.join(
            testinput_dir,
            'fragility_suppasri.json'
        )

        output_dir = os.path.join(current_dir, 'testoutputs')

        updated_exposure_output_filename = os.path.join(
            output_dir,
            'updated_exposure_ts_perf.json'
        )
        transition_output_filename = os.path.join(
            output_dir,
            'transitions_ts_perf.json'
        )
        loss_output_filename = os.path.join(output_dir, 'losses_ts_perf.json')
        merged_output_filename = os.path.join(output_dir, 'merged_ts_perf.json')

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if os.path.exists(updated_exposure_output_filename):
            os.unlink(updated_exposure_output_filename)

        if os.path.exists(transition_output_filename):
            os.unlink(transition_output_filename)

        if os.path.exists(loss_output_filename):
            os.unlink(loss_output_filename)

        if os.path.exists(merged_output_filename):
            os.unlink(merged_output_filename)

        start = datetime.datetime.now()

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

        end = datetime.datetime.now()

        delta = end - start

        total_seconds = delta.total_seconds()

        time_ok_seconds = 60 * 3

        self.assertLess(total_seconds, time_ok_seconds)


if __name__ == '__main__':
    unittest.main()
