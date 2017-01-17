import pyltp
import argparse
import os

def ner():
    print "ner..."
    parser = argparse.ArgumentParser()
    parser.add_argument('-infile', type=str, dest="infile", required=True)
    parser.add_argument('-jamr_home', type=str, dest="jamr_home", required=True)
    args = parser.parse_args()

    jamr_home = args.jamr_home
    if jamr_home[-1] == "/":
        jamr_home = jamr_home[:-1]

    postagger = pyltp.Postagger()
    postagger.load(jamr_home + "/tools/ltp_data/pos.model")
    ner_recognizer = pyltp.NamedEntityRecognizer()
    ner_recognizer.load(jamr_home + '/tools/ltp_data/ner.model')

    infile_path = args.infile
    segfile_path = infile_path + ".tok"
    segfile = open(segfile_path)
    nerfile_path = infile_path + ".IllinoisNER"
    nerfile = open(nerfile_path, 'w')

    print "raw input file path:", infile_path
    print "seg file path:", segfile_path
    print "ner file path:", nerfile_path

    for sentence_words in segfile.readlines():
        sentence_words = sentence_words.split()
        postags = postagger.postag(sentence_words)

        ne_tags = ner_recognizer.recognize(sentence_words, postags)

        for word, ne_tag in zip(sentence_words, ne_tags):
            nerfile.write(word + '\t')
            if ne_tag == 'O':
                nerfile.write(ne_tag + '\n')
            else:
                ne_pos = ne_tag.split('-')[0]
                ne_type = ne_tag.split('-')[1]

                if ne_type == "Nh":
                    ne_type = "PER"
                elif ne_type == "Ns":
                    ne_type = "LOC"
                elif ne_type == "Ni":
                    ne_type = "ORG"

                if ne_pos == 'S' or ne_pos == 'B':
                    ne_pos = 'B'
                else:
                    ne_pos = 'I'

                nerfile.write(ne_pos + '-' + ne_type + '\n')
        nerfile.write('\n')

    nerfile.close()
    ner_recognizer.release()
    print "finish ner"
    return

ner()
