# Crystal Butler
# 2019/05/26
# Generate and save a vocabulary file for a given list of word-feature vectors.
# Vectors must contain the vocabulary word as the first element, followed by
# any number of space-separated feature values.
# The script will ignore all strings not comprised of lowercase English
# alphabet characters. To output all strings regardless of composition,
# change the main function to use the "make_vocab" function.

import argparse
import re

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('vectors_file', help="a file of word-feature vectors", type=str)
parser.add_argument('output_file', help="a file path for writing the vocabulary", type=str)
args = parser.parse_args()

# Constant, used to format output file name.
SUFFIX = ".txt"


def make_vocab():
    """Write out the first string from each line of the input file, regardless of composition."""
    vals = []
    with open(args.vectors_file, 'r', encoding="utf-8") as f, open(args.output_file, 'w', encoding="utf-8") as o:
        for line in f:
            vals = line.rstrip().split(' ')
            print(vals[0])
            o.write("{}\n".format(vals[0]))
        return 0


def make_vocab_lower_alphas():
    """Check the first string from each line of the input file, and if it contains 
    only lowercase English alphabet characters, write it out."""
    vals = []
    with open(args.vectors_file, 'r', encoding="latin-1") as f, open(args.output_file, 'w', encoding="latin-1") as o:
        for line in f:
            vals = line.rstrip().split(' ')
            if re.search(r'[^a-z]', vals[0]):
                continue
            else:
                o.write("{}\n".format(vals[0]))
        return 0

if __name__ == "__main__":
    vocab = make_vocab()
