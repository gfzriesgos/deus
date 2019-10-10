#!/usr/bin/env python3

import unittest

import intensityprovider
import testimplementations


class TestIntensity(unittest.TestCase):
    '''
    Unit test class for intensity related classes.
    '''

    def test_always_the_same_intensity_provider(self):
        intensity_provider = testimplementations.AlwaysTheSameIntensityProvider(
            kind='PGA',
            value=1.0,
            unit='g'
        )

        intensities, units = intensity_provider.get_nearest(1, 1)

        self.assertLess(0.9, intensities['PGA'])
        self.assertLess(intensities['PGA'], 1.1)

        self.assertEqual(units['PGA'], 'g')


    def test_alias_intensity_provider(self):
        inner_intensity_provider = testimplementations.AlwaysTheSameIntensityProvider(
            kind='PGA',
            value=1.0,
            unit='g'
        )

        intensity_provider = intensityprovider.AliasIntensityProvider(
            inner_intensity_provider,
            aliases={
                'SA_01': 'PGA',
                'SA_03': 'PGA',
                'ID': 'mwh',
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
        inner_intensity_provider = testimplementations.AlwaysTheSameIntensityProvider(
            kind='PGA',
            value=1.0,
            unit='g'
        )

        intensity_provider = intensityprovider.ConversionIntensityProvider(
            inner_intensity_provider,
            from_intensity='PGA',
            as_intensity='PGA/1000',
            fun=lambda i, u: (i/1000.0, 'g/1000')
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

