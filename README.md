JAMR-chinese - AMR Parser and Generator for Chinese
=================

JAMR-Chinese is based on [JAMR](https://github.com/jflanigan/jamr). Then framework and algorithms is totally the same as JAMR. The only difference is we provide a Chinese AMR annotation corpus and have a tained model for that, and you can parse Chinese sentences directly.

To make it available for Chinese, we replaced the tools for segmentation([pyltp](https://github.com/HIT-SCIR/pyltp/)), named entity recognization([pyltp](https://github.com/HIT-SCIR/pyltp/)), and dependency parsing([stanford parser](http://nlp.stanford.edu/software/lex-parser.shtml)). 

#Quick Start
Here we give a quick start to use JAMR-Chinese to perform  amr paring on a given Chinese sentence.

Download stanford parser and its model, and then put them in specific position:

1. Stanford Parser: http://nlp.stanford.edu/software/stanford-parser-full-2016-10-31.zip
	
	(Unzip it and move it into target/ folder)
2. Model for Chinese: http://nlp.stanford.edu/software/stanford-chinese-corenlp-2016-10-31-models.jar

	(Move this jar into target/stanford-parser-full-2016-10-31/model, then extract it's content using his command: $jar -xvf stanford-chinese-corenlp-2016-10-31-models.jar)


Run the following commands in your terminal:

	$pip install pyltp
	$git clone https://github.com/tanglrHello/nlpnju
	$cd nlpnju
	$./setup
	$./compile
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

	Tools for English segmentation and NER is not needed anymore, so you don't need to download them during setup stage.

JAMR is a semantic parser, generator, and aligner for the [Abstract Meaning Representation](http://amr.isi.edu/).
For more information about JAMR, please refer to [JAMR](https://github.com/jflanigan/jamr).


#Building

First checkout the github repository (or download the latest release):

    git clone https://github.com/tanglrHello/nlpnju

JAMR depends on [Scala](http://www.scala-lang.org), and [WordNet](http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz) for the
aligner. To download these dependencies into the subdirectory `tools`, cd to the `jamr` repository and run (requires
wget to be installed):

    ./setup

You should agree to the terms and conditions of the software dependencies before running this script.  If you download
them yourself, you will need to change the relevant environment variables in `scripts/config.sh`.  You may need to edit
the Java memory options in the script `sbt` and `build.sbt` if you get out of memory errors.

Besides, you need to install [pyltp](https://github.com/HIT-SCIR/pyltp/):
	
	$pip install pyltp

And you should download Stanford Parser and it's model for Chinese:

1. Stanford Parser: http://nlp.stanford.edu/software/stanford-parser-full-2016-10-31.zip
	
	(Unzip it and move it into target/ folder)
2. Model for Chinese: http://nlp.stanford.edu/software/stanford-chinese-corenlp-2016-10-31-models.jar

	(Move this jar into target/stanford-parser-full-2016-10-31/model, then extract it's content using his command: $jar -xvf stanford-chinese-corenlp-2016-10-31-models.jar)

Source the config script - you will need to do this before running any of the scripts below(config_my_chinese_little_princess.sh is prepared for Chinese parsing/training etc. There are also other config files in scripts/, which is from original JAMR. You can use them by downloading JAMR independently and use them there):

    . scripts/config_my_chinese_little_princess.sh
    or
    source script/config_my_chinese_little_princess.sh

Run `./compile` to build an uberjar, which will be output to
`target/scala-{scala_version}/jamr-assembly-{jamr_version}.jar` (the setup script does this for you).

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

