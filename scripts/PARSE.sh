#!/bin/bash
set -eo pipefail

# usage: ./PARSE.sh < input_file > output_file 2> output_file.err

if [ -z "$JAMR_HOME" ]; then
    echo 'Error: please source config script'
    exit 1
fi

if [ ! -f "${MODEL_DIR}/stage1-weights" ]; then
    echo "Error: cannot find weights file ${MODEL_DIR}/stage1-weights."
    echo "Please train JAMR or download and extract weights file to ${MODEL_DIR}"
    exit 1
fi

cat > /tmp/jamr-$$.snt

INPUT=/tmp/jamr-$$.snt

STAGE1_WEIGHTS="${MODEL_DIR}/stage1-weights"
STAGE2_WEIGHTS="${MODEL_DIR}/stage2-weights.iter5"

cd ${JAMR_HOME}/scripts/

#### Tokenize ####

echo ' ### Tokenizing input ###' >&2

python parsing/chn.seg.py -infile $INPUT -jamr_home ${JAMR_HOME} >&2


#### NER ####

echo ' ### Running NER system ###' >&2
python parsing/chn.ner.py -infile $INPUT -jamr_home ${JAMR_HOME} >&2

#### Dependencies ####

echo ' ### Running dependency parser ###' >&2
./parsing/chn.deps /tmp/jamr-$$  >&2

#### Parse ####

echo ' ### Running JAMR ###' >&2
${JAMR_HOME}/run AMRParser \
  --stage1-concept-table "${MODEL_DIR}/conceptTable.train" \
  --stage1-weights "${STAGE1_WEIGHTS}" \
  --stage2-weights "${STAGE2_WEIGHTS}" \
  --dependencies "${INPUT}.deps" \
  --ner "${INPUT}.IllinoisNER" \
  --tok "${INPUT}.tok" \
  -v 0 \
  ${PARSER_OPTIONS} \
  < "${INPUT}"

rm /tmp/jamr-$$.snt /tmp/jamr-$$.snt.tok /tmp/jamr-$$.snt.deps /tmp/jamr-$$.snt.IllinoisNER
