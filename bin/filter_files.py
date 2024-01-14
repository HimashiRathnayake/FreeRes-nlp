# Crystal Butler
# 2020/08/08
# Filter one directory of files based on the contents of another.
#
# This script is used to match the image and label files to dendrograms that pass
# the clustering test applied in cluster_synonymy_scores.py. It uses the names of
# files in the Dendrograms/Pass directory as a filter. The label and image files
# must have the same prefix as the dendrogram files for the script to work.
# Matching files are copied to the specified directory.

import os
import argparse
import shutil

# Read in options.
parser = argparse.ArgumentParser()
parser.add_argument('filter_dir', help='directory of files to be matched', type=str)
parser.add_argument('in_dir', help='directory of files to filter against filter_dir', type=str)
parser.add_argument('out_dir', help='directory that matching files are copied to', type=str)
args = parser.parse_args()


def make_output_subdirs():
    if not os.path.exists(args.in_dir):
        os.makedirs(args.in_dir)
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)


def create_filter_list():
    filter_list = []
    read_directory = os.fsencode(args.filter_dir)
    for file in os.listdir(read_directory):
        filename = os.fsdecode(file)
        if filename.startswith('.'):
            continue
        filter_name = filename.split(".")[0]
        try:
            filter_list.append(filter_name)
        except:
            print(f"Unable to append {filter_name} to filter list!")
    print(f"Found {len(filter_list)} file names to check.")
    return filter_list


def filter_files(filter_list, in_dir, out_dir):
    copy_list = []
    read_directory = os.fsencode(in_dir)
    for file in os.listdir(read_directory):
        filename = os.fsdecode(file)
        if filename.startswith('.'):
            continue
        check_name = filename.split(".")[0]
        if (check_name in filter_list):
            try:
                copy_list.append(filename)
                copy_file = os.path.join(in_dir, filename)
                shutil.copy2(copy_file, out_dir)
            except:
                print(f"Failed to copy {filename}.")
    print(f"Matched {len(copy_list)} files.")
    assert len(copy_list) == len(filter_list)


if __name__ == "__main__":
    make_output_subdirs()
    filter_list = create_filter_list()
    filter_files(filter_list, args.in_dir, args.out_dir)

