"""Classification statistics and evaluation utilities for PyTorch models.

This module provides classes for computing classification metrics and exporting
misclassified samples to geospatial formats for analysis.
"""

import logging
import math
import os
from collections import OrderedDict
from typing import Optional, Literal, List

import fiona
import numpy as np
import torch
from fiona.crs import from_epsg
from shapely.geometry import mapping
from torch.utils.data import DataLoader
from torchmetrics import F1Score, Accuracy, Recall, Precision
from torchmetrics.classification import MulticlassConfusionMatrix
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ClassificationStats:
    """Compute and display classification metrics for multi-class problems.

    Calculates F1, accuracy, precision, recall, and confusion matrix using torchmetrics.
    Supports multiple averaging modes (micro, macro, weighted, none).

    Attributes:
        f1_type (List): List of averaging modes for F1 score.
        accuracy_type (List): List of averaging modes for accuracy.
        precision_type (List): List of averaging modes for precision.
        recall_type (List): List of averaging modes for recall.
        f1_f (dict): Dictionary of F1Score metric objects.
        confusion_f (MulticlassConfusionMatrix): Confusion matrix metric.
        accuracy_f (dict): Dictionary of Accuracy metric objects.
        recall_f (dict): Dictionary of Recall metric objects.
        precision_f (dict): Dictionary of Precision metric objects.
        computed (bool): Flag indicating if metrics have been computed.
        num_class (int): Number of classes.
        category_name (list, optional): Names of categories for display.
    """



    def __init__(self, num_class, device, category_name=None):
        """Initialize ClassificationStats.

        Args:
            num_class (int): Number of classes in the classification problem.
            device (str): Device to run computations on ('cpu' or 'cuda').
            category_name (list, optional): List of category names for display. Defaults to None.
        """
        #, "micro", "macro", "weighted"
        self.f1_type : List[Optional[Literal["micro", "macro", "weighted", "none"]]]= ["none", "micro"]
        self.accuracy_type: List[Optional[Literal["micro", "macro", "weighted", "none"]]] = ["micro"]
        self.precision_type: List[Optional[Literal["micro", "macro", "weighted", "none"]]] = ["none"]
        self.recall_type: List[Optional[Literal["micro", "macro", "weighted", "none"]]] = ["none"]

        self.f1_f = {t: F1Score(task="multiclass", average=t, num_classes=num_class).to(device) for t in self.f1_type}
        self.confusion_f = MulticlassConfusionMatrix(num_classes=num_class).to(device)

        self.accuracy_f = {t: Accuracy(task="multiclass", average=t, num_classes=num_class).to(device) for t in self.accuracy_type}
        self.recall_f = {t: Recall(task="multiclass", average=t, num_classes=num_class) .to(device)for t in self.recall_type}
        self.precision_f = {t: Precision(task="multiclass", average=t, num_classes=num_class).to(device) for t in self.precision_type}

        self.computed = False

        self.num_class = num_class

        self.category_name = category_name

    def compute(self, model, dataloader: DataLoader, device="cpu"):
        """Compute classification metrics on a dataset.

        Runs model inference on dataloader and accumulates metrics. Resets all metrics
        before computation.

        Args:
            model (torch.nn.Module): Model to evaluate.
            dataloader (DataLoader): DataLoader providing (inputs, labels, meta) batches.
            device (str, optional): Device to run on. Defaults to "cpu".
        """
        model = model.to(device)
        model.eval()

        [self.f1_f[t].reset() for t in self.f1_type]
        self.confusion_f.reset()
        [self.accuracy_f[t].reset() for t in self.accuracy_type]
        [self.precision_f[t].reset() for t in self.precision_type]
        [self.recall_f[t].reset() for t in self.recall_type]

        with torch.inference_mode():
            with tqdm(total=len(dataloader), desc="Batch") as pbar:
                for i, data in enumerate(dataloader):
                    # Every data instance is an input + label pair
                    inputs, labels, meta = data

                    if device is not None:
                        if isinstance(inputs, (list, tuple)):
                            inputs = tuple(map(lambda x: x.to(device), inputs))  # trace need tuple for input
                        else:
                            inputs = inputs.to(device)

                        labels = labels.to(device, non_blocking=True)

                    output = model(*inputs)

                    [self.f1_f[t](output, labels) for t in self.f1_type]
                    self.confusion_f(output, labels)
                    [self.accuracy_f[t](output, labels) for t in self.accuracy_type]
                    [self.precision_f[t](output, labels) for t in self.precision_type]
                    [self.recall_f[t](output, labels).detach() for t in self.recall_type]


        self.computed = True

    def display(self):
        """Display computed metrics to console.

        Prints category names (if provided), F1 scores, accuracy, precision, recall,
        and confusion matrix.
        """
        if self.category_name is not None:
            for i, name in enumerate(self.category_name):
                logger.info(f'{i}: {name}')

        for t, val in self.f1_f.items():
            logger.info(f'f1 {t}: {val.compute().detach().cpu().numpy()}')

        for t, val in self.accuracy_f.items():
            logger.info(f'accuracy {t}: {val.compute().detach().cpu().numpy()}')

        for t, val in self.precision_f.items():
            logger.info(f'precision {t}: {val.compute().detach().cpu().numpy()}')

        for t, val in self.recall_f.items():
            logger.info(f'recall {t}: {val.compute().detach().cpu().numpy()}')

        logger.info(f'Confusion matrix:\n{self.confusion_f.compute()}')

    def to_file(self, path):
        """Write computed metrics to a file.

        Args:
            path (str): Output file path.
        """
        with open(path, 'w') as f:

            if self.category_name is not None:
                for i, name in enumerate(self.category_name):
                    f.write(f'{i}: {name}\n')

            for t, val in self.f1_f.items():
                f.write(f'f1 {t}: {val.compute().detach().cpu().numpy()}\n')

            for t, val in self.accuracy_f.items():
                f.write(f'accuracy {t}: {val.compute().detach().cpu().numpy()}\n')

            for t, val in self.precision_f.items():
                f.write(f'precision {t}: {val.compute().detach().cpu().numpy()}\n')

            for t, val in self.recall_f.items():
                f.write(f'recall {t}: {val.compute().detach().cpu().numpy()}\n')

            confusion = self.confusion_f.compute().detach().cpu().numpy()
            n_digit = math.ceil(math.log10(confusion.max())) + 1
            np.savetxt(f, confusion, fmt=f'%{n_digit}.0d', delimiter=' ', newline=os.linesep)




