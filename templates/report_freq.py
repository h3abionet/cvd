#!/usr/bin/env python2.7

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--pop_freqs", default="${pop_freqs}", help="")
parser.add_argument("--report_maf", default="${report_maf}", help="")

args = parser.parse_args()

def report_freq(pop_freqs, report_maf):
    """

    :param pop_freqs:
    :return:
    """
    out = open(report_maf, 'w')
    data = {}
    pops = []
    snps = set()
    for fil in pop_freqs.split(' '):
        for line in open(fil):
            if "MAF_FREQ" in line:
                line = line.strip().split('\t')
                pop = line[-1].split('_MAF_FREQ')[0]
                data[pop] = {}
                pops.append(pop)
            else:
                line = line.strip().split('\t')
                snp = line[0]
                freq = line[-1]
                data[pop][snp] = freq
                snps.add(snp)
                #for pop in pops:
    snps =  ['_'.join(snp) for snp in sorted([snp.split('_') for snp in snps], key = lambda x: (x[0], x[1]))]
    out.writelines('\\t'.join(['SNP_ID']+pops)+'\\n')
    for snp in snps:
        datas =  [snp]
        for pop in pops:
            if snp not in data[pop]:
                data[pop][snp] = ''
            datas.append(data[pop][snp])
        out.writelines('\\t'.join(datas)+'\\n')

    out.close()


if __name__ == '__main__':
    report_freq(args.pop_freqs, args.report_maf)