#! /bin/bash

# Put that in python
# Generate the similarity .csv files for each model based on:
# -> the Dataset-Muaz binaries
# -> the selected pairs file
# Creates the idbs (slow), preprocesses the data (medium), run the models (medium)

N_BB_MIN=$1
DESCRIPTION="$2"
LOG=./preproc.log

mkdir -p IDBs/Dataset-Muaz/
mkdir -p DBs/Dataset-Muaz/

CISCO_IDBS=$(realpath "IDBs/Dataset-Muaz/")
CISCO_DBS=$(realpath "DBs/Dataset-Muaz/")
CISCO_SCRIPTS=$(realpath "IDA_scripts/")

rm -r "$CISCO_IDBS"
rm -r "$CISCO_DBS"

mkdir -p $CISCO_DBS
mkdir -p $CISCO_IDBS

# preprocess the new binaries
cd $CISCO_SCRIPTS
echo "Generating IDBs from the binaries..."
echo "Generating IDBs from the binaries..." >> $LOG
if ! python3 generate_idbs.py --muaz; then # generates the IDBs
	echo "Error generate_idbs.py --muaz"
	echo "Error generate_idbs.py --muaz" >> $LOG
	exit 1
fi
if ! ./generate_acfg_feature_from_idbs.sh $N_BB_MIN $DESCRIPTION; then
	echo "Error generate_acfg_feature_from_idbs.sh"
	echo "Error generate_acfg_feature_from_idbs.sh" >> $LOG
	exit 1
fi
echo "Done"
