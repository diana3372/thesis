#!/usr/bin/env python2

import numpy as np
import os
import pickle

from generate_dataset import *
from image_utils import *

N_TRAIN_TINY    = 1
N_TRAIN_SMALL = 10
N_TRAIN_MED     = 100
N_TRAIN_LARGE = 1000
N_TRAIN_ALL     = N_TRAIN_MED



if __name__ == "__main__":

    debugging = False

    folder_name = 'dummy_different_targets_{}_{}'.format(N_CELLS, N_CELLS)
    f_generate_dataset = get_dataset_dummy_different_targets#get_dataset_different_targets

    # seed = 42
    # np.random.seed(seed)

    # From Serhii's original experiment
    train_size = 74504 if not debugging else 1
    val_size = 8279 if not debugging else 1
    test_size = 40504 if not debugging else 1


    train_data, val_data, test_data = get_datasets(train_size, val_size, test_size, f_generate_dataset)

    has_tuples = type(train_data[0]) is tuple


    train_data_tiny = train_data[:N_TRAIN_TINY]
    train_data_small = train_data[:N_TRAIN_SMALL]
    train_data_med = train_data[:N_TRAIN_MED]
    train_data_large = train_data

    sets = {
        "train.tiny": train_data_tiny,
        "train.small": train_data_small,
        "train.med": train_data_med,
        "train.large": train_data_large,
        "val": val_data,
        "test": test_data
    }

    assert not os.path.exists(folder_name), 'Trying to overwrite?'
    os.mkdir(folder_name)

    for set_name, set_data in sets.items():
        if not has_tuples:
            set_inputs = np.asarray([image.data[:,:,0:3] for image in set_data])
        else:
            tuple_len = len(set_data[0]) # 2
            n_rows = len(set_data)
            set_inputs = np.zeros((n_rows, tuple_len, WIDTH, HEIGHT, N_CHANNELS), dtype=np.uint8)
            for i in range(n_rows):
                for j in range(tuple_len):
                    set_inputs[i][j] = set_data[i][j].data[:,:,0:3]

        np.save("{}/{}.input".format(folder_name, set_name), set_inputs)

        if not has_tuples:
            set_metadata = [image.metadata for image in set_data]
        else:
            set_metadata = [(image[0].metadata, image[1].metadata) for image in set_data]

        pickle.dump(set_metadata, open('{}/{}.metadata.p'.format(folder_name, set_name), 'wb'))

    print('Saved data set to folder {}'.format(folder_name))
