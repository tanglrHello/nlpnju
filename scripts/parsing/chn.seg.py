import pyltp
import argparse


def seg():
    print "seg..."
    parser = argparse.ArgumentParser()
    parser.add_argument('-infile', type=str, dest="infile", required=True)
    parser.add_argument('-jamr_home', type=str, dest="jamr_home", required=True)
    args = parser.parse_args()

    jamr_home = args.jamr_home
    if jamr_home[-1] == "/":
        jamr_home = jamr_home[:-1]

    segmentor = pyltp.Segmentor()
    segmentor.load(jamr_home + "/tools/ltp_data/cws.model")

    infile_path = args.infile
    infile = open(infile_path)
    outfile_path = infile_path + ".tok"
    outfile = open(outfile_path, "w")
    print "infile path:", infile_path

    for line in infile.readlines():
        if line.strip() == "":
            continue

        print "input:", line
        if ' ' in line.strip():
            words = line.strip().split()
        else:
            words = segmentor.segment(line.strip())
        outfile.write(" ".join(words) + '\n')

    segmentor.release()
    infile.close()
    outfile.close()
    print "finish segment"

seg()
