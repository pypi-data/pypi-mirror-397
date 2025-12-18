"""Automation tasks for machine learning workflows with Earth observation data.

This module provides high-level functions and utilities for automating common machine learning
workflows including data extraction, model training, validation, and inference mapping. It serves
as the orchestration layer that connects data preparation, model creation, training loops, and
prediction generation.

Key functionality:
    - Sample extraction from raster data and vector labels
    - K-fold cross-validation setup for training/validation splits
    - Dataset and dataloader configuration with augmentation
    - Model instantiation and initialization
    - Training orchestration with multiple datasets
    - Map generation using trained models
    - Statistics computation for trained models
"""

import itertools
import logging
from os import path

logger = logging.getLogger(__name__)

import fiona
import torch

from eoml import get_read_profile, get_write_profile
from eoml.data.dataset_utils import k_fold_sample, random_split
from eoml.data.persistence.generic import GeoDataWriter
from eoml.data.persistence.lmdb import LMDBasicGeoDataDAO, LMDBReader
from eoml.raster.dataset.extractor import ThreadedOptimiseLabeledWindowsExtractor
from eoml.torch.cnn.augmentation import rotate_flip_transform
from eoml.torch.cnn.db_dataset import sample_list_id, DBDataset, DBDatasetMeta, DBInfo, MultiDBDataset, \
    db_dataset_multi_proc_init
from eoml.torch.cnn.map_dataset import IterableMapDataset, NNMapper
from eoml.torch.cnn.torch_utils import meta_data_collate, batch_collate
from eoml.torch.models import initialize_weights, ModelFactory
from eoml.torch.sample_statistic import ClassificationStats, BadlyClassifyToGPKG
from eoml.torch.trainer import GradNormClipper, agressive_train_labeling

from rasterio.enums import Resampling
from shapely.geometry import shape
from torch.utils.data import RandomSampler, BatchSampler, DataLoader, WeightedRandomSampler

from rasterop.tiled_op.tiled_raster_op import tiled_op


class KFoldIterator:
    """Iterator for K-fold cross-validation splits.

    Constructs sequences of training and validation folds based on a list of folds
    and split specifications. Each split is defined as ((train_fold_indices), (validation_fold_indices)).

    Attributes:
        folds: List of fold data, where each fold contains sample identifiers
        folds_split: List of tuples defining the train/validation split for each iteration.
            Each tuple is ((train_indices,), (val_indices,))
    """

    def __init__(self, folds, folds_split):
        """Initialize the K-fold iterator.

        Args:
            folds: List of folds, where each fold is a list of sample identifiers
            folds_split: List of split specifications, where each split is a tuple
                ((train_fold_indices), (validation_fold_indices))
        """
        self.folds = folds
        self.folds_split = folds_split

    def __iter__(self):
        """Iterate through all fold splits.

        Yields:
            Tuple of (train_fold, validation_fold), where each fold is a flat list
            of sample identifiers
        """
        for split in self.folds_split:
            train_fold = []
            validation_fold = []
            for s in split[0]:
                train_fold.extend(self.folds[s])
            for s in split[1]:
                validation_fold.extend(self.folds[s])

            yield train_fold, validation_fold

    def __len__(self):
        """Return the number of splits.

        Returns:
            Number of train/validation splits
        """
        return len(self.folds_split)


