"""Model evaluation utilities for PyTorch datasets.

This module provides classes for evaluating trained neural network models on
datasets, collecting predictions and reference values for analysis.
"""

import numpy as np
import torch
from tqdm import tqdm


class DatasetEvaluator:
    """Evaluate a neural network model on a dataset.

    Runs inference on a complete dataset and collects predictions along with
    reference labels for evaluation metrics.

    Todo:
        Implement aggressive/optimized version.

    Attributes:
        model: PyTorch model or path to JIT-compiled model.
    """
    def __init__(self, model):

        if isinstance(model, str):
            self.model = torch.jit.load(model)
        else:
            self.model = model

    def evaluate(self, loader, device="cpu"):
        """Evaluate model on dataset and collect predictions.

        Args:
            loader: PyTorch DataLoader providing test samples.
            device: Device to run inference on ('cpu' or 'cuda'). Defaults to "cpu".

        Returns:
            tuple: (reference_labels, predictions) as numpy arrays.
        """

        # Make sure gradient tracking is off, and do a pass over the data
        self.model.train(False)

        results=[]
        reference=[]

        with torch.inference_mode():

            with tqdm(total=len(loader),desc="Batch") as pbar:
                for i, data in enumerate(loader):
                    # Every data instance is an input + label pair

                    inputs, labels = data
                    if device is not None:
                        if isinstance(inputs, (list, tuple)):
                            inputs = map(lambda x: x.to(device, non_blocking=True), inputs)
                        else:
                            inputs = inputs.to(device, non_blocking=True)

                    # Make predictions for this batch
                    outputs = self.model(*inputs)

                    results.extend(outputs.cpu())
                    reference.extend(labels)

        return np.array(reference), np.array(results)

