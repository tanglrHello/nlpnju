#!/bin/bash
set -ueo pipefail

if [ -z "$JAMR_HOME" ]; then
    echo 'Error: please source config script'
    exit 1
fi

pushd "$JAMR_HOME/scripts/preprocessing" > /dev/null
set -x

# Preprocess the data
./cmd.snt
#./cmd.snt.tok
#./cmd.tok

# Run the aligner
./cmd.aligned
# Remove opN
./cmd.aligned.no_opN
# Extract concept table
./cmd.aligned.concepts_no_opN

# Stanford Dependency Parser
./chn.cmd.snt.tok.deps

# Tag with IllinoisNer
./chn.cmd.snt.IllinoisNER


