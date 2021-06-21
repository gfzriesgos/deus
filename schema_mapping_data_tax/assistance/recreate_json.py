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

import argparse
import json

import pandas as pd


def main():
    arg_parser = argparse.ArgumentParser(
        'Script to convert a conversion matrix for taxonomies to json files'
    )
    arg_parser.add_argument(
        'inputfile',
        help='The xlsx with the matrix of the conversion '
             + '(must be readable by pandas)'
    )
    arg_parser.add_argument(
        'source_schema',
        help='The name of the source schema '
             + '(taxonomies are rows in the input file).'
    )
    arg_parser.add_argument(
        'target_schema',
        help='The name of the target schema '
             + '(taxonomies are the columns in the input file)'
    )

    args = arg_parser.parse_args()

    # if it is csv, we need another read function
    data = pd.read_excel(args.inputfile)

    # we are not interested in a total
    data = data[set(data.columns) - set(['Total'])]

    source_taxonomies = list(data['Taxonomy'].unique())
    target_taxonomies = list(set(data.columns) - set(['Taxonomy']))
    result = {
        'source_schema': args.source_schema,
        'target_schema': args.target_schema,
        'source_taxonomies': source_taxonomies,
        'target_taxonomies': target_taxonomies,
    }

    data = data.set_index('Taxonomy')

    # check
    assert(all([0.999 < sum(row) < 1.001 for row in data.values]))

    # follow the very same structure as for the damage state mappings
    # so target_taxonomies as keys in the first level
    conv_matrix_str = data.transpose().to_json()
    conv_matrix = json.loads(conv_matrix_str)
    result['conv_matrix'] = conv_matrix

    out = json.dumps(result, indent=4)

    print(out)


if __name__ == '__main__':
    main()
