#!/usr/bin/env nextflow
/*
========================================================================================
                         h3abionet/cvd
========================================================================================
 h3abionet/cvd Analysis Pipeline.
 #### Homepage / Documentation
 https://github.com/h3abionet/cvd
----------------------------------------------------------------------------------------
*/


def helpMessage() {
    log.info nfcoreHeader()
    log.info"""

    Usage:

    The typical command for running the pipeline is as follows:

    nextflow run h3abionet/cvd --mapping_file --pheno_file --csv_template --pheno_output

    Mandatory arguments:
      --'main.nf'
                Path to mapping file (must be surrounded with quotes)
      --pheno_file                  Path to study phenotype csv file (comma separated file)
      --csv_template
      --pheno_output
      -profile                      Configuration profile to use. Can use multiple (comma separated)
                                    Available: conda, docker, singularity, awsbatch, test and more.
    Other options:
      --outdir                      The output directory where the results will be saved
      --email                       Set this parameter to your e-mail address to get a summary e-mail with details of the run sent to you when the workflow exits
      -name                         Name for the pipeline run. If not specified, Nextflow will automatically generate a random mnemonic.
    """.stripIndent()
}

/*
 * SET UP CONFIGURATION VARIABLES
 */

// Show help emssage
if (params.help){
    helpMessage()
    exit 0
}


// Has the run name been specified by the user?
//  this has the bonus effect of catching both -name and --name
custom_runName = params.name
if( !(workflow.runName ==~ /[a-z]+_[a-z]+/) ){
  custom_runName = workflow.runName
}

// Stage config files
ch_output_docs = Channel.fromPath("$baseDir/docs/output.md")

params.outdir ='.'
params.project_name = ''
params.hostnames = ''

/*
 * Create a channel for input read files
 */
 // Check if genome exists in the config file
 if (params.genomes && params.genome && !params.genomes.containsKey(params.genome)) {
     exit 1, "The provided genome '${params.genome}' is not available in the iGenomes file. Currently the available genomes are ${params.genomes.keySet().join(", ")}"
 }
chips = []
if(params.chips){
    params.chips.each{ chip ->
        chip_name = chip[0]
        chip_file = chip[1]
        if (!file(chip_file).isFile()) {
            System.err.println "|-- ERROR: \"File ${chip_name}: ${chip_file} does not exist  - Check your config.\""
            exit 1
        }
    }

}

mapping_files = Channel.from([[file(params.mapping_file), file(params.pheno_file), file(params.csv_template), file(params.pheno_output)]])


// Header log info
log.info nfcoreHeader()
def summary = [:]
if(workflow.revision) summary['Pipeline Release'] = workflow.revision
summary['Run Name']             = custom_runName ?: workflow.runName
summary['mapping_file']         = params.mapping_file
summary['pheno_file']           = params.pheno_file
summary['csv_template']           = params.csv_template
summary['pheno_output']           = params.pheno_output
summary['Max Resources']        = "$params.max_memory memory, $params.max_cpus cpus, $params.max_time time per job"
if(workflow.containerEngine) summary['Container'] = "$workflow.containerEngine - $workflow.container"
summary['Output dir']           = params.outdir
summary['Launch dir']           = workflow.launchDir
summary['Working dir']          = workflow.workDir
summary['Script dir']           = workflow.projectDir
summary['User']                 = workflow.userName
summary['Config Profile']       = workflow.profile
if(params.config_profile_description) summary['Config Description'] = params.config_profile_description
if(params.config_profile_contact)     summary['Config Contact']     = params.config_profile_contact
if(params.config_profile_url)         summary['Config URL']         = params.config_profile_url
if(params.email) {
  summary['E-mail Address']  = params.email
}
log.info summary.collect { k,v -> "${k.padRight(18)}: $v" }.join("\n")
log.info "\033[2m----------------------------------------------------\033[0m"

// Check the hostnames against configured profiles
checkHostname()

