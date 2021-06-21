#!/usr/bin/env python3

#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

'''
Test classes to run deus for performance reasons.
'''
import os
import datetime
import subprocess
import unittest


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
        merged_output_filename = os.path.join(
            output_dir, 'merged_ts_perf.json'
        )

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

        time_ok_seconds = 60

        self.assertLess(total_seconds, time_ok_seconds)


if __name__ == '__main__':
    unittest.main()
