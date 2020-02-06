#!/usr/bin/env python3

'''
Testclasses for the loss.
'''

import os
import glob
import unittest

import pandas as pd
from shapely import wkt

import exposure
import loss
import transition

from testimplementations import AlwaysOneDollarPerTransitionLossProvider


class TestLoss(unittest.TestCase):
    '''
    Test class for the loss.
    '''

    def test_exposure_to_loss_cell(self):
        '''
        Tests to create a loss cell
        by using the exposure cell and
        some transitions.
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = exposure.ExposureCell.from_simple_series(
            schema=schema,
            series=series1
        )
        transition_cell1 = transition.TransitionCell.from_exposure_cell(
            exposure_cell1
        )

        transition_to_add = transition.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=1,
            n_buildings=10,
        )

        transition_cell1.add_transition(transition_to_add)
        loss_cell1 = loss.LossCell.from_transition_cell(
            transition_cell=transition_cell1,
            loss_provider=AlwaysOneDollarPerTransitionLossProvider()
        )

        self.assertEqual('$', loss_cell1.loss_unit)
        self.assertEqual(10, loss_cell1.loss_value)
        self.assertEqual('CHL.14.1.1_1', loss_cell1.gid)
        self.assertEqual(geometry1, loss_cell1.geometry)

        loss_list = loss.LossCellList([loss_cell1])

        loss_dataframe = loss_list.to_dataframe()

        self.assertEqual(geometry1, loss_dataframe['geometry'][0])
        self.assertEqual(10, loss_dataframe['loss_value'][0])
        self.assertEqual('$', loss_dataframe['loss_unit'][0])

    def test_read_loss_from_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        loss_data_dir = os.path.join(current_dir, 'loss_data')
        files = glob.glob(os.path.join(loss_data_dir, '*.json'))

        loss_provider = loss.LossProvider.from_files(files, '$')

        loss_value = loss_provider.get_loss(
            schema='SUPPASRI2013_v2.0',
            taxonomy='MIX',
            from_damage_state=0,
            to_damage_state=3
        )

        self.assertLess(0.0, loss_value)

    def test_loss_computation(self):
        '''
        Test for the loss computation.
        :return: None
        '''
        loss_data = {
            'SUPPASRI2013_v2.0': {
                'data': [
                    {
                        'taxonomy': 'URM',
                        'loss_matrix': {
                            '0': {
                                '1': 500,
                                '2': 600,
                                '3': 700,
                                '4': 800,
                            }
                        }
                    }
                ]
            }
        }

        loss_provider = loss.LossProvider(loss_data)

        loss_value = loss_provider.get_loss(
            schema='SUPPASRI2013_v2.0',
            taxonomy='URM',
            from_damage_state=0,
            to_damage_state=3
        )

        self.assertEqual(700, loss_value)


if __name__ == '__main__':
    unittest.main()
