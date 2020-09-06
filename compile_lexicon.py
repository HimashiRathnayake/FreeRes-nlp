# Crystal Butler
# 2020/08/28
# Combine passing dendrograms and statistics created by cluster_synonymy_scores,
# the top label and weight from sum_label_weights and AUs and weights
# from a spreadsheet to create a lexicon of facial expressions.

import os
import sys
import argparse
import time
import pandas as pd
# from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage, AnnotationBbox)
import matplotlib.cbook as cbook

DENDRO_EXT = ".png"
WEIGHTS_EXT = ".weights.txt"
IMAGE_EXT = ".jpg"

parser = argparse.ArgumentParser()
parser.add_argument('dendros_dir', help='full path to a directory containing dendrograms that passed the clustering test', type=str)
parser.add_argument('labels_weights_dir', help='full path to a directory containing summed labels weights', type=str)
parser.add_argument('images_dir', help='full path to a directory of facial expression images', type=str)
parser.add_argument('aus_weights', help='full path to a CSV file containing AUs and weights', type=str)
parser.add_argument('lexicon_dir', help='full path to a directory where lexicon pages will be written', type=str)
args = parser.parse_args()


def make_output_dir():
    if not os.path.exists(args.lexicon_dir):
        os.makedirs(args.lexicon_dir)


def make_input_lists():
    dendros_files = []
    labels_weights_files = []
    images_files = []
    for entry in sorted(os.listdir(args.dendros_dir)):
        if os.path.isfile(os.path.join(args.dendros_dir, entry)):
            if not entry.startswith('.'):
                dendros_files.append(os.path.join(args.dendros_dir, entry))
    for entry in sorted(os.listdir(args.labels_weights_dir)):
        if os.path.isfile(os.path.join(args.labels_weights_dir, entry)):
            if not entry.startswith('.'):
                labels_weights_files.append(os.path.join(args.labels_weights_dir, entry))
    for entry in sorted(os.listdir(args.images_dir)):
        if os.path.isfile(os.path.join(args.images_dir, entry)):
            if not entry.startswith('.'):
                images_files.append(os.path.join(args.images_dir, entry))
    if (len(dendros_files) < 1 or len(labels_weights_files) < 1 or len(images_files) < 1):
        print ("One of the input file lists is empty: quitting!")
        sys.exit()
    if (len(dendros_files) != len(labels_weights_files)):
        print("The dendrogram and label_weights file lists are not the same length: quitting!")
        sys.exit()
    return dendros_files, labels_weights_files, images_files


def get_csv_values():
    aus_weights_vals = pd.read_csv(args.aus_weights, dtype=str)
    index_column = aus_weights_vals.columns.values[0]
    # print(index_column)
    aus_weights_vals.set_index(index_column, inplace=True)
    return aus_weights_vals


def extract_image_names(dendros_files):
    image_names = []
    for file in dendros_files:
        file_name = os.path.basename(file)
        image_name = file_name.split('.')[0]
        image_names.append(image_name)
    assert len(dendros_files) == len(image_names), \
        "Dendros list has %r members and image name list has %r members!" % (len(dendros_files), len(image_names))
    return image_names


def find_dendros_file(image_name, dendros_files):
    for dendros_file in dendros_files:
        if (image_name + DENDRO_EXT) in os.path.basename(dendros_file):
            return dendros_file
    print(f'uh-oh, image {image_name} not found in dendros_files list!')


def find_labels_weights_file(image_name, labels_weights_files):
    for labels_weights_file in labels_weights_files:
        if (image_name + WEIGHTS_EXT) in os.path.basename(labels_weights_file):
            return labels_weights_file
    print(f'uh-oh, image {image_name} not found in labels_weights_files list!')


def get_labels_weights(labels_weights_file):
    with open(labels_weights_file, 'r') as f:
        labels_weights = []
        for line in f:
            stripped_line = line.strip()
            label, weight = stripped_line.split()
            weight = round(float(weight), 6)
            lw = [label, weight]
            labels_weights.append(lw)
        return labels_weights


