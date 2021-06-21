#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)

'''
This module contains
some test implementations
for the classes in the project.
'''


class AlwaysOneDollarPerTransitionLossProvider:
    '''
    A loss provider that will just return 1 $ for
    each transition.

    Useless for productive environment but easy for testing.
    '''

    def get_fallback_replacement_cost(self, schema, taxonomy):
        """Return a dummy replacement cost."""
        return 1

    def get_loss(
            self,
            schema,
            taxonomy,
            from_damage_state,
            to_damage_state,
            replacement_cost):
        '''
        Returns the loss for each transition (one building).
        '''
        return 1

    def get_unit(self):
        '''
        Unit of the loss.
        '''
        return '$'


class AlwaysTheSameIntensityProvider:
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
