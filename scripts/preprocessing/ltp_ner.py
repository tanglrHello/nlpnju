#coding=utf-8
import os
import pyltp
import argparse


def chn_ner_process():
    parser = argparse.ArgumentParser()
    parser.add_argument('-file', type=str, dest='amr_file_name', required=True)
    args = parser.parse_args()

    segged_sentences = get_words_from_deps_file(args.amr_file_name)
    ner_filename = args.amr_file_name + '.snt.IllinoisNER'
    ner(segged_sentences, ner_filename)


def get_words_from_deps_file(amr_file_path):
    deps_file_path = amr_file_path + '.snt.deps'
    deps_file = open(deps_file_path)

    sentences = []

    end_flag = False
    while True:
        words = []
        while True:
            line = deps_file.readline()
            if line == "":
                end_flag = True
                break

            if line.strip() == "":
                sentences.append(words)
                break

            line_fields = line.split("\t")
            word = line_fields[1]
            words.append(word)
        if end_flag:
            break

    return sentences


def ner(segged_sentences, ner_filename):
    postagger = pyltp.Postagger()
    postagger.load("../../target/ltp_data/pos.model")
    ner_recognizer = pyltp.NamedEntityRecognizer()
    ner_recognizer.load('../../target/ltp_data/ner.model')

    ner_file = open(ner_filename, 'w')

    for sentence_words in segged_sentences:
        #print " ".join(sentence_words),"%"
        postags = postagger.postag(sentence_words)
        #print list(postags),"&"
        ne_tags = ner_recognizer.recognize(sentence_words, postags)

        for word, ne_tag in zip(sentence_words, ne_tags):
            ner_file.write(word + '\t')
            if ne_tag == 'O':
                ner_file.write(ne_tag + '\n')
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

                ner_file.write(ne_pos + '-' + ne_type + '\n')
        ner_file.write('\n')

    ner_file.close()
    ner_recognizer.release()
    return

#words =["那 就 请 你们 帮 个 忙 ， 不 要 让 我 这么 忧伤 ： 赶快 写信 告诉 我 ， 他 又 回来 了 …".split(' ')]
#print words,"#"
#ner(words, 'ner.err')
chn_ner_process()