# todo use torch script for model
def extract_sample(gps_path, raster_reader, db_path, windows_size, label_name="Class", id_field=None, mask_path=None, force_write=False):
    """Extract training samples from raster data based on GPS/vector labels.

    Extracts image windows from raster data at locations specified by vector geometries
    (GPS points) and stores them in an LMDB database for efficient training data access.

    Args:
        gps_path: Path to vector file (GeoPackage, Shapefile, etc.) containing sample locations
        raster_reader: RasterReader instance for reading the source imagery
        db_path: Output path for the LMDB database
        windows_size: Size of the extraction window (in pixels)
        label_name: Name of the attribute field containing class labels. Defaults to "Class"
        id_field: Name of the unique identifier field. Defaults to None (uses feature index)
        mask_path: Optional path to mask polygon restricting extraction area
        force_write: If True, overwrite existing database. Defaults to False

    Returns:
        None. Writes extracted samples to database at db_path
    """
    if force_write or not path.exists(db_path):
        writer = GeoDataWriter(LMDBasicGeoDataDAO(db_path))

        #extractor = LabeledWindowsExtractor(gps_path, writer, raster_reader, windows_size, label_name, id_field)

        #extractor = LabeledWindowsExtractor(gps_path, writer, raster_reader, windows_size, label_name)
        #extractor = OptimiseLabeledWindowsExtractor(gps_path, writer, raster_reader, windows_size,
        #                                            label_name, id_field, mask_path=mask_path)
        extractor = ThreadedOptimiseLabeledWindowsExtractor(gps_path, writer, raster_reader, windows_size, label_name,
                                                            id_field, mask_path=mask_path, worker=4, prefetch=3)
        #extractor = ProcessOptimiseLabeledWindowsExtractor(gps_path, writer, raster_reader, windows_size, label_name,
        #                                                    id_field, mask_path=mask_path, worker=4, prefetch=3)

        extractor.process()
    else:
        logger.info(f"{db_path} exists, skipping extraction")

def multi_samples_k_fold_setup(db_path, mapper, n_fold=2):
    """Set up K-fold cross-validation splits for multiple databases.

    Args:
        db_path: List of paths to LMDB databases
        mapper: List of output mappers corresponding to each database
        n_fold: Number of folds for cross-validation. Defaults to 2

    Returns:
        Zipped iterator of K-fold splits for each database
    """
    iterator = [samples_k_fold_setup(path, mapp, n_fold=n_fold) for path, mapp in zip(db_path, mapper)]
    return zip(*iterator)

def multi_samples_yearly_k_fold_setup(db_path, mapper, n_fold=2):
    """Set up K-fold cross-validation for multi-year datasets.

    Creates K-fold splits based on unique geopackage identifiers that appear across
    multiple years (one database per year). This ensures samples from the same location
    across different years are grouped together, maintaining temporal consistency in splits.

    Note: Weighting of repeating samples is not currently implemented.

    Args:
        db_path: List of paths to LMDB databases, one per year
        mapper: List of output mappers for each database
        n_fold: Number of folds for cross-validation. Defaults to 2

    Returns:
        Zipped iterator of KFoldIterator objects, one for each database

    Raises:
        None
    """

    key_set = set()
    for db, mapp in zip(db_path, mapper):
        db_reader = LMDBReader(db)
        with db_reader:
            id_out = db_reader.get_sample_id_output_dic()

        sample_idx = sample_list_id(id_out, mapp)
        key_set.update(sample_idx)

    key_set = list(key_set)
    folds_idx_ref, folds_split = k_fold_sample(key_set, n_fold)

    iterators=[]
    for db, mapp in zip(db_path, mapper):
        db_reader = LMDBReader(db)
        with db_reader:
            id_key = db_reader.get_sample_id_db_key_dic()

            fold_i = []
            for folds in folds_idx_ref:
                f = []
                for idx in folds:
                    key = id_key.get(idx, None)
                    # check is the key exist and if the key is a cover we are mapping
                    if key is not None and mapp(db_reader.get_output(key)) != mapp.no_target:
                        f.append(key)

                fold_i.append(f)

        iterators.append(KFoldIterator(fold_i, folds_split))

    return zip(*iterators)


def samples_k_fold_setup(db_path, mapper, n_fold=2):
    """Set up K-fold cross-validation splits for a single database.

        Args:
            db_path: Path to LMDB database
            mapper: Output mapper for converting raw labels
            n_fold: Number of folds for cross-validation. Defaults to 2

        Returns:
            KFoldIterator object containing train/validation splits
        """
    db_reader = LMDBReader(db_path)

    with db_reader:
        keys_out = db_reader.def_get_output_dic()

    id_list = sample_list_id(keys_out, mapper)

    folds, folds_split = k_fold_sample(id_list, n_fold)

    return KFoldIterator(folds, folds_split)