def print_labels_weights(labels_weights):
    for lw in labels_weights:
        print(lw)


def find_images_file(image_name, images_files):
    for images_file in images_files:
        if (image_name + IMAGE_EXT) in os.path.basename(images_file):
            return images_file
    print(f'uh-oh, image {image_name} not found in images_files list!')


def get_image_record(image_name, aus_weights_vals):
    image_record = aus_weights_vals.loc[image_name]
    # image_record = pd.DataFrame(series).transpose()
    return image_record


def print_image_record(image_record):
    for i in range(len(image_record)):
        print('{:>10}'.format(image_record.index[i]), end='')
    print()
    for i in range(len(image_record)):
        print('{:>10}'.format(image_record.values[i]), end='')
    print('\n')


def plot_image(images_file):
    with cbook.get_sample_data(images_file) as image_file:
        image = plt.imread(image_file)
    fig, ax = plt.subplots()
    im = ax.imshow(image)
    ax.axis('off')
    plt.show(block=False)
    plt.pause(1)
    plt.close()


def print_label_weight(label, weight):
    print(f'Label: {label}')
    print(f'Weight: {weight}')


def format_image_text(weight, image_record):
    """Pretty print layout for the text of the lexicon plot."""
    image_text = '-------------------------------------------------\n\n'
    image_text += ('Label Similarity Score: ' + str(weight) + '\n\n')
    image_text += '-------------------------------------------------\n\n'
    image_text += 'Action Units and Weights\n\n'
    for i in range(0, len(image_record), 2):
        image_text += '%10s' % (str(image_record.index[i]))
        image_text += '%10s' % (str(image_record.index[i + 1]))
        image_text += '\n'
        image_text += '%10s' % (str(image_record.values[i]))
        image_text += '%10s' % (str(image_record.values[i + 1]))
        image_text += '\n'    
    image_text += '\n'
    image_text += '-------------------------------------------------\n'
    # image_text += tabulate(image_record, headers='keys', tablefmt='psql')
    return image_text

def format_labels_weights_text(labels_weights):
    """Pretty print layout for the text of the lexicon plot."""
    image_text = '-------------------------------------------------\n\n'
    image_text += ('Label Similarity Score: ' + str(weight) + '\n\n')
    image_text += '-------------------------------------------------\n\n'
    image_text += 'Action Units and Weights\n\n'
    for i in range(0, len(image_record), 2):
        image_text += '%10s' % (str(image_record.index[i]))
        image_text += '%10s' % (str(image_record.index[i + 1]))
        image_text += '\n'
        image_text += '%10s' % (str(image_record.values[i]))
        image_text += '%10s' % (str(image_record.values[i + 1]))
        image_text += '\n'    
    image_text += '\n'
    image_text += '-------------------------------------------------\n'
    # image_text += tabulate(image_record, headers='keys', tablefmt='psql')
    return image_text


def build_plot(label, dendros_file, images_file, image_text):
    # Set up the plot and subplots.
    fig = plt.figure(figsize=(8.5, 11))
    fig.tight_layout()
    # fig.suptitle("Image Label: " + label, fontsize=18, ha='left')
    # fig.subplots_adjust(bottom=0.1, left=0.025, top = 0.975, right=0.975)

    # Add facial expression image to a subplot.
    with cbook.get_sample_data(images_file) as image_file:
        image = plt.imread(image_file)
    sub1 = fig.add_subplot(2, 4, (1, 2))
    # fig.subplots_adjust(top=0.95)
    sub1.axis('off')
    plt.imshow(image)

    # Add image text to a subplot.
    sub2 = plt.subplot(2, 4, 3)
    fig.subplots_adjust(top=0.50)
    sub2.axis('off')
    sub2.text(0.1, 0.8,
            "Image Label: " + label, 
            fontsize=18,
            va='bottom',
            ha='left')
    sub2.text(0.1, 0.8,
            image_text,
            fontsize = 10,
            va='top',
            ha='left')

    # Add image text to a subplot.
    sub3 = plt.subplot(2, 4, 4)
    fig.subplots_adjust(top=0.50)
    sub3.axis('off')
    sub3.text(0.1, 0.8,
            "Image Label: " + label, 
            fontsize=18,
            va='bottom',
            ha='left')
    sub3.text(0.1, 0.8,
            image_text,
            fontsize = 10,
            va='top',
            ha='left')

    # # Add dendrogram to a subplot.
    with cbook.get_sample_data(dendros_file) as dendro_file:
        dendro = plt.imread(dendro_file)
    sub4 = fig.add_subplot(2, 4, (5, 8))
    sub4.axis('off')
    plt.imshow(dendro)
    
    plt.subplots_adjust(bottom=0.1, top=1.0, right=0.99, left=0.01, wspace=0, hspace=0)
    plt.show(block=False)
    plt.pause(1)
    plt.close()


