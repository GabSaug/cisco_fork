OUT_DIR=$(realpath "$1")

LOG="./models.log"
CISCO_MODELS=$(realpath "Models/")
CISCO_RESULTS=$(realpath "Results/")
mkdir -p $CISCO_RESULTS/csv/
rm -r $CISCO_RESULTS/csv/*
mkdir -p $OUT_DIR
CWD=$(pwd)

cd $CISCO_MODELS/SAFE/
echo "Running SAFE test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/Asm2vec/
echo "Running asm2vec test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/GGSNN-GMN/
echo "Running gnn_opc test_script in $(pwd)" >> $LOG
if ! ./test_script.sh gnn_opc; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

echo "Running gmn test_script in $(pwd)" >> $LOG
if ! ./test_script.sh gmn_opc; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/Zeek/
echo "Running gnn test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/jTrans/
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate jtrans
echo "Running jTrans test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/HermesSim/
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate hermessim
echo "Running HermesSim test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG

cd $CISCO_MODELS/Trex/
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate kelpie
echo "Running Trex test_script in $(pwd)" >> $LOG
if ! ./test_script.sh; then
	echo "Error running test script, no Dataset testing results created"
	echo "Error running test script, no Dataset testing results created" >> $LOG
	notif error "$0 $*" finished
	exit 1
fi
echo "Done" >> $LOG


cd $CWD

# copy the resulting csvs
if ! cp $CISCO_RESULTS/csv/pairs_results_Dataset-Muaz_*.csv $OUT_DIR/; then
	echo "error copying result csvs"
	echo "error copying result csvs" >> $LOG
	exit 1
fi

echo "Done"
echo "Done" >> $LOG