def samples_split_setup(db_path, mapper, split=None):
    """Set up a single train/validation split of samples.

    Args:
        db_path: Path to LMDB database
        mapper: Output mapper for converting raw labels
        split: List defining train/validation split ratios [train_frac, val_frac].
            Defaults to [0.8, 0.2]

    Returns:
        List containing a single train/validation split
    """
    if split is None:
        split = [0.8, 0.2]

    db_reader = LMDBReader(db_path)
    with db_reader:
        keys_out = db_reader.def_get_output_dic()

    id_list = sample_list_id(keys_out, mapper)

    train_id, validation_id = random_split(id_list, split, True)
    return [[train_id, validation_id]]


def augmentation_setup(samples, angles=None, flip=None):
    """Set up data augmentation parameters for a set of samples.

    Args:
        samples: List of sample identifiers
        angles: List of rotation angles in degrees. Defaults to [0, 90, 180, -90]
        flip: List of boolean flags for horizontal flipping. Defaults to [False, True]

    Returns:
        Tuple of (augmented_samples, augmentation_parameters)
    """
    if angles is None:
        angles = [0, 90, 180, -90]

    if flip is None:
        flip = [False, True]

    t_param_list = list(itertools.product(angles, flip))

    t_params = []
    samples_split = []
    for k in samples:
        for p in t_param_list:
            t_params.append(p)
            samples_split.append(k)

    return samples_split, t_params


def dataset_setup(train_id_split, validation_split, augmentation_param, db_path, mapper, db_type=DBDataset):
    """Set up training and validation datasets with augmentation.

    Args:
        train_id_split: List of training sample IDs
        validation_split: List of validation sample IDs
        augmentation_param: Dict containing augmentation settings
        db_path: Path to LMDB database
        mapper: Output mapper for converting raw labels
        db_type: Dataset class to use. Defaults to DBDataset

    Returns:
        Tuple of (train_dataset, validation_dataset)
    """
    # we load a full batch at once to limit the opening and closing of the db

    # dataset_train = DBDataset(gps_db, train_id, mapper_vector)
    transform_param = None
    transform = None
    transform_valid = None
    if augmentation_param["methode"] == "fix":
        train_id_split, transform_param = augmentation_setup(train_id_split, **augmentation_param["parameters"])
        transform = rotate_flip_transform

    if augmentation_param["methode"] == "no_dep":
        transform = augmentation_param["transform_train"]
        transform_valid = augmentation_param["transform_valid"]

    dataset_train = db_type(db_path, train_id_split, mapper, f_transform=transform,
                              transform_param=transform_param)
    dataset_valid = db_type(db_path, validation_split, mapper, f_transform=transform_valid)

    return dataset_train, dataset_valid


def dataloader_setup(dataset_train, dataset_valid, batch_size, balance_sample, num_worker,
                     prefetch, device, persistent_workers):
    """Set up training and validation data loaders.

    Args:
        dataset_train: Training dataset
        dataset_valid: Validation dataset
        batch_size: Number of samples per batch
        balance_sample: Whether to use weighted sampling for class balance
        num_worker: Number of worker processes for data loading
        prefetch: Number of batches to prefetch
        device: Device to use ('cuda' or 'cpu')
        persistent_workers: Whether to maintain persistent worker processes

    Returns:
        Tuple of (train_dataloader, validation_dataloader)
    """
    # TODO balanced sample will not work for multi sample
    if balance_sample:
        train_weight = dataset_train.weight_list()
        #test_weight = dataset_valid.weight_list()

        #print(train_weight)
        #print(test_weight)

        train_rsampler = WeightedRandomSampler(train_weight, len(train_weight), replacement=True)
    else:
        train_rsampler = RandomSampler(dataset_train, replacement=False, num_samples=None, generator=None)

    # TODO also balance but not for now for comparison
    valid_rsampler = RandomSampler(dataset_valid, replacement=False, num_samples=None, generator=None)


    train_bsampler = BatchSampler(train_rsampler, batch_size=batch_size, drop_last=False)


    valid_bsampler = BatchSampler(valid_rsampler, batch_size=batch_size, drop_last=False)

    if device == "cuda":
        pin_memory = True
    else:
        pin_memory = False

    train_dataloader = DataLoader(dataset_train, sampler=train_bsampler, collate_fn=batch_collate,
                                  num_workers=num_worker, prefetch_factor=prefetch, pin_memory=pin_memory,
                                  persistent_workers=persistent_workers, worker_init_fn=db_dataset_multi_proc_init)
    validation_dataloader = DataLoader(dataset_valid, sampler=valid_bsampler, collate_fn=batch_collate,
                                       num_workers=num_worker, prefetch_factor=prefetch, pin_memory=pin_memory,
                                       persistent_workers=persistent_workers, worker_init_fn=db_dataset_multi_proc_init)

    return train_dataloader, validation_dataloader

