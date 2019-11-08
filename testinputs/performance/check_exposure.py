#!/usr/bin/env python3

import collections 
import pandas
import geopandas

TaxDsTuple = collections.namedtuple('TaxDsTuple', 'taxonmy damagestate')

all_cells = geopandas.read_file('exposure_so_far.json')

all_expos = all_cells['expo']

for expo in all_expos:
    expo_df = pandas.DataFrame(expo)
    tax_ds_tuples_counts = collections.defaultdict(lambda: 0)

    for _, row in expo_df.iterrows():
        taxonomy = row['Taxonomy']
        ds = row['Damage']

        tax_ds_tuples_counts[TaxDsTuple(taxonomy, ds)] += 1

    any_more_than_1 = any([v > 1 for v in tax_ds_tuples_counts.values()])
    assert any_more_than_1 == False




