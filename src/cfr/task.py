"""Analyze free recall data."""

import os
import numpy as np
from scipy import io
import pandas as pd
from psifr import fr


def block_fields(study):
    """Add fields labeling category blocks."""
    # add label to study events indicating the block
    list_category = study.groupby(['subject', 'list'])['category']
    study.loc[:, 'block'] = list_category.transform(fr.block_index)

    # get the number of blocks for each study list
    n_block = study.groupby(['subject', 'list'])['block'].max()
    n_block.name = 'n_block'

    # merge the n_block field
    study = pd.merge(study, n_block, left_on=['subject', 'list'],
                     right_on=['subject', 'list'], how='outer')

    # block position
    study.loc[:, 'block_pos'] = study.groupby(['subject', 'list', 'block'])[
                                    'position'].cumcount() + 1

    # block length
    block_len = study.groupby(['subject', 'list', 'block'])['block_pos'].max()
    block_len.name = 'block_len'
    study = pd.merge(study, block_len, left_on=['subject', 'list', 'block'],
                     right_on=['subject', 'list', 'block'], how='outer')
    return study


def read_free_recall(csv_file):
    """Read and score free recall data."""
    if not os.path.exists(csv_file):
        raise ValueError(f'Data file does not exist: {csv_file}')

    data = pd.read_csv(csv_file, dtype={'category': 'category'})
    data.category.cat.as_ordered(inplace=True)

    study = data.query('trial_type == "study"').copy()
    study = block_fields(study)
    recall = data.query('trial_type == "recall"').copy()

    # additional fields
    list_keys = ['session']
    fields = ['list_type', 'list_category', 'distractor']
    for field in fields:
        if field in data:
            list_keys += [field]
    study_keys = ['category', 'block', 'n_block', 'block_pos', 'block_len']
    merged = fr.merge_lists(study, recall, list_keys=list_keys,
                            study_keys=study_keys)
    return merged


def unpack_array(x):
    if isinstance(x, np.ndarray):
        x = unpack_array(x[0])
    return x


def read_similarity(sim_file):
    """Read pairwise similarity values from a standard MAT-file."""
    mat = io.loadmat(sim_file)
    items = np.array([unpack_array(i) for i in mat['items']])
    similarity = mat['sem_mat']
    vectors = mat['vectors']
    sim = {'items': items, 'vectors': vectors, 'similarity': similarity}
    return sim


def set_item_index(data, items):
    """Set item index based on a pool."""
    data_index = np.empty(data.shape[0])
    data_index.fill(np.nan)
    for idx, item in enumerate(items):
        match = data['item'] == item
        if match.any():
            data_index[match.to_numpy()] = idx
    data.loc[:, 'item_index'] = data_index
    return data
