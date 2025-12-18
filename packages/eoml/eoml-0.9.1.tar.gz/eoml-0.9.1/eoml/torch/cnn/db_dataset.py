"""PyTorch datasets for reading training data from LMDB databases.

This module provides dataset classes that read image patches and labels from LMDB
databases, with support for data augmentation, label mapping, and multi-database access.
Includes utilities for mapping between database labels and neural network outputs.
"""

import csv
import logging
from collections import Counter
from typing import List, Dict

import numpy as np
import torch
from eoml.data.persistence.lmdb import LMDBReader
from eoml.torch.cnn.outputs_transformer import ArgMaxToCategory, ArgMax
from torch.utils.data import Dataset


logger = logging.getLogger(__name__)

def sample_list(keys_out, mapper, filter_na=True):
    """Transform id:value pairs to id:nn_output using mapper.

    Args:
        keys_out (dict): Dictionary mapping sample IDs to database values.
        mapper: Mapper object with __call__ method for value transformation.
        filter_na (bool, optional): Filter out samples with invalid output. Defaults to True.

    Returns:
        list: List of (id, nn_output) tuples.
    """
    if filter_na:
        sample = [(id, mapper(val)) for id, val in keys_out.items() if mapper(val) != mapper.no_target]
    else:
        sample = [(id, mapper(val)) for id, val in keys_out.items()]

    return sample


def sample_list_id(keys_out, mapper, filter_na=True):
    """Return list of sample IDs, optionally filtering invalid outputs.

    Args:
        keys_out (dict): Dictionary mapping sample IDs to database values.
        mapper: Mapper object with __call__ method for value transformation.
        filter_na (bool, optional): Filter out samples with invalid output. Defaults to True.

    Returns:
        list: List of sample IDs.
    """
    if filter_na:
        sample = [id for id, val in keys_out.items() if mapper(val) != mapper.no_target]
    else:
        sample = [id for id, val in keys_out.items()]

    return sample


class NNOutput:
    """Represents a neural network output category with associated database labels.

    Maps database label values to neural network output indices and final map values.

    Attributes:
        name (str): Name of the output category.
        map_out (int): Integer value to write to output map.
        nn_out (int): Neural network output index for this category.
        labels_value (list): Database label values that map to this category.
        labels_name (list): Human-readable names for labels.
    """
    """
    Represent one possible output of a neural network and the value which should be given to the map
    If no map output is specified, it will be the same as the neural network argmax value of the output
    """
    def __init__(self, name: str, labels_value: List, labels_name: List, nn_out:int, map_out: int = None):
        """Initialize NNOutput category.

        Args:
            name (str): Name of the output category.
            labels_value (List): Database label values that map to this category.
            labels_name (List): Human-readable names for the labels.
            nn_out (int): Neural network output index for this category.
            map_out (int, optional): Value to write to output map. Defaults to nn_out if None.
        """
        self.name = name
        self.map_out = map_out
        self.nn_out = nn_out

        self.labels_value = labels_value.copy()
        self.labels_name = labels_name.copy()

    def __repr__(self):
        return f'NNOutput(name: {repr(self.name)}, ' \
               f' nn_out: {repr(self.nn_out)}, ' \
               f' map_out:{repr(self.map_out)}, ' \
               f' labels_value: {repr(self.labels_value)}, ' \
               f'labels_name: {repr(self.labels_name)})'


