#!/usr/bin/python
'''
Script created by Gemma I. Martinez-Redondo based on script by Israel Barrios generate configuration files for GOPredSim
Usage:
        python generate_yml.py -s FILE_cdhit100.pep -p FILE_cdhit100_5k_removed.pep -o OUT_PATH -n PREFIX -m [cpu/gpu]
'''

#Import required modules
import argparse
import os

#YAML file contents for both models SeqVec and ProTT5
yml_template_embeddings_prott5_gpu="""global:
  sequences_file: {prott5_seq_file}
  prefix: {prefix}_prott5
{prefix}_prott5_embeddings:
  type: embed
  protocol: prottrans_t5_xl_u50
  model_directory: {gopredsim_path}/models/prottrans_t5_xl_u50
  half_precision_model: true
  device: cuda
  reduce: true
  discard_per_amino_acid_embeddings: true
"""

yml_template_embeddings_prott5_cpu="""global:
  sequences_file: {prott5_seq_file}
  prefix: {prefix}_prott5
{prefix}_prott5_embeddings:
  type: embed
  protocol: prottrans_t5_xl_u50
  model_directory: {gopredsim_path}/models/prottrans_t5_xl_u50
  reduce: true
  discard_per_amino_acid_embeddings: true
"""

yml_template_embeddings_seqvec_gpu="""global:
  sequences_file: {seqvec_seq_file}
  prefix: {prefix}_seqvec
{prefix}_seqvec_embeddings:
  type: embed
  protocol: seqvec
  weights_file: {gopredsim_path}/models/weights.hdf5
  options_file: {gopredsim_path}/models/options.json
  device: cuda
  reduce: True
  discard_per_amino_acid_embeddings: true
"""

yml_template_embeddings_seqvec_cpu="""global:
  sequences_file: {seqvec_seq_file}
  prefix: {prefix}_seqvec
{prefix}_seqvec_embeddings:
  type: embed
  protocol: seqvec
  weights_file: {gopredsim_path}/models/weights.hdf5
  options_file: {gopredsim_path}/models/options.json
  reduce: True
  discard_per_amino_acid_embeddings: true
"""

yml_template_gopredsim_prott5="""go: {gopredsim_path}/goPredSim/data/GO/go_2022.obo
lookup_set: {gopredsim_path}/goPredSim/data/prott5_goa_2022.h5
annotations: {gopredsim_path}/goPredSim/data/goa_annotations/goa_annotations_2022.txt
targets: {out_path}/{prefix}_prott5/{prefix}_prott5_embeddings/reduced_embeddings_file.h5
onto: all
thresh: 1
modus: num
output: {out_path}/{prefix}_prott5/gopredsim_{prefix}_prott5
"""

yml_template_gopredsim_seqvec="""go: {gopredsim_path}/goPredSim/data/GO/go_2022.obo
lookup_set: {gopredsim_path}/goPredSim/data/seqvec_fixed_lookup.h5
annotations: {gopredsim_path}/goPredSim/data/goa_annotations/goa_annotations_2022.txt
targets: {out_path}/{prefix}_seqvec/{prefix}_seqvec_embeddings/reduced_embeddings_file.h5
onto: all
thresh: 1
modus: num
output: {out_path}/{prefix}_seqvec/gopredsim_{prefix}_seqvec
"""

#Define parsing of the command
def parser():
    args = argparse.ArgumentParser(description='Generate Yaml files for using SeqVec and ProTT5 models in GOPredSim. At least one path to file to be annotated must be provided')
    args.add_argument('-s', '--seqvec', required=False, help="Path to the FASTA file that will be annotated using SeqVec.")
    args.add_argument('-p', '--prott5', required=False, help="Path to the FASTA file that will be annotated using ProTT5.")
    args.add_argument('-o', '--outpath', required=False, help="Path where output files from GOPredSim will be created. If not provided, current directory will be used.")
    args.add_argument('-n', '--name', required=True, help="Name to use as prefix to add to GOPredSim output folders.")
    args.add_argument('-g', '--gopredsim', required=True, help="Path to GOPredSim folder.")
    args.add_argument('-c', '--config', required=True, help="Path to configuration files.")
    args.add_argument('-m', '--mode', required=True, help="Specify if GOPredSim will be used using CPUs or GPUs.")
    args=args.parse_args()
    return args

#Obtain arguments and check their content
args=parser()

if not args.seqvec and not args.prott5:
    print("At least one file to be annotated must be provided")
    raise Exception

if args.seqvec and not os.path.exists(args.seqvec):
    print("Sequence file does not exist")
    raise Exception

if args.prott5 and not os.path.exists(args.prott5):
    print("Sequence file does not exist")
    raise Exception

if not args.name:
    print("Prefix name has not been specified")
    raise Exception

if not args.gopredsim:
    print("Path to GOPredSim folder has not been provided")
    raise Exception

if not args.config:
    print("Path to configuration files folder not provided")
    raise Exception

if not args.outpath:
    outpath=os.path()

if not args.mode:
    print("GPU or CPU-mode not specified")
    raise Exception

#Create configuration files if --seqvec was specified
if args.seqvec:
    if args.mode.lower()=="cpu":
        with open(args.config+"/embeddings/"+args.name+"_seqvec.yml","w") as yml_seqvec_embeddings:
            yml_seqvec_embeddings.write(yml_template_embeddings_seqvec_cpu.format(seqvec_seq_file=args.seqvec, prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))
    elif args.mode.lower()=="gpu":
        with open(args.config+"/embeddings/"+args.name+"_seqvec.yml","w") as yml_seqvec_embeddings:
            yml_seqvec_embeddings.write(yml_template_embeddings_seqvec_gpu.format(seqvec_seq_file=args.seqvec, prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))
    else:
        print("Mode not valid. Must be cpu or gpu")
        raise Exception
    with open(args.config+"/gopredsim/"+args.name+"_seqvec.yml","w") as yml_seqvec_gopredsim:
        yml_seqvec_gopredsim.write(yml_template_gopredsim_seqvec.format(prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))

#Create configuration files if --prott5 was specified
if args.prott5:
    if args.mode.lower()=="cpu":
        with open(args.config+"/embeddings/"+args.name+"_prott5.yml","w") as yml_prott5_embeddings:
            yml_prott5_embeddings.write(yml_template_embeddings_prott5_cpu.format(prott5_seq_file=args.prott5, prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))
    elif args.mode.lower()=="gpu":
        with open(args.config+"/embeddings/"+args.name+"_prott5.yml","w") as yml_prott5_embeddings:
            yml_prott5_embeddings.write(yml_template_embeddings_prott5_gpu.format(prott5_seq_file=args.prott5, prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))
    else:
        print("Mode not valid. Must be cpu or gpu")
        raise Exception
    with open(args.config+"/gopredsim/"+args.name+"_prott5.yml","w") as yml_prott5_gopredsim:
        yml_prott5_gopredsim.write(yml_template_gopredsim_prott5.format(prefix=args.name, gopredsim_path=args.gopredsim, out_path=args.outpath))