def create_workflow_summary(summary) {
    def yaml_file = workDir.resolve('workflow_summary_mqc.yaml')
    yaml_file.text  = """
    id: 'pheno_mapping-summary'
    description: " - this information is collected when the pipeline is started."
    section_name: 'h3abionet/cvd Workflow Summary'
    section_href: 'https://github.com/h3abionet/cvd'
    plot_type: 'html'
    data: |
        <dl class=\"dl-horizontal\">
${summary.collect { k,v -> "            <dt>$k</dt><dd><samp>${v ?: '<span style=\"color:#999999;\">N/A</a>'}</samp></dd>" }.join("\n")}
        </dl>
    """.stripIndent()

   return yaml_file
}


/*
 * Parse software version numbers
 */
process pheno_mapping {
    tag "pheno_mapping_${params.project_name}"
    publishDir "${params.outdir}/harmonisez_pheno", mode: 'copy'

    input:
    set file(mapping_file), file(pheno_file), file(csv_template), file(pheno_output) from mapping_files

    output:
    set file(mapping_file) into pheno_mapping

    script:
    """
    python3 ${workflow.projectDir}/bin/pheno_mapping.py \
        --mapping_file ${mapping_file} \
        --pheno_file ${pheno_file} \
        --csv_template ${csv_template} \
        --pheno_output ${pheno_output}
    """
}


/*
 * Completion e-mail notification
 */
workflow.onComplete {
    if(workflow.success){
        log.info "${c_purple}[h3abionet/cvd]${c_green} Pipeline completed successfully${c_reset}"
    } else {
        checkHostname()
        log.info "${c_purple}[h3abionet/cvd]${c_red} Pipeline completed with errors${c_reset}"
    }
}


def nfcoreHeader(){
    // Log colors ANSI codes
    c_reset = params.monochrome_logs ? '' : "\033[0m";
    c_dim = params.monochrome_logs ? '' : "\033[2m";
    c_black = params.monochrome_logs ? '' : "\033[0;30m";
    c_green = params.monochrome_logs ? '' : "\033[0;32m";
    c_yellow = params.monochrome_logs ? '' : "\033[0;33m";
    c_blue = params.monochrome_logs ? '' : "\033[0;34m";
    c_purple = params.monochrome_logs ? '' : "\033[0;35m";
    c_cyan = params.monochrome_logs ? '' : "\033[0;36m";
    c_white = params.monochrome_logs ? '' : "\033[0;37m";

    return """    ${c_dim}----------------------------------------------------${c_reset}
                                            ${c_green},--.${c_black}/${c_green},-.${c_reset}
    ${c_blue}        ___     __   __   __   ___     ${c_green}/,-._.--~\'${c_reset}
    ${c_blue}  |\\ | |__  __ /  ` /  \\ |__) |__         ${c_yellow}}  {${c_reset}
    ${c_blue}  | \\| |       \\__, \\__/ |  \\ |___     ${c_green}\\`-._,-`-,${c_reset}
                                            ${c_green}`._,._,\'${c_reset}
    ${c_purple}  h3abionet/cvd v${workflow.manifest.version}${c_reset}
    ${c_dim}----------------------------------------------------${c_reset}
    """.stripIndent()
}

def checkHostname(){
    def c_reset = params.monochrome_logs ? '' : "\033[0m"
    def c_white = params.monochrome_logs ? '' : "\033[0;37m"
    def c_red = params.monochrome_logs ? '' : "\033[1;91m"
    def c_yellow_bold = params.monochrome_logs ? '' : "\033[1;93m"
    if(params.hostnames){
        def hostname = "hostname".execute().text.trim()
        params.hostnames.each { prof, hnames ->
            hnames.each { hname ->
                if(hostname.contains(hname) && !workflow.profile.contains(prof)){
                    log.error "====================================================\n" +
                            "  ${c_red}WARNING!${c_reset} You are running with `-profile $workflow.profile`\n" +
                            "  but your machine hostname is ${c_white}'$hostname'${c_reset}\n" +
                            "  ${c_yellow_bold}It's highly recommended that you use `-profile $prof${c_reset}`\n" +
                            "============================================================"
                }
            }
        }
    }
}
