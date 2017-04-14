#!/bin/bash
set -ueo pipefail

if [ -z "$JAMR_HOME" ]; then
    echo 'Error: please source config script'
    exit 1
fi

pushd "$JAMR_HOME/scripts/preprocessing" > /dev/null
set -x

# remove sentences without amr tagging
python remove_empty_tag_snts.py -trainf $TRAIN_FILE -devf $DEV_FILE -testf $TEST_FILE

# Preprocess the data
./cmd.snt
./cmd.snt.tok
./cmd.tok

# Run the aligner
if [ "$USE_GOLD_ALIGN" -ne 1 ]; then
    echo 'No gold alignment annotation, running automatic aligner...'
    ./cmd.aligned
else
    echo "extract alignment annotation from train file"
    python gold_aligned.py -gold_align_amr_file $TRAIN_FILE
    python gold_aligned.py -gold_align_amr_file $DEV_FILE
    python gold_aligned.py -gold_align_amr_file $TEST_FILE
fi


# Remove opN
./cmd.aligned.no_opN
# Extract concept table
./cmd.aligned.concepts_no_opN

# Stanford Dependency Parser
./chn.cmd.snt.tok.deps

# Tag with IllinoisNer
./chn.cmd.snt.IllinoisNER