class BadlyClassifyToGPKG:
    """Export misclassified samples to GeoPackage format for spatial analysis.

    Identifies samples where model predictions don't match reference labels and exports
    them as point geometries with prediction and reference label attributes.

    Attributes:
        results (list): List of misclassified sample records with geometry and properties.
    """

    def __init__(self):
        """Initialize BadlyClassifyToGPKG with empty results list."""
        self.results = []

    def compute(self, model, dataloader: DataLoader, device="cpu"):
        """Identify misclassified samples from model predictions.

        Runs inference on dataloader and stores records for samples where prediction
        differs from reference label.

        Args:
            model (torch.nn.Module): Model to evaluate.
            dataloader (DataLoader): DataLoader providing (inputs, labels, meta) batches.
                Meta must contain geometry information.
            device (str, optional): Device to run on. Defaults to "cpu".
        """

        self.results = []

        model = model.to(device)
        model.eval()

        with torch.inference_mode():
            with tqdm(total=len(dataloader), desc="Batch") as pbar:
                for i, data in enumerate(dataloader):
                    # Every data instance is an input + label pair
                    inputs, labels, meta = data

                    if device is not None:
                        if isinstance(inputs, (list, tuple)):
                            inputs = tuple(map(lambda x: x.to(device), inputs))  # trace need tuple for input
                        else:
                            inputs = inputs.to(device)

                        labels = labels.to(device, non_blocking=True)

                    output = model(*inputs)

                    output = torch.argmax(output, dim=1)
                    output = output.detach().cpu().numpy()
                    labels = labels.detach().cpu().numpy()

                    for o,l, m in zip(output, labels, meta):
                        if o != l:
                            rec ={'geometry': mapping(m.geometry),
                                  'properties': OrderedDict([
                                    ('Ref_label', int(l)),
                                    ('Pred_label', int(o)),
                                ])
                            }
                            self.results.append(rec)


    def to_file(self, path, crs="4326"):
        """Write misclassified samples to GeoPackage file.

        Args:
            path (str): Output GeoPackage file path.
            crs (str, optional): EPSG code for coordinate reference system. Defaults to "4326".
        """
        #('Class', 'float:16')

        schema= {'geometry': 'Point',
                 'properties': OrderedDict([('Ref_label', 'int'),
                                           ('Pred_label', 'int')])
                 }
        crs = from_epsg(crs)

        with fiona.open(path, 'w',
                        driver='GPKG',
                        schema=schema,
                        crs=crs) as src:

            for record in self.results:
                src.write(record)
