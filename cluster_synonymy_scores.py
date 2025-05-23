# Crystal Butler
# 2020/06/15
# Perform hierarchical agglomerative clustering on a set of single word labels,
# using the similarity scores output by word_pair_distance.py.
# Output includes a dendrogram for each input label set, statistics
# describing the set and a determination as to whether it passes or
# fails the clustering test for set coherence.

import os
import sys
import argparse
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('scores_dir', help='full path to a directory containing all pairs synonymy scores', type=str)
parser.add_argument('labels_dir', help='full path to a directory containing labels for all pairs synonymy scores',
                    type=str)
parser.add_argument('clustering_dir', help='full path to a directory where clustering output will be written', type=str)
parser.add_argument('--dendro_cutoff', help='the cutoff value for agglomerative hierarchical clustering',
                    default=0.7275, type=float)
args = parser.parse_args()


def make_input_lists():
    scores_files = []
    labels_files = []
    for entry in sorted(os.listdir(args.scores_dir)):
        if os.path.isfile(os.path.join(args.scores_dir, entry)):
            if not entry.startswith('.'):
                scores_files.append(entry)
    for entry in sorted(os.listdir(args.labels_dir)):
        if os.path.isfile(os.path.join(args.labels_dir, entry)):
            if not entry.startswith('.'):
                labels_files.append(entry)
    if (len(scores_files) < 1 or len(labels_files) < 1):
        print("Either scores or labels file list is empty: quitting!")
        sys.exit()
    if (len(scores_files) != len(labels_files)):
        print("The number of scores files doesn't match the number of labels files: quitting!")
        sys.exit()
    return scores_files, labels_files


def make_arrays(scores_path, labels_path):
    """Read scores and labels in from files. Convert them to ndarrays for clustering.
    Transform similarity (proximity) scores to distances."""
    pairs_scores = pd.read_csv(scores_path, header=None)
    labels = pd.read_csv(labels_path, header=None)
    scores_array = np.array(pairs_scores[0][:])
    scores_norm = normalize_array(scores_array)
    distances_array = 1 - scores_norm
    labels_array = np.array(labels[0][:])
    assert len(pairs_scores[0]) == len(
        distances_array), "Scores dataframe and distances array should be the same length."
    assert len(labels[0]) == len(labels_array), "Labels dataframe and labels array should be the same length."
    return distances_array, labels_array


def normalize_array(scores_array):
    scores_norm = (scores_array - np.min(scores_array)) / np.ptp(scores_array)
    scores_norm = scores_norm.round(decimals=6)  # clean up floating point errors and reduce significant digits
    return scores_norm


def check_expected_distances_count(labels_array):
    """The distances array should be a serialized upper triangular label x label matrix,
       with entries below the diagonal omitted."""
    expected_distances_count = int((len(labels_array) * (len(labels_array) - 1)) / 2)
    return expected_distances_count


def build_linkage_matrix(distances_array):
    """Create the linkage matrix Z (perform hierarchical/agglomerative clustering)."""
    linkage_matrix = sch.linkage(distances_array, 'average')
    # Fix distances that have become less than 0 due to floating point errors.
    for i in range(len(linkage_matrix)):
        if linkage_matrix[i][2] < 0:
            linkage_matrix[i][2] = 0
    return linkage_matrix


def extract_dendro_name(labels_file, scores_file):
    labels_name = os.path.basename(labels_file)
    scores_name = os.path.basename(scores_file)
    labels_prefix = labels_name.split('.')[0] # (hrat069) changed _ to .
    scores_prefix = scores_name.split('.')[0] # (hrat069) changed _ to .
    assert labels_prefix == scores_prefix, "Labels and scores should have the same file name prefix."
    return labels_prefix


def calculate_cluster_stats(linkage_matrix, distances_array):
    """Calculate clustering statistics for cophenetic coefficient correlation,
    the number of clusters, the count of labels per cluster and the
    percent membershp in the largest cluster."""
    clusters = sch.fcluster(linkage_matrix, args.dendro_cutoff, criterion='distance')
    cluster_enumeration = np.unique(clusters)
    # Calculate the cophenetic correlation coefficient statistic: closer to 1 is better.
    cophenetic_coefficient, _ = sch.cophenet(linkage_matrix, distances_array)
    # Get membership counts for each cluster.
    cluster_membership = {}
    for value in cluster_enumeration:
        member_count = np.count_nonzero(clusters == value)
        cluster_membership[value] = member_count
    # Calculate the percentage membership in the largest cluster.
    c_max = max(cluster_membership.values())
    c_sum = sum(cluster_membership.values())
    pct = 100 * (c_max / c_sum)
    return cophenetic_coefficient, cluster_membership, pct


def make_output_subdirs():
    if not os.path.exists(args.clustering_dir):
        os.makedirs(args.clustering_dir)
    if not os.path.exists(os.path.join(args.clustering_dir, 'Dendrograms/Pass')):
        os.makedirs(os.path.join(args.clustering_dir, 'Dendrograms/Pass'))
    if not os.path.exists(os.path.join(args.clustering_dir, 'Dendrograms/Fail')):
        os.makedirs(os.path.join(args.clustering_dir, 'Dendrograms/Fail'))
    if not os.path.exists(os.path.join(args.clustering_dir, 'Statistics/Pass')):
        os.makedirs(os.path.join(args.clustering_dir, 'Statistics/Pass'))
    if not os.path.exists(os.path.join(args.clustering_dir, 'Statistics/Fail')):
        os.makedirs(os.path.join(args.clustering_dir, 'Statistics/Fail'))


