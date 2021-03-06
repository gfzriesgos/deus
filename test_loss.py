#!/usr/bin/env python3

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
