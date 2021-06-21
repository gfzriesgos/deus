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

import collections
import pandas
import geopandas

TaxDsTuple = collections.namedtuple('TaxDsTuple', 'taxonomy damage state')

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
    assert any_more_than_1 is False