class Mapper:
    """Maps database values to neural network outputs.

    Builds a dictionary mapping database label values to neural network output indices.
    Supports grouping multiple database labels into single NN categories.

    Attributes:
        output_list (List[NNOutput]): List of output categories.
        dictionary (dict): Mapping from database values to NN outputs.
        no_target: Value returned for invalid/missing labels.
        vectorize (bool): Whether to use one-hot vector outputs.
        label_dictionary (Dict[str,int], optional): Maps label names to values.
    """

    def __init__(self, no_target=-1, vectorize=False, label_dictionary: Dict[str,int]=None):
        """Initialize Mapper.

        Args:
            no_target (int, optional): Value for invalid targets. Defaults to -1.
            vectorize (bool, optional): Use one-hot vectors instead of scalar outputs.
                Defaults to False.
            label_dictionary (Dict[str,int], optional): Maps label names to integer values.
                Defaults to None.
        """
        self.output_list: List[NNOutput] = []
        self.dictionary = {}
        self.no_target = no_target
        self.vectorize = vectorize

        self.label_dictionary = label_dictionary

    def __repr__(self):
        return f'Mapper(output_list: {repr(self.output_list)}, ' \
               f'dictionary: {repr(self.dictionary)}, ' \
               f'no_target: {repr(self.no_target)}, ' \
               f'vectorize: {repr(self.vectorize)})' \


    def load_dic_from_file(self, csv_path):
        with open(csv_path, mode='r') as infile:
            reader = csv.reader(infile)
            self.label_dictionary = {rows[0]: rows[1] for rows in reader}

    def map_value_names(self):
        return [(output.map_out, output.name) for output in self.output_list]

    def map_names(self):
        return [output.name for output in self.output_list]

    def map_values(self):
        return [output.map_out for output in self.output_list]

    def nn_name(self):
        return [output.name for output in self.output_list]

    def add_category(self, name, labels, map_value=None):
        """ add an output to the neural network"""

        labels_name = labels

        if self.label_dictionary is not None:
            labels_values = [self.label_dictionary[name] for name in labels]
        else:
            labels_values = labels

        if map_value is None:
            map_value = len(self)

        category = NNOutput(name, labels_values, labels_name, len(self), map_value)

        self.output_list.append(category)
        self._update_dictionary(category)

    def __len__(self):
        return len(self.output_list)

    def _vectorize(self, no_target=-1):
        """Transform to integer output to vector output """

        for i, value in enumerate(self.output_list):
            out = np.zeros(len(self))
            out[i] = 1
            value.nn_out = out

        # if no target has len we assum it fine and no need to touch
        if hasattr(no_target, '__len__'):
            self.no_target = no_target
        else:
            # set it to a vector of 0
            self.no_target = np.zeros(len(self))

    def __call__(self, value):
        return self.dictionary.get(value, self.no_target)

    def map_output_transformer(self):
        """Return a transformer to change transform the output of the nn (assuming argmax is used)"""
        is_identity = True
        nn_out_to_map = []
        for i, out in enumerate(self.output_list):
            is_identity = is_identity and (i == out.map_out)
            nn_out_to_map.append(out.map_out)

        return ArgMax() if is_identity else ArgMaxToCategory(nn_out_to_map)

    def _update_dictionary(self, output: NNOutput):
        """Update the dictionary transforming mapping the label to the output based ont the new nn output """
        for value in output.labels_value:
            if value in self.dictionary.keys():
                logger.warning(f"{value} appears twice in the label-value mapping. One value has been ignored.")
            self.dictionary[value] = output.nn_out


def db_dataset_multi_proc_init(worker_id):
    """This function initialise the dataset in a way that the database reader environment is keep open during the full
     process life

     Used to fix:
     Issue with newer version and lmdb, keep the db env open for the worker
    https://github.com/jnwatson/py-lmdb/issues/340

     """
    worker_info = torch.utils.data.get_worker_info()
    dataset: DBDataset = worker_info.dataset
    dataset.init_db_environment(True)


