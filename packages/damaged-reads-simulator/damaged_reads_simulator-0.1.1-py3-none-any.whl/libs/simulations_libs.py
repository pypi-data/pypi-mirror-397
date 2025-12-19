#!/usr/bin/env python

from itertools import product
import numpy as np
import re
import sys, os
from scipy.stats import skewnorm
from fast_string_replace import replace_at_positions



'''
The idea is to load a mock reference genome (short. About 1000 lines total) and sample from there
read1 and read2 to generate:
    reads without mismatches from the reference.
    reads with a basal level of noise.
    reads with specific noise. For example, for FFPE, we will get reads where read2 has the 
    characteristic pattern of C->T and read1 G->A.
'''

def make_reference_genome(CONSTANTS):
    '''
    Makes a refernce genome.

    Args:
        included in CONSTANTS:
        GC_pct         (int) : GC percent across the entire genome 
        contig_lengths (list): length of each contig
        seed           (int) : random seed (for reproducibility)

    Returns:
        dict: Keys are contig names and values are the sequences.
    '''
    np.random.seed(CONSTANTS['random_seed'])
    nucleotides = ['A','T','C','G']
    total_num_nucleotides = np.sum(CONSTANTS['contig_lengths'])
    ATs = np.random.choice(['A','T'], int( (100-CONSTANTS['GC_pct']) / 100 * total_num_nucleotides) )
    GCs = np.random.choice(['G','C'], int(      CONSTANTS['GC_pct']  / 100  * total_num_nucleotides) )
    genome_sequence_arr = np.hstack([ATs, GCs])
    np.random.shuffle(genome_sequence_arr)
    contig_starts = np.append( 0, np.cumsum(CONSTANTS['contig_lengths']) )
    contig_start_end = zip(contig_starts[:-1], contig_starts[1:])
    reference = {f"contig{n}": ''.join( genome_sequence_arr[i[0]:i[1]] ) for n,i in enumerate( contig_start_end ) }
    
    return reference



def load_reference_genome(fasta):
    '''
    Load a reference file

    Args: 
        fasta (str): Path of the reference genome

    Returns:
        dict: Keys are contig names and values are the sequences.
    '''
    genome, sequence = {}, []

    with open(fasta, 'r') as f:
        for line in f:
            if line[0] == ">":

                if len(sequence) > 5: # skip very first header
                    genome[contig_name] = ''.join(sequence)

                contig_name = line[1:].strip()
                sequence = []

            else:
                sequence.append(line.strip())

    genome[contig_name] = ''.join(sequence)

    return genome


def bisulfite_conversion(sequence, CONSTANTS, read = 'R1'):
    '''
    Converts Cs to Ts, in the specified frequency, in the reference

    Args:
        sequence        (str) : reference sequence
        CONSTANTS       (dict): dictionary containing parameters including 'pct_methylation' and 'random_seed'
        read            (str) : 'R1' or 'R2' R1: C->T ; R2: G->A

    Returns:
        dict: reference with conversions rate as defined in the arguments
    '''
    np.random.seed(CONSTANTS['random_seed'])
    pct_converted = 100 - CONSTANTS['pct_methylation']  # e.g. 80% converted if 20% methylated
    
    if read == 'R1':
        CpGs = np.array([i.span()[0] for i in re.finditer("C", sequence)])
        new_nt = 'T'
    elif read == 'R2':
        CpGs = np.array([i.span()[0] for i in re.finditer("G", sequence)])
        new_nt = 'A'
    else:
        raise ValueError("read must be 'R1' or 'R2'")
        
    # randomly pick the pct_converted
    np.random.shuffle(CpGs)
    n = int( CpGs.shape[0] * pct_converted / 100 )

    methylation_dict = { int(i):new_nt for i in CpGs[:n] }
    
    bs_converted_sequence = replace_at_positions(sequence, methylation_dict)

    return bs_converted_sequence


