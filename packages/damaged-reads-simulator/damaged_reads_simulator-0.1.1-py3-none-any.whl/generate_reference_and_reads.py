import sys, os
sys.path.append(os.path.realpath("./"))
from sys import stderr, argv
import os
import re
import argparse
from libs.simulations_libs import *
import numpy as np


def read_parameters_file(parameters_info_file):

    with open(parameters_info_file, 'r') as f:
        specifications = [i.strip().split(":") for i in f if i[0] != "#" and len(i) > 2]

    CONSTANTS = {
        'make_reference': None,
        'reference_fasta_path': None,
        'GC_pct': None,
        'contig_lengths': None,
        'n_reads': None,
        'read_length': None,
        'insert_length': None,
        'insert_length_var': None,
        'skewed_insert_sizes': None,
        'library_type': None,
        'methylated_genome': None,
        'pct_methylation': None,
        'random_seed': 42,
        'prefix': None,
        'random_mismatch_error_rate': 0.0001
    }

    for key, value in specifications:
        value = value.strip()
        match key:
            case 'generate reference':          CONSTANTS['make_reference'] = value.lower() == 'true'
            case 'reference file path':         CONSTANTS['reference_fasta_path'] = value
            case 'GC percentage':               CONSTANTS['GC_pct'] = int(value)
            case 'length of contigs':           CONSTANTS['contig_lengths'] = np.array(value.split(",")).astype(int)
            case 'number of reads':             CONSTANTS['n_reads'] = int(value)
            case 'read_length':                 CONSTANTS['read_length'] = int(value)
            case 'insert length':               CONSTANTS['insert_length'] = int(value)
            case 'insert length variations':    CONSTANTS['insert_length_var'] = int(value)
            case 'skewed insert sizes':         CONSTANTS['skewed_insert_sizes'] = value.lower()
            case 'type of library':             CONSTANTS['library_type'] = value
            case 'methylation library':         CONSTANTS['methylated_genome'] = value.lower() == 'true'
            case 'percent methylation':         CONSTANTS['pct_methylation'] = float(value)
            case 'random seed':                 CONSTANTS['random_seed'] = int(value)
            case 'prefix':                      CONSTANTS['prefix']  = value
            case 'random (sequencing) mismatch error rate': CONSTANTS['random_mismatch_error_rate'] = float(value)
            case _: print(f"Unknown parameter: {key}")

    return CONSTANTS


def main():
    if len(argv) > 1:
        parameters_info_file = argv[1]
    else:
        parameters_info_file = "parameters.info"
        if not os.path.isfile(parameters_info_file):
            print(f"{parameters_info_file} not found. If you renamed it, add it as an argument: ./read_simulator parameters.file.info")
            sys.exit()

    CONSTANTS = read_parameters_file(parameters_info_file=sys.argv[1] if len(sys.argv) > 1 else "parameters.info")

    abs_path = os.path.realpath(parameters_info_file)
    stderr.write(f"parameters_file = {abs_path}\n")

    simulations_folder = CONSTANTS['prefix'] + "_simulations"
    os.makedirs(simulations_folder, exist_ok=True)


    if CONSTANTS['make_reference']:
        reference_file_path = 'simulated_reference_genome.fa'
        stderr.write(f"generating a new reference and saving it as {reference_file_path} \n")
        genome_dict = make_reference_genome(CONSTANTS=CONSTANTS) 

        # write to disk for reproducibility?
        g = '\n'.join( [">" + k + "\n" + v for k,v in genome_dict.items()] )
        with open(reference_file_path, 'w') as f:
            f.write( g )
    else:
        stderr.write(f"using {CONSTANTS['reference_fasta_path']} as the reference\n")
        genome_dict = load_reference_genome(CONSTANTS['reference_fasta_path'])

    # if libraries are bisulfite or EM-seq reads should contain conversions (r1:C->T & r2:G->A)
    #if CONSTANTS['methylated_genome'] == True:
    #    stderr.write("genome is treated as methylated - bisulfite/emseq converted\n")
    #    genome_dict = make_reference_bisulfite(genome_dict, pct_methylation=CONSTANTS['pct_methylation'], seed=CONSTANTS['random_seed'])

    # Variants can be simulated into the genome
    variants_list = read_proposed_variants('variants_proposed.tsv')
    variants_dict = assign_contigs_to_variants(variants_list, genome_dict, seed=CONSTANTS['random_seed'])

    # First generate reads where variants are allegedly present at the proper allele frequencies
    reads = generate_reads(
        genome_dict=genome_dict,
        variants_dict=variants_dict,
        CONSTANTS=CONSTANTS
        #base_noise_level=CONSTANTS['random_mismatch_error_rate']
    )
    stderr.write(f"reads generated from reference genome with variants \n")

    # Generate the positional pattern (of damage) that simulated reads should contain
    probs = generate_probabilities(CONSTANTS=CONSTANTS)
    # Include positional damage into the reads
    mutated_reads = mutate_reads(reads=reads, probabilities=probs, CONSTANTS=CONSTANTS)

    assert reads != mutated_reads, "HEY!!! reads and mutated reads are the same!!!"

    # Save reads containing variants and positional damage.
    reads_dict = print_reads(mutated_reads, CONSTANTS=CONSTANTS)
    stderr.write(f"fastq reads sved in simulation_folder \n")

    with open('simulated_reads_R1.fastq', 'w') as f:
        f.write(reads_dict[0])

    with open('simulated_reads_R2.fastq', 'w') as f:
        f.write(reads_dict[1])

if __name__ == "__main__":
    main()