def model_setup(model_name, type, path, device, nn_parameter):
    """Set up and initialize a neural network model.

    Args:
        model_name: Name of the model architecture
        type: Type of model
        path: Path to model weights/checkpoints
        device: Device to use ('cuda' or 'cpu')
        nn_parameter: Dict of model hyperparameters

    Returns:
        Initialized neural network model
    """
    # ----------------------------------------
    # Architecture
    # ----------------------------------------

    factory = ModelFactory()

    net = factory(model_name, type=type, path=path, model_args=nn_parameter)

    # net = Conv2Dense3(size, 65, n_out)
    #net = ConvJavaSmall(**nn_parameter)
    net.apply(initialize_weights)
    net.to(device)

    return net


def optimizer_setup(net, loss, optimizer, optimizer_parameter, scheduler_mode,
                    scheduler_parameter=None, data_loader=None, epoch=None):
    optimizer = optimizer(net.parameters(), **optimizer_parameter)
    """Set up optimizer and learning rate scheduler.

    Args:
        net: Neural network model
        loss: Loss function
        optimizer: Optimizer class
        optimizer_parameter: Dict of optimizer parameters
        scheduler_mode: Learning rate scheduler mode
        scheduler_parameter: Dict of scheduler parameters. Defaults to None
        data_loader: DataLoader for scheduler steps. Defaults to None
        epoch: Number of epochs for scheduler. Defaults to None

    Returns:
        Tuple of (optimizer, loss_function, scheduler)
    """
    if scheduler_mode is None:
        return optimizer, loss, None

    if scheduler_mode == "cycle":
        scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, steps_per_epoch=len(data_loader), epochs=epoch, **scheduler_parameter)
        return optimizer, loss, scheduler

    #if scheduler_mode == "plateau":
    #    print("metric need in step and other stuff")
    #    torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=10, threshold=0.0001,
    #                                               threshold_mode='rel', cooldown=0, min_lr=0, eps=1e-08, verbose=True)


    raise Exception("Unknown scheduler_mode")

def generate_map_iterator(jit_model_path,
                 map_path,
                 map_iterator,
                 transformer,
                 mask, #path or geom
                 bounds,
                 mode,
                 num_worker,
                 prefetch,
                 custom_collate=meta_data_collate,
                 worker_init_fn=IterableMapDataset.basic_worker_init_fn):
    # 0 full cpu, no pinning
    # 1 pinned memory in loader, moved asynchronously (more loader needed) to the gpu, (seems to like big batch)
    # 2 start cuda in each thread of the loader and prepare most of the sampled directly on the gpu (each thread/num
    # loader use ~1gb graphic memory and need torch.multiprocessing.set_start_method('spawn') to be used
    # TODO test const mem for memory limited gpy
    write_profile = get_write_profile()


    # if a path is given
    if isinstance(mask, str):
        with fiona.open(mask) as layer:
            features = [shape(feature["geometry"]) for feature in layer]
    else:
        #mask is already a mask
        features = mask

    is_pinned = False
    loader_device = "cpu"
    nn_device = "cpu"

    if isinstance(jit_model_path, str):
        model = torch.jit.load(jit_model_path)
    else:
        model = jit_model_path

    if mode == 0:
        is_pinned = False
        loader_device = "cpu"
        nn_device = "cpu"
    if mode == 1:
        is_pinned = True
        loader_device = "cpu"
        nn_device = "cuda"


    mapper = NNMapper(model,
                      stride=1,
                      loader_device=loader_device,
                      mapper_device=nn_device,
                      pin_memory=is_pinned,
                      num_worker=num_worker,
                      prefetch_factor=prefetch,
                      custom_collate=custom_collate,
                      worker_init_fn=worker_init_fn,
                      write_profile=write_profile,
                      async_agr=True)

    # deprecated, it is not recommended to use cuda in workers
    # if mode == 2:
    #     is_pinned = False
    #     loader_device = "cuda"
    #     nn_device = "cuda"

    # if mode == 2:
    #     mapper = NNMapper(model,
    #                       windows_size,
    #                       stride=1,
    #                       batch_size=batch_size,
    #                       loader_device=loader_device,
    #                       mapper_device=nn_device,
    #                       pin_memory=is_pinned,
    #                       num_worker=num_worker,
    #                       prefetch_factor=prefetch,
    #                       map_dataset_class=IterableMapDatasetConstMem,
    #                       custom_collate=meta_data_collate,
    #                       worker_init_fn=worker_init_fn,
    #                       aggregator=MapResultAggregatorConstMem,
    #                       write_profile=write_profile,
    #                       async_agr=True)

    mapper.map(map_path, map_iterator, transformer, bounds=bounds, mask=features)

    return map_path


