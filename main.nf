#!/usr/bin/env nextflow
nextflow.enable.dsl=2

/*
========================================================================================
h3abionet/cvd
========================================================================================
h3abionet/cvd Analysis Pipeline.
Homepage / Documentation
https://github.com/h3abionet/cvd
----------------------------------------------------------------------------------------
*/

//// Help functions
def helpMessage() {
    // log.info nfcoreHeader()
    log.info"""

    Usage:

    The typical command for running the pipeline is as follows:

    nextflow run h3abionet/cvd --mapping_file "mapping.csv" --pheno_file "pheno.csv" --pheno_output "output.csv"

    Mandatory arguments:
      --mapping_file        : Path to mapping file (must be surrounded with quotes)
      --pheno_file          : Path to study phenotype csv file
      --pheno_output        : Output phenotype csv file
      --outdir              : The output directory where the results will be saved
      -profile              : Configuration profile to use. Can use multiple (comma separated). 
                              Available: local, singularity, test, slurm and more.
    """.stripIndent()
}

def check_files(file_list) {
    file_list.each { myfile ->
        if (!file(myfile).exists() && !file(myfile).isFile()) exit 1, "|-- ERROR: File ${myfile} not found. Please check your params or config file."
    }
}

process pheno_mapping {
    tag "pheno_mapping"
    publishDir "${params.outdir}/harmonised_pheno", mode: 'copy'

    input:
        tuple file(mapping_file), file(pheno_file), val(pheno_output)

    output:
        tuple file(pheno_output)
    
    script:
        """
        pheno_mapping.py --pheno_file ${pheno_file} --mapping_file ${mapping_file} --pheno_output ${pheno_output} 
        """
}

process generate_mapping {
    tag "generate_mapping"
    publishDir "${params.outdir}/harmonised_pheno", mode: 'copy'

    input:
        tuple file(json_file), file(out_file)

    output:
        tuple file(mapping_file)
    
    script:
        mapping_file = "${out_file}_mapping_file.xlsx"
        """
        generate_mapping.py --json_file ${json_file} --mapping_file ${mapping_file}
        """
}

// Show help emssage

workflow{
    if (params.help){
        helpMessage()
        exit 0
    }

    // Generate mapping file from JSON
    if(params.gen_mapping){
        check_files( [ file(params.json_file) ] )
        generate_mapping(Channel.from([[ file(params.json_file), file(params.mapping_file) ]]))
    }

    // Harmonise data based on mapping file
    if(params.harm){
        check_files( [file(params.mapping_file), file(params.pheno_file)] )
        pheno_mapping(Channel.from([[file(params.mapping_file), file(params.pheno_file), params.pheno_output]])).view()
    }

}