class DBDataset(Dataset):
    """PyTorch Dataset for reading training samples from LMDB database.

    Reads image patches and labels from LMDB database with optional label mapping
    and data augmentation. Supports both single-threaded and multi-threaded data loading.

    Attributes:
        multithread (bool): Whether to use multi-threaded data loading.
        db_path (str): Path to LMDB database.
        samples_list (np.ndarray): Array of sample IDs to fetch.
        target_mapper: Mapper for transforming database labels to NN outputs.
        f_transform: Data augmentation function.
        transform_param (np.ndarray, optional): Parameters for augmentation per sample.
        reader (LMDBReader): Database reader instance.
    """

    def __init__(self, db_path, samples_list, target_mapper=None, f_transform=None, transform_param=None, multithread=True):
        """Initialize DBDataset.

        Args:
            db_path (str): Path to LMDB database file.
            samples_list (list): List of sample IDs to include in dataset.
            target_mapper (Mapper, optional): Maps database labels to NN outputs.
                Defaults to None.
            f_transform (callable, optional): Data augmentation function. Defaults to None.
            transform_param (list, optional): Per-sample augmentation parameters.
                Must be numeric types to avoid memory leaks. Defaults to None.
            multithread (bool, optional): Enable multi-threaded loading. Defaults to True.

        Note:
            - Use numpy arrays (not Python objects) for transform_param to avoid memory leaks
              (see https://github.com/pytorch/pytorch/issues/13246)
            - For multithread=True, use db_dataset_multi_proc_init as worker_init_fn
              (see https://github.com/jnwatson/py-lmdb/issues/340)
        """
        super().__init__()

        self.multithread = multithread

        self.db_path = db_path

        # normal list cause memory leak
        self.samples_list = np.array(samples_list)
        self.target_mapper = target_mapper

        self.f_transform = f_transform

        if transform_param is not None:
            self.transform_param = np.array(transform_param)
        else:
            self.transform_param = None

        self.reader = None
        if not multithread:
            self.init_db_environment(False)

    def init_db_environment(self, keep_env_open):
        """init the db environment, Used to init it in different process using the worker_init_fun from
        the datasetloader"""
        self.reader = LMDBReader(self.db_path, keep_env_open=keep_env_open)

    def __len__(self):
        return len(self.samples_list)

    def __getitem__(self, idx):

        # TODO we create the reader here for multithreading env, but maybe could be done differently

        with self.reader as db:

            if hasattr(idx, '__iter__'):
                return self._get_items(idx, db)

            if isinstance(idx, int):
                return self._get_one_item(idx, db)

            if isinstance(idx, slice):
                # Get the start, stop, and step from the slice
                return self._get_items(range(idx.start, idx.stop, idx.step), db)

    def batch_statistic(self):

        reader = LMDBReader(self.db_path)

        with reader:
            outputs = [reader.get_output(s) for s in self.samples_list]

        outputs = [self.target_mapper(val) for val in outputs]

        counter = Counter(outputs)
        logger.info(f"counter: {counter}")
        #total = counter.total()
        # highest appearing value
        maximum = counter.most_common()[0][1]

        logger.info(f"most common category {maximum}")

        return {key: maximum / val for key, val in counter.items()}

    def weight_list(self):

        weight_dic = self.batch_statistic()

        reader = LMDBReader(self.db_path)
        with reader:
            weights = []
            for s in self.samples_list:
                target_val = self.target_mapper(reader.get_output(s))
                weights.append(weight_dic[target_val])

        return weights

    def _get_items_deprecated(self, iterable, reader):
        inputs = []
        targets = []

        # see default collate for better memory management

        for key in iterable:
            # inputs[i], targets[i] = self._get_one_item(key, reader)
            input, target = self._get_one_item(key, reader)
            inputs.append(input)
            targets.append(target)


        #batch = len(inputs)
        # taken from default_collate, we initialise the space on a shared memory, to avoid extra copy
        # could also be done for target
        #storage = input.storage()._new_shared(len(inputs) * input.numel(), device=input.device)
        #out = input.new(storage).resize_(batch, *list(input.size()))
        #torch.stack(inputs, out=out)

        #return out, torch.LongTensor(targets)

        return torch.stack(inputs), torch.LongTensor(targets)

    def _get_items(self, iterable, reader):
        # datas = []
        # labels = []
        batch = len(iterable)

        iterable = iterable.__iter__()

        try:
            (one_input,), target = self._get_one_item(next(iterable), reader)

        except StopIteration:
            return []

        # compute the shape
        shape_in = (batch,) + one_input.shape

        if isinstance(target, int):
            shape_out = batch
            targets = torch.empty(shape_out, dtype=torch.long)
        else:
            shape_out = (batch,) + target.shape
            targets = torch.empty(shape_out, dtype=torch.float32)

        inputs = torch.empty(shape_in, dtype=torch.float32)

        inputs[0] = one_input
        targets[0] = target

        for i, key in enumerate(iterable, 1):
            # the nn take on parameter so we unpack the 1 tuples and make it for the batch
            (inputs[i],), targets[i] = self._get_one_item(key, reader)
        # the nn take on parameter so we make a 1 element tuple
        return (inputs,), targets

    def _get_one_item(self, idx, reader):
            key = self.samples_list[idx]

            # key = [db_key, tranfsorm_param]
            inputs, target = reader.get_data(int(key))

            inputs = torch.from_numpy(inputs.copy())

            if self.f_transform is not None:

                if self.transform_param is not None:
                    param = self.transform_param[idx]
                    inputs = self.f_transform(inputs, *param)
                else:
                    inputs = self.f_transform(inputs)


            if self.target_mapper is not None:
                target = self.target_mapper(target)

            # the nn take on parameter so we make a 1 element tuple
            return (inputs,), target



