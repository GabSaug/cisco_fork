#!/bin/bash

# setup
# put all your IDA-extracted (with /IDA_scripts/generate_idbs.py) databases in /IDBs/Dataset-Muaz/
# create a Dbs/Dataset-Muaz folder
# create features and pairs folders
# $1: min number of bb per function
N_BB_MIN=$1
DESCRIPTION=$2
export IDA_PATH=$HOME/idapro-7.5/idat64
rm -r ../DBs/Dataset-Muaz
mkdir -p ../DBs/Dataset-Muaz
mkdir -p ../DBs/Dataset-Muaz/features
mkdir -p ../DBs/Dataset-Muaz/pairs

# flowchart (to select functions with at least 5 blocks)
## input: IDBs fodler
## output: csv file with selected functions data
echo "[*] Launching IDA_flowchart/cli_flowchart.py"
python3 IDA_flowchart/cli_flowchart.py -i ../IDBs/Dataset-Muaz -o ../DBs/Dataset-Muaz/features/flowchart_Dataset-Muaz.csv -s DBs_files_scripts/selected_pairs.csv

# select pairs and functions
## input: flowchart csv file
## output: testing_dataset.csv, features/selected_Dataset-Muaz.json, pairs/pairs_testing_Dataset-Muaz.csv
echo "[*] Launching dataset_creation_notebooks/Dataset-Muaz_creation.py"
python3 DBs_files_scripts/Dataset-Muaz_creation.py \
    "DBs_files_scripts/selected_pairs.csv" \
    "../DBs/Dataset-Muaz/features/flowchart_Dataset-Muaz.csv" \
    "../DBs/Dataset-Muaz/pairs/pairs_testing_Dataset-Muaz.csv" \
    "../DBs/Dataset-Muaz/features/selected_Dataset-Muaz.json" \
    "../DBs/Dataset-Muaz/testing_Dataset-Muaz.csv" \
    -n $N_BB_MIN \
    --description "$DESCRIPTION" \
    --name "Dataset-Muaz"

# compute acfg features
## input: selected_Dataset-Muaz.json
## output: features/acfg_disasm/acfg_disasm.json files
echo "[*] Launching IDA_acfg_disasm/cli_acfg_disasm.py"
python3 IDA_acfg_disasm/cli_acfg_disasm.py -j ../DBs/Dataset-Muaz/features/selected_Dataset-Muaz.json -o ../DBs/Dataset-Muaz/features/acfg_disasm