def format_cluster_stats(cophenetic_coefficient, cluster_membership, pct):
    """Pretty print layout for clustering statistics; can be appended to the dendrogram or saved out as a file."""
    stats_printout = '---------------------------------------------------------------------------------\n'
    stats_printout += 'Agglomerative Hierarchical Clustering Statistics\n---------------------------------------------------------------------------------\n'
    stats_printout += ('Cophenectic correlation coefficient: ' + str(cophenetic_coefficient) + '\n')
    stats_printout += ('Cluster: Count\n')
    for key in cluster_membership.keys():
        stats_printout += (str(key) + ': ' + str(cluster_membership[key]) + '\n')
    cluster_max_membership = max(cluster_membership.items(), key=lambda x: x[1])
    stats_printout += ('Cluster ' + str(cluster_max_membership[0]) + ' with ' + str(
        cluster_max_membership[1]) + ' members has ' + str(pct) + '% of the membership.\n')
    pass_fail = classify_pass_fail(pct)
    stats_printout += ('Cluster coherence test: ' + pass_fail)
    return stats_printout


def classify_pass_fail(pct):
    """The clustering coherence test is based on membership percentage in the largest cluster."""
    pass_fail = 'pass' if pct >= 75 else 'fail'
    return pass_fail


def make_output_filenames(pct, dendro_name):
    """Write statistics and dendrograms to Pass or Fail directories based on the clustering coherence test."""
    if pct >= 66:
        dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Pass/' + dendro_name + '.png')
        stats_file = os.path.join(args.clustering_dir, 'Statistics/Pass/' + dendro_name + '.txt')
    else:
        dendro_file = os.path.join(args.clustering_dir, 'Dendrograms/Fail/' + dendro_name + '.png')
        stats_file = os.path.join(args.clustering_dir, 'Statistics/Fail/' + dendro_name + '.txt')
    return dendro_file, stats_file


if __name__ == '__main__':
    make_output_subdirs()
    if (os.path.isdir(args.scores_dir) and os.path.isdir(args.labels_dir) and os.path.isdir(args.clustering_dir)):
        """We are reading from one or more files containing word pair synonymy scores
        and their associated labels, clustering the distances between scores,
        generating a dendrogram and some statistics from the clustering, and writing
        that output to a file."""
        scores_files, labels_files = make_input_lists()
        for i in range(len(scores_files)):
            scores_file = os.path.join(args.scores_dir, scores_files[i])
            labels_file = os.path.join(args.labels_dir, labels_files[i])
            distances_array, labels_array = make_arrays(scores_file, labels_file)
            expected_distances_count = check_expected_distances_count(labels_array)
            if (expected_distances_count != len(distances_array)):
                print(
                    f'The number of values in the {scores_file} distances list is {len(distances_array)}, but it should be {expected_distances_count}.')
                input("Press Enter to continue...")
                continue

            linkage_matrix = build_linkage_matrix(distances_array)
            assert (linkage_matrix.shape[0] + 1) == (
                len(labels_array)), "The linkage matrix and labels array have mismatched lengths."
            cophenetic_coefficient, cluster_membership, pct = calculate_cluster_stats(linkage_matrix, distances_array)
            stats_printout = format_cluster_stats(cophenetic_coefficient, cluster_membership, pct)

            # Title the dendrogram, using the labels file name.
            dendro_name = extract_dendro_name(labels_file, scores_file)
            # Set up the plot.
            fig, ax = plt.subplots(figsize=(14, 8.5))  # (width, height) in inches
            title = "Image: " + dendro_name
            plt.title(title, fontsize=18)
            plt.rc('ytick', labelsize=14)
            y_label = 'Cophenetic Coefficient (Cutoff: ' + str(args.dendro_cutoff) + ')'
            plt.ylabel(y_label, fontsize=16)
            plt.axhline(y=args.dendro_cutoff, color="grey", linestyle="--")
            # plt.figtext(0.02, 0.12, stats_printout, horizontalalignment='left', verticalalignment='center', fontsize=14)
            plt.subplots_adjust(bottom=0.22, top=0.95, right=0.98, left=0.06)
            # Create the dendrogram, with a cutoff specified during module invocation.
            dendro = sch.dendrogram(linkage_matrix, labels=labels_array, color_threshold=args.dendro_cutoff, \
                                    leaf_font_size=8, leaf_rotation=90, count_sort='ascending', ax=ax, above_threshold_color='lightgray')
            ax.set_ylim(0, 1)

            # Save out the plot and statistics.
            dendro_file, stats_file = make_output_filenames(pct, dendro_name)
            with open(stats_file, 'w') as f_stat:
                f_stat.write(stats_printout)
            try:
                plt.savefig(dendro_file, format='png')
            except:
                print(f'Unable to save {dendro_file}!')
            # plt.show()  # uncomment to display the plot before continuing
            plt.close()

    else:
        print("Be sure to include options for scores, labels and output directories when calling this module.")