def read_proposed_variants(vars_file):
    '''
    vars_file is a tab separated file (TSV) and NO HEADER
    each line in vars_file contains original_base, variant_base, frequency(%), strand
    e.g. C  T   10  +
         G  A   0.8 - (yes. 0.8%)
    
    Args:
        path to the file containing the variants

    Returns:
        list of dicts: Each dict specifies the variant for the relevant reference.
    '''
    with open(vars_file, 'r') as f:
        pre_vars = [i.strip().split("\t") for i in f]


    vars_list = [
        {
        'original':  i[0],
        'variant':   i[1],
        'frequency': float(i[2]),
        'strand':    i[3]
        }
        for i in pre_vars
    ]

    return vars_list


def complement(sequence):
        d = {'A': 'T', 'T':'A', 'C':'G', 'G':'C', 'N':'N'}
        return ''.join([d[i] for i in sequence])

def reverse_complement(sequence):
    return complement(sequence)[::-1]


def assign_contigs_to_variants(vars_list, genome_dict, seed=42):
    '''
    Instead of generating multiple references containing the variants at their estimated frequencies,
    we keep the original references but generate a dictionary for contig-positions containing the 
    variants and their frequencies are expressed as a list of 100 (this could change) options, 
    including the reference base-id and the variant base-id. This will be used downstream to generate
    the reads from "multiple genomes" where these variants should be found at their "known" frequences.
    The function starts by assigning variants to contigs randomly.

    Args: 
        vars_list (list): variants (loaded from the file) in dict format
        genome_dict (dict): reference; key=contig; values=sequences

    Returns:
        nested dictionaries
        kyes1   = contigs
        keys2   = positions
        values2 = list of characters containing 100 characters
                  e.g. for a G->T with allele frequency=0.1
                  [T,T,G,T,T,T,T,T,T,T...]
    '''
    np.random.seed(seed)

    n_vars = len(vars_list)
    n_contigs = len(genome_dict)

    contig_vars = np.random.randint(0, n_contigs, n_vars)

    variants_dict = { contig: {} for contig in genome_dict.keys() }

    for n, (contig, sequence) in enumerate(genome_dict.items()):
        idx_contig_vars = np.where(contig_vars == n)[0]
        
        for idx_contig_var in idx_contig_vars:
            var_dict = vars_list[idx_contig_var]
            strand = var_dict['strand']
            old_base = [var_dict['original'] if strand == "+" else reverse_complement(var_dict['original'])][0]
            new_base = [var_dict['variant'] if strand == "+" else reverse_complement(var_dict['variant'])][0]
            potential_positions_var = np.array( [i.span()[0] for i in  re.finditer(old_base, sequence)] )
            selected_position = potential_positions_var[ np.random.randint( len(potential_positions_var) ) ]
            floored_frequency = np.max( [var_dict['frequency'], 1] ).astype(int) # 1% is, for now, the lowest option.
            
            # variant and original with their frequencies in a arr[10] 
            variants_dict[contig][ selected_position ] = np.array( [old_base] * (100 - floored_frequency) + [new_base] * floored_frequency )
            np.random.shuffle( variants_dict[contig][ selected_position ] )

            # print(f"Assigned variant {var_dict['original']}->{var_dict['variant']} at contig {contig} position {selected_position} with frequency {var_dict['frequency']}%")
            # print(f"floored frequency: {floored_frequency}")
    
    # e.g. variant_dict['chr1'][1014365] = np.arr( ['G','G','T','G','G','T','T','G','G',....'T'] )
    return variants_dict