class DBDatasetMeta(DBDataset):
    """
    read dataset from db.
    """

    def __init__(self, db_path, samples_list, target_mapper=None, f_transform=None, transform_param=None):
        """

        :param db_path: path of the db to open
        :param samples_list: a list of key to fetch from the db
        :param target_mapper: map the db output to the nn output.

        https://github.com/pytorch/pytorch/issues/13246 use numpy of NOT OBJ to solve memory leak
        transfomration parameter should all be number!!!


        """
        super().__init__(db_path, samples_list, target_mapper, f_transform, transform_param)

    def __len__(self):
        return len(self.samples_list)

    def __getitem__(self, idx):

        with self.reader as db:

            if hasattr(idx, '__iter__'):
                inputs, outputs = self._get_items(idx, db)
                headers = self._get_headers(idx, db)
                return inputs, outputs, headers

            if isinstance(idx, int):
                _input, output = self._get_one_item(idx, db)
                header = self._get_header(idx, db)
                return _input, output, header

            if isinstance(idx, slice):
                # Get the start, stop, and step from the slice
                inputs, outputs = self._get_items(range(idx.start, idx.stop, idx.step), db)
                headers = self._get_headers(range(idx.start, idx.stop, idx.step), db)
                return inputs, outputs, headers

    def _get_headers(self, iterable, reader):
        return [self._get_header(h, reader) for h in iterable]

    def _get_header(self, idx, reader):
        key = int(self.samples_list[idx])
        return reader.get_header(key)


class DBInfo:
    def __init__(self, db_path, sample_list, target_mapper, f_transform=None, transform_param=None):
        self.db_path = db_path
        self.sample_list = sample_list
        self.target_mapper = target_mapper
        self.f_transform = f_transform
        self.transform_param = transform_param


class MultiDBDataset(Dataset):
    """
       read dataset from multiple db
       TODO check if helper function of torch can not replace that.
       TODO 2 check if get one item function
       """
    def __init__(self, db_info: List[DBInfo], multithread=True):
        """

        :param db_path: path of the db to open
        :param samples_list: a list of key to fetch from the db
        :param target_mapper: map the db output to the nn output.

        https://github.com/pytorch/pytorch/issues/13246 use numpy of NOT OBJ to solve memory leak not implemented here
        transfomration parameter should all be number!!!
        """
        super().__init__()

        self.db_info: List[DBInfo] = db_info

        self.size = 0

        #todo improve
        index =0
        self.samples_index= []
        for db_index, db in enumerate(self.db_info):
            self.size += len(db.sample_list)

            for sample_index in db.sample_list:
                # sample list is the pair db and sample index in db
                self.samples_index.append((db_index, sample_index))
                index += 1

        self.readers=None

        if not multithread:
            self.init_db_environment(False)
    def init_db_environment(self, keep_env_open):
        """init the db environment, Used to init it in different process using the worker_init_fun from
        the datasetloader"""
        self.readers = [LMDBReader(db.db_path, keep_env_open=keep_env_open) for db in self.db_info]

    def __len__(self):
        return self.size

    def __getitem__(self, idx):

        # TODO we create the reader here for multithreading env, but maybe could be done differently

        try:

            for reader in self.readers:
                reader.open()

            if hasattr(idx, '__iter__'):
                return self._get_items(idx, self.readers)

            if isinstance(idx, int):
                return self._get_one_item(idx, self.readers)

            if isinstance(idx, slice):
                # Get the start, stop, and step from the slice
                return self._get_items(range(idx.start, idx.stop, idx.step), self.readers)

        except Exception as e:
            raise e

        finally:
            for reader in self.readers:
                reader.close()

    def _get_items(self, iterable, readers):
        # datas = []
        # labels = []
        batch = len(iterable)

        iterable = iterable.__iter__()


        try:
            idx = next(iterable)
            input, target = self._get_one_item(idx, readers)

        except StopIteration:
            return []

        # compute the shape
        shape_in = (batch,) + input.shape

        if isinstance(target, int):
            shape_out = batch
            targets = torch.empty(shape_out, dtype=torch.long)
        else:
            shape_out = (batch,) + target.shape
            targets = torch.empty(shape_out, dtype=torch.float32)

        inputs = torch.empty(shape_in, dtype=torch.float32)

        inputs[0] = input
        targets[0] = target

        for i, idx in enumerate(iterable, 1):

            inputs[i], targets[i] = self._get_one_item(idx, readers)

        return inputs, targets

    def _get_one_item(self, idx, readers):
        db_index, id_sample = self.samples_index[idx]
        inputs, target = readers[db_index].get_data(id_sample)

        inputs = torch.from_numpy(inputs.copy())

        if self.db_info[db_index].f_transform is not None:

            if self.db_info[db_index].transform_param is not None:
                param = self.db_info[db_index].transform_param[id_sample]
                inputs = self.db_info[db_index].f_transform(inputs, *param)
            else:
                inputs = self.db_info[db_index].f_transform(inputs)

        if self.db_info[db_index].target_mapper is not None:
            target = self.db_info[db_index].target_mapper(target)

        return inputs, target
