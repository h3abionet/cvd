#!/usr/bin/env python3

import argparse,sys
import csv
import time
import pyparsing as pp

parser = argparse.ArgumentParser()
parser.add_argument("--mapping_file", default="", help="Mapping file ")
parser.add_argument("--pheno_file", default="", help="Phenotype file")
parser.add_argument("--pheno_output", default="", help="Phenotype output file")
args = parser.parse_args()

CRED = '\033[91m'
CEND = '\033[0m'

def error_message(code, format1='', format2='', format3='', format4='', format5=''):
    """
    Print error message
    """
    if code == 1:
        print('{0}\nError: \"NEW Variable Name\" variable missing for record -- {2} {1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    elif code == 2:
        print('{0}\nError: \"Study Variable Format\" variable missing for record -- {2} {1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    elif code == 3:
        print('{0}\nError: \"Study Variable Name\" or \"Study Variable Format\" variable missing for record -- {2} {1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    elif code == 4:
        print('{0}\nError: \"Wrong option {2}\" for record -- {3} {1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    elif code == 5:
        print('{0}\nError: \"Coding \'{3}\' not included in mapping for variable \'{2}\' in record {4}\"{1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    elif code == 6:
        print('{0}\nError: \"Wrong Variable Format {2}\" in \'mapping file {4}\' for record -- {3} {1}\n'.format(CRED, CEND, format1, format2, format3, format4, format5))
    sys.exit(1)



def read_mapping(mapping_file):
    '''
    '''
    study_data = {}
    option_formats = ['text', 'single_choice', 'hardcode', 'automated'] ## with formula must be computed last
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
            if format in data_formats:
                for item in data_formats[format]:
                    # print(item)
                    item_str = ', '.join([':'.join([key,item[key]]) for key in item if key != None and item[key] != None]) # to use for error logging
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
                                # print(study_option)
                                for it in [it for it in study_option.split("|")]:
                                    newStr = pp.commaSeparatedList.parseString(it).asList() # in case there is a comma in an option
                                    try:
                                        study_options[newStr[0]] = newStr[1].replace('\'','')
                                    except:
                                        error_message(4, study_option, item_str)
                            elif var_format in ['automated', 'hardcode']: ## Case 8: automated
                                study_data[study_var] = {}
                                study_options = ''
                            else:
                                error_message(6, var_format, item_str, mapping_file)
                            study_data[study_var] = {'study_options':study_options}

                            ## Get new CVD variable and options
                            if 'NEW Variable Name' in item:
                                if item['NEW Variable Name'] != '':
                                    new_var = item['NEW Variable Name']
                                    new_option = item['NEW to Study Mapping']
                                    new_coding = item['NEW Variable Coding']
                                    study_data[study_var]['new_variable'] = new_var
                                     # in case there is a comma in an option
                                    if var_format == 'text': ## Case 1: text
                                        new_mapping = new_option
                                        study_data[study_var]['new_mapping'] = new_mapping
                                    elif var_format == 'single_choice': # Case 2: multiple options field
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
                                    else:
                                        error_message(6, var_format, item_str, mapping_file)
                                    # elif var_format == 'automated': ## Case 9: automated
                                    #     if '+' in new_option:
                                    #         options = [it.strip() for it in new_option.split('=')[1].replace('\'','').split('+')]
                                    #     new_mapping = new_option
                                    # elif new_coding == '': # Case 1: free text field
                                    #     new_mapping = {}
                                    study_data[study_var]['new_mapping'] = new_mapping
                                    study_data[study_var]['new_format'] = var_format
                                else:
                                    error_message(1, item_str)
                            else:
                                error_message(1, item_str)
                        else:
                            error_message(2, item_str)
                    else:
                        error_message(3, item_str)

    # print(study_data)
    return study_data ## return variables list as well to use during convertion

def pheno_mapping(pheno_file, mapping_file):
    '''
    '''
    datas = {}
    phenos = []
    mapping = read_mapping(mapping_file)
    # print(mapping)
    with open(pheno_file, newline='') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='\"')
        record = 1
        # print(list(data))
        for item in data:
            item = dict(item)
            item_str = ', '.join([':'.join([key,item[key]]) for key in item]) # to use for error logging
            new_item = {}
            # print("-------0",item)
            for var in item:
                if var in mapping and 'new_mapping' in mapping[var] and 'new_variable' in mapping[var] and 'new_format' in mapping[var]:
                    new_var = mapping[var]['new_variable']
                    var_format =  mapping[var]['new_format']
                    # print("---------",var, var_format)
                    if new_var not in phenos:
                        phenos.append(new_var)
                    if var_format == 'text': ## Case 1
                        # print("-------1",item)
                        new_item[new_var] = item[var]
                    elif var_format == 'single_choice': ## Case 2
                            # print("-------2",item)
                            # print(item[var], mapping[var])
                            if item[var] in mapping[var]['new_mapping'] or item[var] == '':
                                new_item[new_var] = item[var]
                                if item[var] != '':
                                    new_item[new_var] = mapping[var]['new_mapping'][item[var]]
                                else:
                                    new_item[new_var] = '999'
                            else:
                                error_message(5, var, item[var], item_str)
                    else:
                        print(var, var_format)
                        # print('mamana')
                        time.sleep(10)
                    # print("-------FINAL",[item])
                    # time.sleep(10)
            datas[record] = new_item
            record += 1
        # print(datas)
        return datas

def pheno_output(pheno_file, mapping_file, pheno_output):
    """
    """
    mapping = pheno_mapping(args.pheno_file, args.mapping_file)
    output = open(pheno_output, 'w')
    for pid in sorted(mapping):
        datas = [pid]
        if cvs_pheno in mapping[pid]:
            datas.append(mapping[pid][cvs_pheno])
        else:
            datas.append('999')
        output.writelines(','.join(datas)+'\n')
    output.close()


if __name__ == '__main__':
    # print(read_mapping(args.mapping_file))
    # pheno_mapping(args.pheno_file, args.mapping_file)
    pheno_output(args.pheno_file, args.mapping_file, args.pheno_output)
