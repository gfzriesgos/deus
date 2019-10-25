#!/usr/bin/env python3

import argparse
import json

import pandas as pd

def main():
    arg_parser = argparse.ArgumentParser('Script to convert a conversion matrix for taxonomies to json files')
    arg_parser.add_argument('inputfile', help='The xlsx with the matrix of the conversion (must be readable by pandas)')
    arg_parser.add_argument('source_schema', help='The name of the source schema (taxonomies are rows in the input file).')
    arg_parser.add_argument('target_schema', help='The name of the target schema (taxonomies are the columns in the input file)')

    args = arg_parser.parse_args()

    # if it is csv, we need another read function
    data = pd.read_excel(args.inputfile)

    # we are not interested in a total 
    data = data[ set(data.columns) - set(['Total'])]

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
    conv_matrix_str = data.to_json()
    conv_matrix = json.loads(conv_matrix_str)
    result['conv_matrix'] = conv_matrix

    out = json.dumps(result, indent=4)

    print(out)

if __name__ == '__main__':
    main()