def save_lexicon_entry(plot):
        #     # Save out the plot and statistics.
        #     dendro_file, stats_file = make_output_filenames(pct, dendro_name)
        #     with open(stats_file, 'w') as f_stat:
        #         f_stat.write(stats_printout)
        #     try:
        #         plt.savefig(dendro_file, format='png')
        #     except:
        #         print(f'Unable to save {dendro_file}!')
    plt.show(block=False)
    plt.pause(1)
    plt.close()


# def make_output_filenames(pct, dendro_name):
#     """Write statistics and dendrograms to Pass or Fail directories based on the clustering coherence test."""
#     if pct >= 75:
#         dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Pass/' + dendro_name + '.png')
#         stats_file = os.path.join(args.clustering_dir, 'Statistics/Pass/' + dendro_name + '.txt')
#     else:
#         dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Fail/' + dendro_name + '.png')
#         stats_file = os.path.join(args.clustering_dir, 'Statistics/Fail/' + dendro_name + '.txt')
#     return dendro_file, stats_file


if __name__ == '__main__':
    make_output_dir()
    if (os.path.isdir(args.dendros_dir) and os.path.isdir(args.labels_weights_dir) and os.path.isdir(args.images_dir) \
        and os.path.isfile(args.aus_weights)):
        """We are pulling dendrogram, summed label weight and synthetic facial expression
        image files and matching them with lines from a CSV file that documents the
        generative parameters for the expressions. Lexicon entries are created
        by iteratively compiling one entry from each source per entry."""
        dendros_files, labels_weights_files, images_files = make_input_lists()
        aus_weights_vals = get_csv_values()
        image_names = extract_image_names(dendros_files)
        for image_name in image_names:
            dendros_file = find_dendros_file(image_name, dendros_files)
            labels_weights_file = find_labels_weights_file(image_name, labels_weights_files)
            labels_weights = get_labels_weights(labels_weights_file)
            images_file = find_images_file(image_name, images_files)
            image_record = get_image_record(image_name, aus_weights_vals)
            image_text = format_image_text(labels_weights[0][1], image_record)
            # print(image_text)
            # build_plot(label, dendros_file, images_file, image_text)
            # print(tabulate(image_record, headers='keys', tablefmt='psql'))
            # print(image_record)
            # print_labels_weights(labels_weights)

    else:
        if (not os.path.isdir(args.dendros_dir)):
            print(f'Missing or incorrect argument for dendros_dir: tried {args.dendros_dir}.')
        elif (not os.path.isdir(args.labels_weights_dir)):
            print(f'Missing or incorrect argument for labels_weights_dir: tried {args.labels_weights_dir}.')
        elif (not os.path.isdir(args.images_dir)):
            print(f'Missing or incorrect argument for images_dir: tried {args.images_dir}.')
        elif (not os.path.isfile(args.aus_weights)):
            print(f'Missing or incorrect argument for aus_weights: tried {args.aus_weights}.')
        else:
            print("Be sure to include options for the dendrogram directory, labels and weights directory, \
images directory, AUs and weights file and output directory when calling this module.")