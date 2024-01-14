# FreeRes-nlp
A pipeline for analyzing single word free response label sets. More information can be found in the 2020 Intelligent Virtual Agents conference paper [here](https://www.crystal-butler.com/?p=1533).

## Contents of the repository
Most of the files in this repo are scripts that can be pipelined to analyze the semantics of a list of single word labels. The pipeline determine whether the terms in the
list are similar enough to represent a single semantic concept, and if a concept exists, calculates which word best represents the set semantics. 
At a high level, the scripts perform the following processes:
1. Compute relatedness scores between all pairs of labels in the set, using natural language processing (NLP)--specifically, cosine similarity of label word embeddings.
2. Cluster labels hierarchically based on their semantic proximity to other labels in the set, using an empirically determined clustering cutoff
to establish the number of clusters that can vary per label set.
3. Test for percentage membership in the largest cluster; sets with membership below a specified threshold are considered too disperse to represent
a single semantic concept.
4. For labels sets that pass the clustering test above, calculate which constituent label has the highest cumulative relatedness score and 
nominate it to be the set representative.

In addition to the core pipeline scripts, some scripts for data preprocessing, visualization and statistical analysis are included. Their use is optional, and will not be
described in detail here.

*Word Embeddings*
The word embeddings included in this repo can be used to calculate semantic similarity between labels. They were developed through extensive testing of a variety of 
off-the-shelf NLP models, with the best performing model fine-tuned using [retrofitting](https://www.cs.cmu.edu/~hovy/papers/15HLT-retrofitting-word-vectors.pdf) with a custom dictionary and thesaurus corpus (not provided here), then [counter-fit](https://www.aclweb.org/anthology/N16-1018.pdf). The resulting word embeddings outperformed all other models on a facial expression
label synonymy scoring task, and can be found in the word_embeddings directory.

*Synonymy Scoring Task*
This pipeline was developed to analyze sets of free response facial expression labels. To test the quality of word embeddings for this purpose, a curated benchmark 
test set of facial expression label pairs was scored for synonymy by crowdsourced human raters. The label pairs, averaged synonymy scores and benchmark vocabulary are included
in the synonyms_dataset directory. Word embeddings can model semantic relatedness, but are not specific enough to capture only the synonymy relationship between words, which
is required to determine whether labels relate to a central semantic concept. To assess the comparitive quality of word embeddings for capturing synonymy values, calculate
inter-rater reliability between the model and human raters with a test statistic such as 
[Krippendorff's alpha](https://repository.upenn.edu/cgi/viewcontent.cgi?article=1043&context=asc_papers#:~:text=Krippendorff's%20alpha%20(%CE%B1)%20is%20a,assign%20computable%20values%20to%20them.).

## Setup
The scripts in this repo were developed under Python 3.7.4. To set up a working Python environment in which to run them:
1. Install Python 3.7 by going to https://www.python.org/downloads/ and navigating to the latest version for your operating system.
2. Clone this repo (hosted at https://github.com/crystal-butler/FreeRes-nlp).
3. Create a Python 3.7 virtual environment within the top level of the FreeRes-nlp directory (see instructions here: https://docs.python.org/3.7/library/venv.html).
4. Activate the virtual environment, then install package dependencies by executing `pip install -r requirements`.

## How to pipeline the scripts
The Python scripts in this repository are set up to be run individually, in the sequence listed below. To see the required and optional arguments for each, 
including any default values, execute `python <script_name>.py --help`, substituting in the name of the file for <script_name>.
1. create_all_pairs.py: generate all pairs of single word labels from one or more lists
2. word_pair_distance.py: calculate the cosine similarity scores for one or more files of word pairs generted by create_all_pairs.py
3. cluster_synonymy_scores.py: cluster label sets based on relatedness scores from word_pair_distance.py, and test for cluster coherence
4. sum_label_weights.py: find the cumulative relatedness scores for all labels in one or more lists output by word_pair_distance.py

## Getting the word embeddings
The FreeRes-NLP word embeddings are stored in compressed format in the word_embeddings directory using [Git Large File Storage](https://git-lfs.github.com/). If you want to clone the repository and include the word embeddings, you will need to install git lfs--see info here on [versioning large files](https://docs.github.com/en/free-pro-team@latest/github/managing-large-files/versioning-large-files). Alternately, you can [download the file from GitHub directly](https://github.com/crystal-butler/FreeRes-nlp/raw/master/word_embeddings/FreeRes-NLP_word_embeddings.zip).

python create_all_pairs.py files/word_lists files/word_pairs
python word_pair_distance.py files/model2.vec --source_dir files/word_pairs --output_dir files/out
python cluster_synonymy_scores.py files/out/Score_Lists files/out/Label_Lists files/clustering