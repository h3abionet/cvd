#!/usr/bin/env python3

import argparse,sys
import csv
import time
import pyparsing as pp

parser = argparse.ArgumentParser()
parser.add_argument("--mapping_file", default="${mapping_file}", help="Mapping file ")
parser.add_argument("--pheno_file", default="${pheno_file}", help="Phenotype file")
parser.add_argument("--csv_template", default="${csv_template}", help="CSV template file")
parser.add_argument("--pheno_output", default="${pheno_output}", help="Phenotype output file")
args = parser.parse_args()

CRED = '\033[91m'
CEND = '\033[0m'

def read_mapping(mapping_file):
    '''
    '''
    study_data = {}
    option_formats = ['text', 'single_choice', 'automated'] ## with formula must be computed last
    with open(mapping_file, newline='') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='\"')
        ## Get all Variable formats
        data_formats = {}
        for item in data:
            item = dict(item)
            if 'Study Variable Format' in item:
                format = item['Study Variable Format']
                if format != '':
                    if format not in data_formats:
                        data_formats[format] = []
                    data_formats[format].append(item)

        ## Process non formula variables first
        for format in option_formats:
            for item in data_formats[format]:
                # print(item)
                if 'Study Variable Name' in item and 'Study Variable Format' in item:
                    ## Get old study variable
                    study_var = item['Study Variable Name'] #TODO check this is not empty
                    study_option = item['Study Variable Coding']
                    var_format = item['Study Variable Format']
                    if item['Study Variable Format'] != '':
                        if var_format == 'text': ## Case 1
                            study_data[study_var] = {}
                            study_options = study_option
                        elif var_format == 'single_choice': # Case 2: multiple options field
                            study_options = {}
                            print(study_option)
                            for it in [it for it in study_option.split("|")]:
                                newStr = pp.commaSeparatedList.parseString(it).asList() # in case there is a comma in an option
                                try:
                                    study_options[newStr[0]] = newStr[1].replace('\'','')
                                except:
                                    print('{1}\nError: \"Wrong option {3}\" for -- {0} {2}\n'.format(', '.join(item.values()), CRED, CEND, study_option))
                                    sys.exit(1)
                        elif var_format == 'automated': ## Case 8: automated
                            study_data[study_var] = {}
                            study_options = ''
                        elif study_option == '': # Case 1: free text field
                            study_data[study_var] = {}
                            study_options = ''
                        study_data[study_var] = {'study_options':study_options}

                        ## Get new CVD variable and options
                        if 'NEW Variable Name' in item:
                            if item['NEW Variable Name'] != '':
                                new_var = item['NEW Variable Name']
                                new_option = item['NEW to Study Mapping']
                                new_coding = item['NEW Variable Coding']
                                study_data[study_var]['new_variable'] = new_var
                                 # in case there is a comma in an option
                                if var_format == 'text': ## Case 1: automated
                                    new_mapping = new_option
                                    study_data[study_var]['new_mapping'] = new_mapping
                                elif var_format == 'automated': ## Case 9: automated
                                    if '+' in new_option:
                                        options = [it.strip() for it in new_option.split('=')[1].replace('\'','').split('+')]
                                        # for option in options:
                                        #     if '$' in option:
                                    new_mapping = new_option
                                elif new_coding == '': # Case 1: free text field
                                    new_mapping = {}
                                elif '|' in new_option: # Case 2: multiple options field
                                    new_mapping = {}
                                    for option in [it.split('=') for it in new_option.split("|")]:
                                        option = [opt.strip() for opt in option] # remove whitespace
                                        key = option[0]
                                        vals = option[1].split(',')
                                        if len(vals) == 1:
                                            new_mapping[vals[0]] = key
                                        else:
                                            for val in vals:
                                                new_mapping[val.strip()] = key.strip()
                                study_data[study_var]['new_mapping'] = new_mapping
                                study_data[study_var]['new_format'] = var_format
                            else:
                                print('{1}\nError: \"NEW Variable Name\" variable missing for -- {0} {2}\n'.format(', '.join(item.values()), CRED, CEND))
                                sys.exit(1)
                        else:
                            print('{1}\nError: \"NEW Variable Name\" variable missing for -- {0} {2}\n'.format(', '.join(item.values()), CRED, CEND))
                            sys.exit(1)
                    else:
                        print('{1}\nError: \"Study Variable Format\" variable missing for -- {0} {2}\n'.format(', '.join(item.values()), CRED, CEND))
                        sys.exit(1)
                else:
                    print('{1}\nError: \"Study Variable Name\" or \"Study Variable Format\" variable missing for -- {0} {2}\n'.format(', '.join(item.values()), CRED, CEND))
                    sys.exit(1)
    return study_data