def generate_reads(genome_dict, variants_dict, CONSTANTS):
    '''
    Generate reads from references. Variants, at their specified frequencies, will be present in the reads.
    Systematic and random mismatches will be present. E.g. positional patterns suchas the C->T in FFPE can 
    be modeled in these reads with mutate_reads method by specifying the library_type.

    Args:
        genome_dict          (dict): reference. keys=contigs; values=sequences
        variants_dict        (dict): nested dict. k1=contig; k2=position; values=array with ref and var in proper 
                                      frequences
        CONTAINED IN CONSTANTS:
        n_reads               (int): Number of reads to design
        read_length           (int): Length of the read (# cycles in a Illumina type sequencing)
        insert_length         (int): Length of the fragment being sequenced.
        insert_length_var     (int): +/- (var) of insert_length form the distribution of inserts (mean=insert_legnth)
        base_noise_level    (float): Simulate errors from sequencing and library prep. (random noise)
        bidulphite_reference (dict): if provided, the bisulfite converted reference to sample from
        seed                  (int): random seed for reproducibility.

    Returns:
        Nested dict. k1=read number; k2=R1 or R2; values=read sequence
                     e.g. reads[14]['R1']="ATGTGTCCACAATGTCA..."
    '''

    np.random.seed(CONSTANTS['random_seed'])
    # insert length = WITHOUT adapter

    simulated_reads = []

    # Distribute the reads across contigs evenly, based on the length of each contig.
    contig_lengths = {name: len(seq) for name, seq in genome_dict.items()}
    total_length = np.sum([v for v in contig_lengths.values()])
    read_unit = CONSTANTS['n_reads'] / total_length

    contig_reads = {name: int(length * read_unit) for name, length in contig_lengths.items()}
    previous_n = 0

    # Generate reads for each contig.
    for contig_name, original_sequence in genome_dict.items():
        read_starts = np.random.randint(0, contig_lengths[contig_name] - CONSTANTS['insert_length'], contig_reads[contig_name])
        if CONSTANTS['skewed_insert_sizes'] == 'right':
            insert_lengths = skewnorm.rvs(a=4, loc=CONSTANTS['insert_length'], scale=CONSTANTS['insert_length_var'], size=contig_reads[contig_name]).astype(int)
        elif CONSTANTS['skewed_insert_sizes'] == 'left':
            insert_lengths = skewnorm.rvs(a=-3, loc=CONSTANTS['insert_length'], scale=CONSTANTS['insert_length_var'], size=contig_reads[contig_name]).astype(int)
        elif CONSTANTS['skewed_insert_sizes'] == 'none':
            insert_lengths = np.random.normal(CONSTANTS['insert_length'], CONSTANTS['insert_length_var'], contig_reads[contig_name]).astype(int)
        else:
            raise ValueError("skewed_insert_sizes must be 'right', 'left' or 'none'")

        # repeat the sampling N times (Ideally 100 but let's start with 10)
        # split array of starting positions in 10 (to make the sampling form "10 var-genomes" easier.
        read_starts_split = np.array_split(read_starts,10)
        insert_lengths_split = np.array_split(insert_lengths, 10)

        # 10 times, generate a "variant-genome" and sample from it.
        for var_index in range(10):
            contig_vars_input = { int(var_position): str(var_nt[var_index]) for var_position, var_nt in variants_dict[contig_name].items() }
            
            #### join variant and conversino dicts here ???

            sequence = replace_at_positions(original_sequence, contig_vars_input)
            sequence_R1 = bisulfite_conversion(sequence, CONSTANTS, read = 'R1')
            sequence_R2 = bisulfite_conversion(sequence, CONSTANTS, read = 'R2')

            # start (0) and end (1) of the insert seen from the FWD strand. 
            inserts_ends = np.vstack([ 
                read_starts_split[var_index], 
                read_starts_split[var_index] + insert_lengths_split[var_index]
            ]).T
            
            # randomly half of the reads will be: read1=rev and read2=fwd (and vice versa)
            # If Bisulphite, we need c->t conversions in the read1 and g->a in the read2
            n_reads_tmp = len(read_starts_split[var_index])
            idx = np.arange( n_reads_tmp ) 
            np.random.shuffle(idx)
            fr = idx[:n_reads_tmp//2]
            rf = idx[n_reads_tmp//2:]
            
            loop_fr = inserts_ends[fr]
            loop_rf = inserts_ends[rf]

            # filter out inserts that go beyond the contig limits
            loop_fr = loop_fr[ loop_fr[:,1] + CONSTANTS['read_length'] <= contig_lengths[contig_name] ]
            loop_rf = loop_rf[ loop_rf[:,1] + CONSTANTS['read_length'] <= contig_lengths[contig_name] ]

            # generate the reads. You can only see the ends of the fragments
            reads_fr = {
                n + previous_n: {
                    'R1' :             sequence_R1[i[0] : i[0]+CONSTANTS['read_length'] ].upper(), # left end
                    'R2' : complement( sequence_R1[i[1] : i[1]+CONSTANTS['read_length'] ].upper() )[::-1] # right end
                }
                for n,i in enumerate(loop_fr)
            }

            reads_rf = {
                n + previous_n: {
                    'R2' :             sequence_R2[i[0] : i[0]+CONSTANTS['read_length'] ].upper(), # right end
                    'R1' : complement( sequence_R2[i[1] : i[1]+CONSTANTS['read_length'] ].upper() )[::-1] # left end
                }
                for n,i in enumerate(loop_rf)
            }

            sys.stderr.write(f"fr reads: {len(fr)}\trf reads: {len(rf)}\n")
            new_reads = {**reads_fr, **reads_rf}
            simulated_reads.append(new_reads)

            previous_n += n_reads_tmp

    return {k:v for d in simulated_reads for k,v in d.items()}


def print_reads(reads, CONSTANTS):
    '''
    Print designed reads into fastq files.
    If needed, this can be adapted to different sequencing platforms, 
    barcodes, tails, and proper coordinates
    
    Args:
        reads (dict): nested dict. k1=read number; k2=R1 or R2; values=sequence.
        seed   (int): random seed for reproducibility.

    Returns:
        string. fastq files are strings ready to be written into a file.
    '''
    phreds = [ ''.join( ['A'] * 5 + ['E'] * ( len(reads[0]['R1']) - 5 ) ) ] * len(reads)
    tiles = np.sort( np.random.randint( 1,5, len(reads) ) )
    coords = np.random.randint( 100, 14000, (len(reads),3) )
    barcodes = "GTTCTGCA+GCTCCTTC"
    headers = [
        f"@NB552064:NB552064:H3CTYAFXC:{tile}:{coord[0]}:{coord[1]}:{coord[2]} 1:N:0:{barcodes}"
        for tile, coord in zip(tiles, coords)
    ]

    preads1 = '\n'.join( 
            [
                '\n'.join([ header, read['R1'], "+", phred[ :len(read['R1']) ] ]) 
                for header, read, phred in zip(headers, reads.values(), phreds)
            ] 
    ) 
    
    preads2 = '\n'.join( 
            [
                '\n'.join([ header, read['R2'], "+", phred[ :len(read['R2']) ] ]) 
                for header, read, phred in zip(headers, reads.values(), phreds)
            ] 
    ) 

    return preads1, preads2

def generate_probabilities(CONSTANTS):
    '''
    Generate mismatch patterns as the probabilities for each position in each read
    to have each of the 4 possible nucleotides in the read.

    Args:
        library_type (str): pattern of positional mutations (e.g. FFPE)
        read_length  (int): length of the read
        seed         (int): random seed for reproducibility.

    Returns:
        2 dictionaries for read1 and read2
        each dict has mismatches as keys (e.g. CT=C->T, GT, etc...)
        and values are numpy arrays with shape = (read_length, 1)
        and values indicating the probabilidad of each position to 
        make it into the library.
        E.g. a CT at position 3 in read 1, with a value of 0.8 will be adopted 
        (by other function) in the read, and the C will become T in 
        ~80% of the positions 3 from read 1.
    '''
    np.random.seed(CONSTANTS['random_seed'])

    bases = ['A','T','C','G']
    mismatches = [''.join(i) for i in product(bases, repeat=2) if i[1]!=i[0]]

    # generate random basal noise. If CONSTANTS['random_mismatch_error_rate'] specifies 0, there will be no noise.
    # Otherwise, all positions will have this basal level of noise. These are compared to random numbers to decide 
    # if a mismatch occurs at the mutation step.
    mean = CONSTANTS['random_mismatch_error_rate'] 
    std = mean # Not necessary to have mean=std.
    read1 = {
        mismatch: np.random.normal(mean, std, CONSTANTS['read_length']).clip(0,None)
        for mismatch in mismatches
    }
    read2 = read1.copy()

    if CONSTANTS['library_type'] == 'FFPE':

        # C to T in read 2
        # ---------------
        # the curve seems to comprise 2 distinct regions
        x1 = np.arange(1,12)
        x2 = np.arange(12,77)
        
        # with values within the following limits
        y1 = np.linspace(0.009, 0.004, len(x1)) 
        y2 = np.linspace(0.004,0.0015, len(x2))

        # data has some noise:
        var1 = 0.0004 # defined empirically, guided by data
        var2 = 0.0008
        noise1 = ( np.random.rand(len(y1)) - 0.5 ) * var1
        noise2 = ( np.random.rand(len(y2)) - 0.5 ) * var2

        # So combined all
        read2['CT'] = np.hstack([ y1 + noise1, y2 + noise2])
        
        # G to A in read 1
        # ----------------      
        # linear with a mild exponential increase
        x = np.arange(1,77)

        base = np.linspace(0.0013, 0.0015,len(x))
        expon = -1 * np.linspace(1.1,1.5, len(x))
        y = np.power(base, expon) / (base[-1]**expon[-1]) * 0.003

        # add a little noise
        var2 = 0.0008
        noise2 = ( np.random.rand(len(y)) - 0.5 ) * var2
        y += noise2  

        read1['GA'] = y
    


    elif CONSTANTS['library_type'] == 'sonication':
        pass
    else: # random noise only
        pass        

    sys.stderr.write(f"Generating positional probabilities for library type: {CONSTANTS['library_type']}\nRead1:\n")

    return read1, read2


def mutate_single_read(read, read_probs, random_probs):
    '''
    Mutate a single read based on positional probabilities
    of mismatches.
    
    Args:
        probs  (dict): keys: AT, GA, etc; values: probabilities
        read  (array): numpy (str) array of the sequence

    Returns:
        sting: The read including positional, systematic mismatches.
    '''
    #copilot benchmarked set operation slightly faster 
    #than numpy-indices AND operation for this type of 
    #cases
    new_read = str(read)
    for m,p in read_probs.items():
        # looking for positions where nt is X (for mutation XY)
        # and random robability of XY is high enough.
        base_position = set([i.span()[0] for i in re.finditer(m[0], read)])
        read_probs_complement = 1 - p
        prob_position = set( np.where(random_probs >= read_probs_complement)[0] )
        positions = base_position.intersection(prob_position)

        if len(positions) == 0: continue

        new_read = replace_at_positions( read, {int(i):m[1] for i in positions} )

    return new_read 


def mutate_reads(reads, probabilities, CONSTANTS):
    '''
    Applies mutate_single_read to any set of multiple reads.

    Args:
        reads         (dict): nested. k1=read number; k2=R1 or R2; values=sequences
        probabilities (dict): keys: AT, GA, etc; values: probabilities

    Returns:
        dict: nested. k1=read number; k2=R1 or R2; values=sequences (containing the 
        specified positional mismatches).
    '''

    simulated_reads= {}

    for n, read in enumerate(reads.values()):
        simulated_reads[n] = {
            'R1': mutate_single_read(read['R1'], probabilities[0], np.random.rand(CONSTANTS['read_length'])),
            'R2': mutate_single_read(read['R2'], probabilities[1], np.random.rand(CONSTANTS['read_length']))
        }
    return simulated_reads

