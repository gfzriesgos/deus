#!/usr/bin/env python3

'''
This module contains
some test implementations
for the classes in the project.
'''


class AlwaysOneDollarPerTransitionLossProvider():
    '''
    A loss provider that will just return 1 $ for
    each transition.

    Useless for productive environment but easy for testing.
    '''

    def get_loss(self, schema, taxonomy, from_damage_state, to_damage_state):
        '''
        Returns the loss for each transition (one building).
        '''
        return 1

    def get_unit(self):
        '''
        Unit of the loss.
        '''
        return '$'
