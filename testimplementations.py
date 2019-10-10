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


class AlwaysTheSameIntensityProvider():
    def __init__(self, kind, value, unit):
        self._kind = kind
        self._value = value
        self._unit = unit

    def get_nearest(self, lon, lat):
        '''
        Returns always an intensity of
        1 at every point for PGA and the unit g.
        '''

        intensities = {self._kind: self._value}
        units = {self._kind: self._unit}

        return intensities, units
