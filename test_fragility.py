#!/usr/bin/env python3

import unittest
import fragility


class TestFragility(unittest.TestCase):

    def test_read_schema_from_fragility_file(self):
        '''
        Reads the schema from the fragility file.
        '''

        fr_file = fragility.Fragility.from_file(
            './testinputs/fragility_sara.json')
        fr_provider = fr_file.to_fragility_provider()

        schema = fr_provider.get_schema()

        self.assertEqual('SARA_v1.0', schema)

        fr_file2 = fragility.Fragility.from_file(
            './testinputs/fragility_suppasri.json')
        fr_provider2 = fr_file2.to_fragility_provider()

        schema2 = fr_provider2.get_schema()

        self.assertEqual('SUPPASRI2013.0', schema2)

if __name__ == '__main__':
    unittest.main()
