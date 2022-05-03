#!/usr/bin/env python3

from pprint import pprint
import pandas as pd
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mapping_file", default="", help="Output Mapping file ")
parser.add_argument("--json_file", default="", help="JSON file")
args = parser.parse_args()

# TODO minimal mode


def generate_mapping_from_json(json_file, mapping_file):
    """_summary_
    """

    with open(json_file) as f:
        data = json.load(f)
    results = {}
    header = ''
    for prop in data['properties']:
        if data['properties'][prop]['type'] == 'object':
            if prop in data['required']:
                variables = data['properties'][prop]['properties']
                variables['record_id'] = {
                    'description': 'Record ID', 'type': 'autonumber'}
                for var in variables:
                    if 'enum' in variables[var]:
                        options = variables[var]['enum']
                        variables[var]['coding'] = '|'.join(
                            [f'{options.index(it)+1},{it}' for it in variables[var]['enum']])
                        variables[var]['enum'] = 'single_choice'
                    else:
                        variables[var]['coding'] = ''
                    for it in variables[var]:
                        if 'type' in variables[var]:
                            if 'string' in variables[var]['type']:
                                variables[var]['type'] = 'text'
                    study_format = ''
                    mapping = f'{var}='
                    if 'record_id' in var:
                        study_format = 'automated'
                        mapping = f'{var}={{pid}}'
                    results[f'{list(variables.keys()).index(var)+1}'] = ['',
                                                                         '', '', study_format, var]+[val for val in variables[var].values()]
                    results[f'{list(variables.keys()).index(var)+1}'].append(mapping)
                    if header == '':
                        header = ['Study Variable Name', 'Study Variable Description', 'Study Variable Coding',
                                  'Study Variable Format', 'NEW Variable Name']+list(variables[var].keys())
                        for h in range(len(header)):
                            if header[h] == 'type':
                                header[h] = 'NEW Variable Format'
                            if header[h] == 'description':
                                header[h] = 'NEW Variable Description'
                            if header[h] == 'coding':
                                header[h] = 'NEW Variable Coding'
                        header.append('NEW to Study Mapping')

        else:
            continue
    res = pd.DataFrame.from_dict(results, orient='index', columns=header)
    res.to_excel(f'{mapping_file}', index=None, header=True)


if __name__ == '__main__':
    generate_mapping_from_json(args.json_file, args.mapping_file)
