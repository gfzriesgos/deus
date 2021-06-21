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
Testclasses for the loss.
'''

import os
import glob
import unittest

import loss


class TestLoss(unittest.TestCase):
    '''
    Test class for the loss.
    '''

    def test_read_loss_from_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        loss_data_dir = os.path.join(current_dir, 'loss_data')
        files = glob.glob(os.path.join(loss_data_dir, '*.json'))

        loss_provider = loss.LossProvider.from_files(files, '$')

        replacement_cost = loss_provider.get_fallback_replacement_cost(
            schema='SUPPASRI2013_v2.0',
            taxonomy='MIX'
        )

        self.assertLess(11999.0, replacement_cost)
        self.assertLess(replacement_cost, 12001.0)

        loss_value = loss_provider.get_loss(
            schema='SUPPASRI2013_v2.0',
            taxonomy='MIX',
            from_damage_state=0,
            to_damage_state=3,
            replacement_cost=replacement_cost
        )

        self.assertLess(0.0, loss_value)

    def test_loss_computation(self):
        '''
        Test for the loss computation.
        :return: None
        '''
        loss_data = {
            'SUPPASRI2013_v2.0': {
                'data': {
                    'steps': {
                        '1': 500 / 800,
                        '2': 600 / 800,
                        '3': 700 / 800,
                        '4': 1,
                    },
                    'replacementCosts': {
                        'URM': 800,
                    }
                }
            }
        }

        loss_provider = loss.LossProvider(loss_data)
        replacement_cost = loss_provider.get_fallback_replacement_cost(
            schema='SUPPASRI2013_v2.0',
            taxonomy='URM',
        )

        self.assertLess(799, replacement_cost)
        self.assertLess(replacement_cost, 801)

        loss_value = loss_provider.get_loss(
            schema='SUPPASRI2013_v2.0',
            taxonomy='URM',
            from_damage_state=0,
            to_damage_state=3,
            replacement_cost=replacement_cost
        )

        self.assertEqual(700, loss_value)


if __name__ == '__main__':
    unittest.main()