def training_step(net, optimizer, loss, scheduler, train_dataloader, validation_dataloader, max_epochs,
                  run_stats_dir, model_base_path, model_tag, grad_clip_value, device):
    """do the training step"""

    grad_f = None
    if grad_clip_value is not None:
        grad_f = GradNormClipper(grad_clip_value)

    return agressive_train_labeling(max_epochs, net, optimizer, loss, scheduler, train_dataloader,
                                    validation_dataloader,
                                    writer_base_path=run_stats_dir, model_base_path=model_base_path,
                                    model_tag=model_tag,
                                    grad_f=grad_f, device=device)


def generate_map(jit_model_path,
                 map_path,
                 raster_reader,
                 windows_size,
                 batch_size,
                 transformer,
                 mask, #path or geom
                 bounds,
                 mode,
                 num_worker,
                 prefetch,
                 custom_collate=meta_data_collate,
                 worker_init_fn=IterableMapDataset.basic_worker_init_fn):



    map_iterator = IterableMapDataset(raster_reader, windows_size, batch_size=batch_size)

    generate_map_iterator(jit_model_path,
                         map_path,
                         map_iterator,
                         transformer,
                         mask, #path or geom
                         bounds,
                         mode,
                         num_worker,
                         prefetch,
                         custom_collate=custom_collate,
                         worker_init_fn=worker_init_fn)



def train(sample_param, augmentation_param, dataset_parameter, dataloader_parameter, model_parameter, optimizer_parameter, train_nn_parameter):
    """
    Map and train in function of the parameter
    :param sample_param:
    :param augmentation_param:
    :param dataset_parameter:
    :param model_parameter:
    :param train_nn_parameter:
    :param map_parameter:
    :return:
    """

    experiment_iterator = sample_param["methode"](**sample_param["param"])

    out = []
    for (i, (train_id, validation_id)) in enumerate(experiment_iterator):

        train_dataset, validation_dataset = dataset_setup(train_id, validation_id, augmentation_param,
                                                          **dataset_parameter)

        train_dataloader, validation_dataloader = dataloader_setup(train_dataset, validation_dataset,
                                                                   **dataloader_parameter)

        net = model_setup(**model_parameter)

        optimizer, loss, scheduler = optimizer_setup(net=net, data_loader=train_dataloader, epoch=train_nn_parameter["max_epochs"],
                                                    **optimizer_parameter)

        base_model_dir, best_model_path, model_path_jitted, model_name = training_step(net, optimizer, loss, scheduler, train_dataloader,
                                                                    validation_dataloader, **train_nn_parameter)

        del train_dataloader, validation_dataloader, net, loss, optimizer, train_id,

        out.append((base_model_dir, best_model_path, model_path_jitted, model_name))

    return out

