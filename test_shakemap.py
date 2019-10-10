#!/usr/bin/env python3

import unittest

import shakemap


class TestShakemap(unittest.TestCase):

    def test_read_ts_shakemap(self):
        shake_map_ts = shakemap.Shakemaps.from_file(
            './testinputs/shakemap_tsunami.xml')
        ts_provider = shake_map_ts.to_intensity_provider()

        ts_intensity, ts_units = ts_provider.get_nearest(
            lon=-71.547, lat=-32.803)

        self.assertEqual('m', ts_units['MWH'])

        self.assertLess(3.5621, ts_intensity['MWH'])
        self.assertLess(ts_intensity['MWH'], 3.5623)

    def test_read_shakemap(self):
        '''
        Reads a normal shakemap (as it is the output of shakyground.
        :return: None
        '''
        shake_map_eq = shakemap.Shakemaps.from_file(
            './testinputs/shakemap.xml')
        eq_provider = shake_map_eq.to_intensity_provider()

        self.assertIsNotNone(eq_provider)

        eq_intensity, eq_units = eq_provider.get_nearest(
            lon=-72.7, lat=-31.6416666667)

        self.assertEqual('g', eq_units['PGA'])

        self.assertLess(0.028835543, eq_intensity['PGA'])
        self.assertLess(eq_intensity['PGA'], 0.028835545)

    def test_lahar_shakemap(self):
        '''
        Reads a lahar shakemap.
        '''

        shake_map_lahar = shakemap.Shakemaps.from_file(
            './testinputs/shakemap_lahar.xml'
        )
        lh_provider = shake_map_lahar.to_intensity_provider()

        lh_intensity, lh_units = lh_provider.get_nearest(
            lon=-78.5075157783, lat=-0.499855281537
        )

        self.assertEqual('m/s', lh_units['MAXVELOCITY'])
        self.assertLess(0.029, lh_intensity['MAXVELOCITY'])
        self.assertLess(lh_intensity['MAXVELOCITY'], 0.031)


if __name__ == '__main__':
    unittest.main()
