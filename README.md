JAMR-chinese - AMR Parser and Generator for Chinese
=================

JAMR-Chinese is based on [JAMR](https://github.com/jflanigan/jamr). Then framework and algorithms is totally the same as JAMR. The only difference is we provide a Chinese AMR annotation corpus and have a tained model for that, and you can parse Chinese sentences directly.

To make it available for Chinese, we replaced the tools for segmentation([pyltp](https://github.com/HIT-SCIR/pyltp/)), named entity recognization([pyltp](https://github.com/HIT-SCIR/pyltp/)), and dependency parsing([stanford parser](http://nlp.stanford.edu/software/lex-parser.shtml)). 

#Quick Start
Here we give a quick start to use JAMR-Chinese to perform  amr paring on a given Chinese sentence.

Run the following commands in your terminal:

	$git clone https://github.com/tanglrHello/nlpnju
	$cd nlpnju
	$./setup

Now you need to download the model files for pyltp (ltp-data-v3.3.1.zip) manually from this [url](https://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569#list/path=%2Fltp-models%2F3.3.1). Then unzip the .zip file, and move it into $JAMR_HOME/tools/.

Continue executing the following commands:
	
	$. script/config_my_chinese_little_princess.sh
	(prepare a chn_test.txt file in the root path for JAMR-Chinese)
	$./script/PARSE.sh < chn_test.txt > chn_test.out 2> chn_test.err
	(Then you can see the amr parsing result in chn_test.out)

More detailed information can be found below.



#The difference between this project and [JAMR](https://github.com/jflanigan/jamr) 
1. Config File

	script/config_my_chinese_little_princess.sh: this is a config file for [the Chinese AMR annotation corpus](http://www.cs.brandeis.edu/~clp/camr/camr.html). It indicates the file path of training/dev/test files and the path to save trained model.
	
2. Data and Model

	1) data/chinese_little_princess_annotation/: contains train/dev/test AMR file for Chinese

	2) model/my_chinese_little_princess/: contains the model trained from data/chinese_little_princess_annotation
	

3. Preprocessing Stage

	1) script/preprocessing/PREPROESS.sh: run newly created bash files(mentioned in 2/3) to do NER and denpendency parsing, instead of those bashes for English.
	
	2) script/preprocessing/chn.cmd.snt.IllinoisNER: do Chinese NER using [pyltp](https://github.com/HIT-SCIR/pyltp/) in preprocess stage.
	
	3) script/preprocessing/chn.cmd.snt.tok.deps: do Chinese dependency parsing using [stanford parser](http://nlp.stanford.edu/software/lex-parser.shtml) in preprocess stage.
	
	4) script/preprocessing/transform_dep_format.py: called by chn.cmd.snt.tok.deps, which is used to generate CONLL format dependency parsing from the output of stanford parser.

3. Parsing Stage

	1) script/PARSE.sh: run newly created bash files(mentioned in 6/7/8 below) to do Chinese segmentation, NER and dependency parsing, instead of those bashes for English.
	
	2) script/training/chn.seg.py: do Chinese segmentation using [pyltp](https://github.com/HIT-SCIR/pyltp/) in parsing stage.

	3) script/training/chn.ner.py: do Chinese NER using [pyltp](https://github.com/HIT-SCIR/pyltp/) in parsing stage.
	
	4) script/training/chn.deps: do Chinese dependency parsing using [stanford parser](http://nlp.stanford.edu/software/lex-parser.shtml) in parsing stage.

5. Setup Stage

	Tools for English segmentation and NER is not needed anymore, so you don't need to download them during setup stage. But pyltp and stanford parser will be downloaded by setup.

JAMR is a semantic parser, generator, and aligner for the [Abstract Meaning Representation](http://amr.isi.edu/).
For more information about JAMR, please refer to [JAMR](https://github.com/jflanigan/jamr).


#Building

First checkout the github repository (or download the latest release):

    git clone https://github.com/tanglrHello/nlpnju

JAMR-chinese depends on cdec, [Scala](http://www.scala-lang.org),  [WordNet](http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz), [pyltp](https://github.com/HIT-SCIR/pyltp/) and [stanford parser](http://nlp.stanford.edu/software/lex-parser.shtml). To download these dependencies, cd to the `jamr` repository and run (requires wget to be installed):

    ./setup

This bash will install python package pyltp for you, so you may need to use sudo to execute it.

Besides, you need to download models for ltp (ltp-data-v3.3.1.zip) from this [url](https://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569#list/path=%2Fltp-models%2F3.3.1). Move the model into target/, unzip it, and rename the resulting fold to 'ltp_data'. There should  several .model files in target/ltp_data/.


You will need to source the config script before running any of the scripts below (config_my_chinese_little_princess.sh is prepared for Chinese parsing/training):

    . scripts/config_my_chinese_little_princess.sh
    or
    source script/config_my_chinese_little_princess.sh

There are also other config files in scripts/, which is from original JAMR. You can use them by downloading JAMR independently and use them there)


#Running the Parser

To parse a file (untokenized or tokenized, with one Chinese sentence per line) with the model trained on data do:

    . scripts/config_my_chinese_little_princess.sh
    scripts/PARSE.sh < input_file > output_file 2> output_file.err

The output is AMR format, with some extra fields described in [docs/Nodes and Edges
Format](docs/Nodes_and_Edges_Format.md) and [docs/Alignment Format](docs/Alignment_Format.md). 

#Running the Aligner

To run the rule-based aligner:

    . scripts/config.sh
    scripts/ALIGN.sh < amr_input_file > output_file

The output of the aligner is described in [docs/Alignment Format](docs/Alignment_Format.md).  Currently the aligner
works best for release r3 data (AMR Specification v1.0), but it will run on newer data as well.


#Training the Parser

The following describes how to train and evaluate the parser.  There are scripts to train the parser on various
datasets, as well as a general train script to train the parser on any AMR dataset. We use the general train script here. We illustrate the process for training use chinese_littile_princess as example, which is already existing in the project. If you have other Chinese AMR annotation corpus, you can train it similarly.

Attention, JAMR-Chinese is only available for Chinese corpus, and can't process any non-Chinese corpus.

To train the parser on amr data, download the annotation files
into to `$JAMR_HOME/data/`. There should be a train file, a dev file, and a test file respectively.

The trained model will go into a subdirectory of `models/` (we configured this path in config_my_chinese_little_princess.sh) and the evaulation results will be printed and saved to
`models/my_chinese_little_princess/RESULTS.txt`. 

To train the parser on your dataset, create a [config file](docs/Config_File.md) in `scripts/`, and set the file path to train/dev/test file and model. And
then do:

    . scripts/config_my_chinese_little_princess.sh
    scripts/TRAIN.sh

The trained model will be saved into the `$MODEL_DIR` specified in the config script, and the results saved in
`$MODEL_DIR/RESULTS.txt` To run the parser with your trained model, remember source `config_my_chinese_little_princess.sh` before running
`PARSE.sh`.

## Evaluating

To evaluate a trained model against a gold standard AMR file, do:

    . scripts/config_my_chinese_little_princess.sh
    scripts/EVAL.sh gold_amr_file

The predicted output will be in `models/my_chinese_little_princess/gold_amr_file.parsed-gold-concepts` for the parser with oracle
concept ID, `models/my_chinese_little_princess/gold_amr_file.parsed` for the full pipeline, and the results saved in
`models/my_chinese_little_princess/gold_amr_file.results`.

