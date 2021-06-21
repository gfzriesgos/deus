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
Test cases for the intensity classes.
'''

import unittest

import intensityprovider
import testimplementations


class TestIntensity(unittest.TestCase):
    '''
    Unit test class for intensity related classes.
    '''

    def test_always_the_same_intensity_provider(self):
        '''
        Tests an test implementation which always
        returns the same values regardless of
        the coordinates.
        '''
        intensity_provider = (
            testimplementations.AlwaysTheSameIntensityProvider(
                kind='PGA',
                value=1.0,
                unit='g'
            )
        )

        intensities, units = intensity_provider.get_nearest(1, 1)

        self.assertLess(0.9, intensities['PGA'])
        self.assertLess(intensities['PGA'], 1.1)

        self.assertEqual(units['PGA'], 'g')

        intensities2, units2 = intensity_provider.get_nearest(180, 90)
        self.assertEqual(intensities, intensities2)
        self.assertEqual(units, units2)

    def test_alias_intensity_provider(self):
        '''
        Test for aliases.
        '''
        inner_intensity_provider = (
            testimplementations.AlwaysTheSameIntensityProvider(
                kind='PGA',
                value=1.0,
                unit='g'
            )
        )

        intensity_provider = intensityprovider.AliasIntensityProvider(
            inner_intensity_provider,
            aliases={
                'SA_01': ['PGA'],
                'SA_03': ['PGA'],
                'ID': ['mwh'],
            }
        )

        intensities, units = intensity_provider.get_nearest(1, 1)

        for kind in ['PGA', 'SA_01', 'SA_03']:
            self.assertLess(0.9, intensities[kind])
            self.assertLess(intensities[kind], 1.1)

            self.assertEqual(units[kind], 'g')

        self.assertNotIn('mwh', intensities.keys())
        self.assertNotIn('ID', intensities.keys())

    def test_conversion_intensity_provider(self):
        '''
        Test for intensity conversion.
        '''
        inner_intensity_provider = (
            testimplementations.AlwaysTheSameIntensityProvider(
                kind='PGA',
                value=1.0,
                unit='g'
            )
        )

        def pga_to_pga1000(old_intensity, old_unit):
            return old_intensity / 1000, 'g/1000'

        intensity_provider = intensityprovider.ConversionIntensityProvider(
            inner_intensity_provider,
            from_intensity='PGA',
            as_intensity='PGA/1000',
            fun=pga_to_pga1000,
        )

        intensities, units = intensity_provider.get_nearest(1, 1)

        self.assertLess(0.9, intensities['PGA'])
        self.assertLess(intensities['PGA'], 1.1)

        self.assertEqual(units['PGA'], 'g')

        self.assertLess(0.0009, intensities['PGA/1000'])
        self.assertLess(intensities['PGA/1000'], 0.0011)

        self.assertEqual(units['PGA/1000'], 'g/1000')


if __name__ == '__main__':
    unittest.main()
