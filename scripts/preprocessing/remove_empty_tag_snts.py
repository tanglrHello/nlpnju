#coding=utf-8
import argparse
import os


def remove():
    parser = argparse.ArgumentParser()
    # old file will be replaced by new file with the same name
    parser.add_argument('-trainf', type=str, dest='train_filepath', required=True, default=None)
    parser.add_argument("-devf", type=str, dest ='dev_filepath', required=True, default=None)
    parser.add_argument("-testf", type=str, dest='test_filepath', required=True, default=None)

    args = parser.parse_args()
    file_paths = [args.train_filepath, args.dev_filepath, args.test_filepath]

    original_files = []
    new_files = []
    for f_path in file_paths:
        original_files.append(open(f_path))
        new_files.append(open(f_path + ".new", "w"))

    for i in range(3):
        print file_paths[i], "removing..."
        remove_sentences(original_files[i], new_files[i])

    for file in original_files + new_files:
        file.close()

    # replace file
    for f_path in file_paths:
        os.remove(f_path)
        os.rename(f_path + ".new", f_path)


def remove_sentences(original_file, new_file):
    snt_info = []
    first_snt = True
    for line in original_file.readlines():
        if line.startswith("# ::id") and not first_snt:
            write_snt(snt_info, new_file)
            snt_info = []

        first_snt = False

        if line.strip() != "":
            snt_info.append(line)

    write_snt(snt_info, new_file)



def write_snt(snt_info, destfile, min_length=0, max_length=2000):
    # ignore sentences without AMR tagging
    if len(snt_info) == 2 and snt_info[0].startswith("# ::id") and snt_info[1].startswith("# ::snt"):
        return
    else:
        for line in snt_info:
            destfile.write(line)
        destfile.write("\n")


    # filter sentences by its length
    sentence_toks = snt_info[0].split()[1:]


remove()