def multi_db_merge(ids, augmentation_param, dataset_parameter):
    """Merge multiple databases into combined train/validation datasets.

    Args:
        ids: List of (train_ids, val_ids) tuples for each database
        augmentation_param: Dict of augmentation parameters
        dataset_parameter: List of dataset parameters for each database

    Returns:
        Tuple of (merged_train_dataset, merged_validation_dataset)
    """

    train_data = []
    valid_data = []
    for (train_id, validation_id), data_param in zip(ids, dataset_parameter):

        train_dataset, validation_dataset = dataset_setup(train_id, validation_id, augmentation_param, db_type= DBInfo,
                                                          **data_param)


        train_data.append(train_dataset)
        valid_data.append(validation_dataset)

    return MultiDBDataset(train_data), MultiDBDataset(valid_data)

def multi_train_and_map(sample_param, augmentation_param, dataset_parameter, dataloader_parameter,model_parameter, optimizer_parameter, train_nn_parameter,
                  map_parameter):
    """
    Map and train in function of the parameter
    :param sample_param:
    :param augmentation_param:
    :param dataset_parameter:
    :param model_parameter:
    :param train_nn_parameter:
    :param map_parameter:
    :return:
    """

    experiment_iterator = sample_param["methode"](**sample_param["param"])

    out = {}
    for (i, ids) in enumerate(experiment_iterator):

        train_dataset, validation_dataset = multi_db_merge(ids, augmentation_param, dataset_parameter)

        train_dataloader, validation_dataloader = dataloader_setup(train_dataset, validation_dataset,
                                                                   **dataloader_parameter)

        net = model_setup(**model_parameter)

        optimizer, loss, scheduler = optimizer_setup(net=net, data_loader=train_dataloader, epoch=train_nn_parameter["max_epochs"],
                                                     **optimizer_parameter)

        base_model_dir, best_model_path, model_path_jitted, model_name = training_step(net, optimizer, loss, scheduler, train_dataloader,
                                                                    validation_dataloader, **train_nn_parameter)

        # TODO add again for later
        #dataset_stats(f'{base_model_dir}' ,model_path_jitted, train_id, validation_id, dataset_parameter["db_path"],
        #              dataset_parameter["batch_size"], dataset_parameter["mapper"], dataset_parameter["num_worker"],
        #              dataset_parameter["prefetch"], train_nn_parameter["device"])

        del train_dataloader, validation_dataloader, net, loss, optimizer, ids


        for i, map_param in enumerate(map_parameter):
            map_path = f'{base_model_dir}/{map_param["map_tag"]}_{model_name}_{i}.tif'
            map_param["map_path"] = map_path
            current_map_parameter = map_param.copy()
            del current_map_parameter['map_tag'] # remove as not a input of the mapping function

            m_out = out.setdefault(i, [])
            m_out.append(generate_map(model_path_jitted, **current_map_parameter))

    return out


def train_and_map(sample_param, augmentation_param, dataset_parameter, dataloader_parameter, model_parameter, optimizer_parameter, train_nn_parameter,
                  map_parameter):
    """
    Map and train in function of the parameter
    :param sample_param:
    :param augmentation_param:
    :param dataset_parameter:
    :param model_parameter:
    :param train_nn_parameter:
    :param map_parameter:
    :return:
    """

    experiment_iterator = sample_param["methode"](**sample_param["param"])

    out = []
    for (i, (train_id, validation_id)) in enumerate(experiment_iterator):

        train_dataset, validation_dataset = dataset_setup(train_id, validation_id, augmentation_param,
                                                          **dataset_parameter)

        train_dataloader, validation_dataloader = dataloader_setup(train_dataset, validation_dataset,
                                                                **dataloader_parameter)

        net = model_setup(**model_parameter)

        optimizer, loss, scheduler = optimizer_setup(net=net, data_loader=train_dataloader,
                                                     epoch=train_nn_parameter["max_epochs"],
                                                     **optimizer_parameter)

        base_model_dir, best_model_path, model_path_jitted, model_name = training_step(net,
                                                                                       optimizer,
                                                                                       loss,
                                                                                       scheduler,
                                                                                       train_dataloader,
                                                                                       validation_dataloader,
                                                                                       **train_nn_parameter)

        dataset_stats(f'{base_model_dir}', model_path_jitted, train_id, validation_id, augmentation_param["transform_valid"], dataset_parameter["db_path"],
                      dataloader_parameter["batch_size"], dataset_parameter["mapper"], dataloader_parameter["num_worker"],
                      dataloader_parameter["prefetch"], train_nn_parameter["device"])

        del train_dataloader, validation_dataloader, net, loss, optimizer, train_id

        map_path = f'{base_model_dir}/{map_parameter["map_tag"]}_{model_name}_{i}.tif'
        map_parameter["map_path"] = map_path
        current_map_parameter = map_parameter.copy()
        del current_map_parameter['map_tag'] # remove as not a input of the mapping function
        out.append(generate_map(model_path_jitted, **current_map_parameter))


    return out


