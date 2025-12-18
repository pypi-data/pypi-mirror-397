"""
Dataset utility functions for machine learning workflows.

This module provides utility functions for splitting and organizing datasets
for machine learning experiments, including random splitting and k-fold
cross-validation setup.
"""

import math
import random

import numpy as np
import rasterio


def random_split(id_list, counts_list, relative=False) -> list:
    """
    Randomly split a list of IDs into multiple subsets.

    This function splits a list of identifiers into multiple subsets according
    to specified counts. Useful for creating train/validation/test splits.

    Args:
        id_list (list): List of identifiers to split.
        counts_list (list): List of counts for each split. If relative=True,
            these are interpreted as proportions; otherwise as absolute counts.
        relative (bool, optional): If True, counts_list values are proportions
            of the total. If False, they are absolute counts. Defaults to False.

    Returns:
        list: List of lists, where each sublist contains IDs for one split.

    Raises:
        Exception: If the requested number of samples exceeds the list length.

    Examples:
        >>> ids = list(range(100))
        >>> train, val, test = random_split(ids, [0.7, 0.15, 0.15], relative=True)
        >>> # or with absolute counts:
        >>> train, val = random_split(ids, [80, 20], relative=False)
    """
    n_el = len(id_list)
    ids = id_list.copy()
    counts = counts_list

    if relative:
        counts = list(map(lambda x: round(x*n_el), counts))

    random.shuffle(ids)
    sums = np.cumsum(counts)
    sums = np.insert(sums, 0, 0)

    if sums[-1] > n_el:
        raise Exception("number of sample requested higher than list length")

    split = []
    for i in range(1, len(sums)):
        start = sums[i-1]
        end = sums[i]
        split.append(ids[start:end])

    return split


def k_fold_sample(id_list, n_fold):
    """
    Create k-fold cross-validation splits from a list of IDs.

    This function creates n_fold partitions of the data and generates fold
    definitions for k-fold cross-validation, where each fold is used once
    as validation while the remaining folds are used for training.

    Args:
        id_list (list): List of sample identifiers to split.
        n_fold (int): Number of folds to create.

    Returns:
        tuple: A tuple containing:
            - folds (list): List of n_fold lists, each containing sample IDs for that fold.
            - fold_id (list): List of tuples defining train/validation splits, where each
              tuple contains ([training_fold_indices], [validation_fold_index]).

    Examples:
        >>> ids = list(range(100))
        >>> folds, fold_splits = k_fold_sample(ids, n_fold=5)
        >>> # folds[0] contains ~20 samples, fold_splits[0] is ([1,2,3,4], [0])
    """
    # create n partition of the data
    random.shuffle(id_list)
    # create n partition of the data
    folds = [id_list[cross::n_fold] for cross in range(n_fold)]

    fold_id = []
    # make the fold, exclude 1 sample each time
    for i in range(n_fold):
        fold_id.append(([j for j in range(n_fold) if j != i], [i]))

    return folds, fold_id
