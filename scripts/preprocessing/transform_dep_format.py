#coding=utf-8
import argparse
import os


def transform():
    parser = argparse.ArgumentParser()
    # old file will be replaced by new file with the same name
    parser.add_argument('-file', type=str, dest='file_name', required=True)
    parser.add_argument("-outfile", type=str, dest ='outfile', required=False, default=None)
    args = parser.parse_args()

    penn_file_path = args.file_name + '.snt.penn'
    dep_file_path = args.file_name + '.snt.dep'
    penn_file = open(penn_file_path, 'a')
    dep_file = open(dep_file_path, 'a')
    penn_file.write('\n')
    dep_file.write('\n')
    penn_file.close()
    dep_file.close()
    penn_file = open(penn_file_path)
    dep_file = open(dep_file_path)
    print "penn file path:", penn_file_path
    print "dep file path:", dep_file_path

    if args.outfile == None:
        out_file = open(args.file_name + '.snt.deps', 'w')
    else:
        out_file = open(args.outfile, 'w')

    while True:
        # read a sentence from penn
        edges = []
        end_flag = False
        while True:
            line = dep_file.readline()
            if line == '':
                end_flag = True
                break

            if line.strip() == '':
                break
            else:
                edges.append(extract_info_from_dep_line(line))

        # read a sentence from dep
        word_pos = []
        while True:
            line = penn_file.readline()
            if line.strip() == '':
                break
            else:
                word_pos += extract_info_from_penn_line(line)

        if end_flag:
            break

        # construct conll from above info
        lines = construct_conll(edges, word_pos)
        if lines == []:
            continue

        for line in lines:
            out_file.write(line + '\n')
        out_file.write('\n')




    penn_file.close()
    dep_file.close()
    out_file.close()
    #os.remove(penn_file_path)
    #os.remove(dep_file_path)


def extract_info_from_dep_line(line):
    rel = line.split('(')[0].strip()
    nodes = line.split('(')[1].split(')')[0].strip().split(',')
    node1 = nodes[0].strip()
    node2 = nodes[1].strip()
    return rel, node1, node2


def extract_info_from_penn_line(line):
    word_pos = []
    last_bracket_type = "("
    last_bracket_index = -1
    for cindex, char in enumerate(line):
        if char == '(':
            last_bracket_type = 'left'
            last_bracket_index = cindex
        elif char == ')':
            if last_bracket_type == 'left':
                this_word_pos = line[last_bracket_index+1:cindex].strip()
                word_and_pos = this_word_pos.split()
                assert len(word_and_pos) == 2
                word_pos.append(tuple(word_and_pos))

            last_bracket_type = 'right'
            last_bracket_index = cindex
    return word_pos


def construct_conll(edges, word_pos):
    conll_lines = []

    index = 1
    for edge in edges:
        rel = edge[0]
        parent = edge[1].split('-')[0]
        parent_index = edge[1].split('-')[1]
        child = edge[2].split('-')[0]
        child_index = edge[2].split('-')[1]


        fields = []
        fields.append(str(index))
        fields.append(child)
        fields.append('_')
        fields.append(word_pos[int(child_index) - 1][0])
        fields.append(word_pos[int(child_index) - 1][0])
        fields.append('_')
        fields.append(parent_index)
        fields.append(rel)
        fields.append('_')
        fields.append('_')

        new_line = '\t'.join(fields)
        conll_lines.append(new_line)
        index += 1

    return conll_lines


# print extract_info_from_dep_line(u"rcomp(了解-3, 到-4)\n")
# print extract_info_from_penn_line(u"          (VRD (VV 了解) (VV 到))\n")
transform()