def dataset_stats(path, jit_model_path, train_id_split, validation_split, transform, db_path, batch_size, mapper, num_worker,
                  prefetch, device):

    model = torch.jit.load(jit_model_path)
    model = model.to(device)

    # we load a full batch at once to limit the opening and closing of the db

    # dataset_train = DBDataset(gps_db, train_id, mapper_vector)
    dataset_train = DBDatasetMeta(db_path, train_id_split, mapper, f_transform=transform)
    dataset_valid = DBDatasetMeta(db_path, validation_split, mapper, f_transform=transform)

    train_rsampler = RandomSampler(dataset_train, replacement=False, num_samples=None, generator=None)
    valid_rsampler = RandomSampler(dataset_valid, replacement=False, num_samples=None, generator=None)

    train_bsampler = BatchSampler(train_rsampler, batch_size=batch_size, drop_last=False)
    valid_bsampler = BatchSampler(valid_rsampler, batch_size=batch_size, drop_last=False)

    if device == "cuda":
        pin_memory = True
    else:
        pin_memory = False


    train_dataloader = DataLoader(dataset_train, sampler=train_bsampler, collate_fn=batch_collate,
                                  num_workers=num_worker, prefetch_factor=prefetch, pin_memory=pin_memory,
                                  worker_init_fn=db_dataset_multi_proc_init)
    validation_dataloader = DataLoader(dataset_valid, sampler=valid_bsampler, collate_fn=batch_collate,
                                       num_workers=num_worker, prefetch_factor=prefetch, pin_memory=pin_memory,
                                       worker_init_fn=db_dataset_multi_proc_init)

    stats = ClassificationStats(len(mapper), device, mapper.nn_name())

    stats.compute(model, train_dataloader, device)
    stats.display()
    stats.to_file(f"{path}/train.txt")

    stats.compute(model, validation_dataloader, device)
    stats.display()
    stats.to_file(f"{path}/train.txt")

    bctg = BadlyClassifyToGPKG()

    bctg.compute(model, train_dataloader, device)
    bctg.to_file(f"{path}/train.gpkg")

    bctg.compute(model, validation_dataloader, device)
    bctg.to_file(f"{path}/validation.gpkg")

def tiled_task(maps, raster_out, operation, bounds=None, res=None,
               resampling=Resampling.nearest, target_aligned_pixels=False, indexes=None, src_kwds=None,
               dst_kwds=None, num_workers=8):
    """
    Execute the specified tiled task with the specified arguments
    :param maps:
    :param raster_out:
    :param operation:
    :param operation_args:
    :param bounds:
    :param res:
    :param nodata:
    :param resampling:
    :param target_aligned_pixels:
    :param indexes:
    :param src_kwds:
    :param dst_kwds:
    :param num_workers:
    :return:
    """


    if src_kwds is None:
        src_kwds = get_read_profile()

    if dst_kwds is None:
        dst_kwds = get_write_profile()

    tiled_op(
        maps,
        operation,
        operation.n_band_out,
        raster_out,
        bounds=bounds,
        res=res,
        nodata=operation.nodata,
        dtype=operation.dtype,
        indexes=indexes,
        resampling=resampling,
        target_aligned_pixels=target_aligned_pixels,
        dst_kwds=dst_kwds,
        src_kwds=src_kwds,
        num_workers=num_workers)




# only run if main script (important as we will use threading with the spawn methode