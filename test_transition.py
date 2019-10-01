#!/usr/bin/env python3

'''
Test classes for the transitions.
'''

import unittest

import pandas as pd
from shapely import wkt

import exposure
import transition


class TestTransition(unittest.TestCase):
    '''
    Test class for the transition.
    '''
    def test_exposure_to_transition_cell(self):
        '''
        Test to create a transition cell
        using the exposure cell.
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
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

        self.assertEqual(0, len(transition_cell1.get_transitions()))

        transition_to_add = transition.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=1,
            n_buildings=10,
        )
        transition_cell1.add_transition(transition_to_add)

        self.assertEqual(1, len(transition_cell1.get_transitions()))
        first_transition = transition_cell1.get_transitions()[0]

        self.assertEqual(schema, first_transition.get_schema())
        self.assertEqual('W+WS/H:1,2', first_transition.get_taxonomy())
        self.assertEqual(0, first_transition.get_from_damage_state())
        self.assertEqual(1, first_transition.get_to_damage_state())
        self.assertEqual(10, first_transition.get_n_buildings())

        transition_cell1.add_transition(transition_to_add)

        self.assertEqual(1, len(transition_cell1.get_transitions()))
        first_transition = transition_cell1.get_transitions()[0]
        self.assertEqual(20, first_transition.get_n_buildings())

        self.assertEqual('Colina', transition_cell1.get_name())
        self.assertEqual('CHL.14.1.1_1', transition_cell1.get_gid())
        self.assertEqual(geometry1, transition_cell1.get_geometry())

        transition_to_add2 = transition.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=2,
            n_buildings=10,
        )
        transition_cell1.add_transition(transition_to_add2)

        transition_list = transition.TransitionCellList([transition_cell1])
        transition_dataframe = transition_list.to_dataframe()

        self.assertEqual('Colina', transition_dataframe['name'][0])
        self.assertEqual('CHL.14.1.1_1', transition_dataframe['gid'][0])
        self.assertEqual(geometry1, transition_dataframe['geometry'][0])
        self.assertEqual(schema, transition_dataframe['schema'][0])

        transition_element = pd.DataFrame(
            transition_dataframe['transitions'][0])

        self.assertTrue('taxonomy' in transition_element.columns)
        self.assertTrue('from_damage_state' in transition_element.columns)
        self.assertTrue('to_damage_state' in transition_element.columns)
        self.assertTrue('n_buildings' in transition_element.columns)

        self.assertEqual(2, len(transition_element['taxonomy']))
        self.assertTrue(all(transition_element['taxonomy'] == 'W+WS/H:1,2'))
        self.assertTrue(all(transition_element['from_damage_state'] == 0))
        self.assertTrue(any(transition_element['to_damage_state'] == 1))
        self.assertTrue(any(transition_element['to_damage_state'] == 2))


if __name__ == '__main__':
    unittest.main()
