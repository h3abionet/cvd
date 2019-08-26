#!/usr/bin/env python2.7

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--chip_file", default="${chip_file}", help="")
parser.add_argument("--out_chip_file", default="${out_chip_file}", help="")

args = parser.parse_args()

def process_chip_file(chip_file, out_chip_file):
    """

    :param chip_file:
    :return:
    """
    output = {}
    for line in open(chip_file):
        line = line.strip().split(',')
        try:
            chr = line[9]
            pos = line[10]
            if chr not in output:
                output[chr] = open(out_chip_file+'_'+chr+'.tsv', 'w')
            output[chr].writelines('\\t'.join([chr,pos,pos])+'\\n')
        except:
            continue
    for chr in output:
        output[chr].close()


process_chip_file(args.chip_file, args.out_chip_file)