def read_csv_template(csv_template):
    """
    """
    with open(csv_template) as data:
        item = data.readlines()[0]
    return item.split(',')

def pheno_mapping(pheno_file, mapping_file):
    '''
    '''
    datas = {}
    phenos = []
    mapping = read_mapping(mapping_file)
    print(mapping)
    with open(pheno_file, newline='') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='\"')
        record = 1
        # print(list(data))
        for item in data:
            item = dict(item)
            new_item = {}
            print("-------1",item)
            for var in item:
                if var in mapping:
                    new_var = mapping[var]['new_variable']
                    var_format =  mapping[var]['new_format']
                    print("---------",var, var_format)
                    if new_var not in phenos:
                        phenos.append(new_var)
                    if var_format == 'text': ## Case 1
                        # item[new_var] = item.pop(var)
                        new_item[new_var] = item[var]
                    elif var_format == 'single_choice': ## Case 2
                        # try:
                            print("-------2",item)
                            new_value = mapping[var]['new_mapping'][item[var]]
                            # item[new_var] = item.pop(var)
                            new_item[new_var] = item[var]
                            print("-------3",item)
                            # item[new_var] = new_value
                            new_item[new_var] = new_value
                            print("-------4",item)
                            print('mamana')
                            time.sleep(4)
                            #
                            # print(var, new_var, var_format)
                            # print(item[new_var])
                        # except KeyError:
                            # if item[new_var] not in new_var:
                            #     print(CRED + '\nError: \"Invalid coding {0}:{1} in record {2}\"\n'.format(var, item[var],item['pid'])+ CEND)
                            #     sys.exit(1)
                    # else: # Mapping case 2
                    #     try:
                    #         new_value = mapping[var]['new_mapping'][item[var]]
                    #         old_var = var
                    #         item[new_var] = item.pop(var)
                    #         item[new_var] = new_value
                    #     except KeyError:
                    #         if item[var] not in new_var:
                    #             print(CRED + '\nError: \"Invalid coding {0}:{1} in record {2}\"\n'.format(var, item[var],item['pid'])+ CEND)
                    #             sys.exit(1)
                    # print(item)
            datas[record] = new_item
            record += 1
        print(datas)
        return datas

def pheno_output(pheno_file, mapping_file, csv_template, pheno_output):
    """
    """
    mapping = pheno_mapping(args.pheno_file, args.mapping_file)
    csv_template = read_csv_template(args.csv_template)
    output = open(pheno_output, 'w')
    output.writelines(','.join(csv_template)+'\n')
    for pid in sorted(mapping):
        datas = [pid]
        for cvs_pheno in csv_template:
            if cvs_pheno in mapping[pid]:
                datas.append(mapping[pid][cvs_pheno])
            else:
                datas.append('999')
        output.writelines(','.join(datas)+'\n')
    output.close()


if __name__ == '__main__':
    # print(read_mapping(args.mapping_file))
    pheno_mapping(args.pheno_file, args.mapping_file)
    # pheno_output(args.pheno_file, args.mapping_file, args.csv_template, args.pheno_output)
