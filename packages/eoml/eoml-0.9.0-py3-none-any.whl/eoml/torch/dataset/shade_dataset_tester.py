"""Evaluation utilities for shade detection datasets.

This module provides classes for testing and evaluating shade detection models
on validation datasets.
"""

from eoml.torch.cnn.dataset_evaluator import DatasetEvaluator


class ShadeDatasetTestet:
    """Test and evaluate shade detection models on datasets.

    Note: Class name appears to be a typo (Testet instead of Tester).

    Attributes:
        rasters (list): List of raster file paths.
        datasets (list): List of dataset objects.
        metric_list (list): List of metrics to compute.
        model_path (str): Path to trained model file.
    """

    def __init__(self, rasters, datasets, metric_list, model_path):
        """Initialize ShadeDatasetTestet.

        Args:
            rasters (list): List of raster file paths for evaluation.
            datasets (list): List of dataset objects.
            metric_list (list): Metrics to compute during evaluation.
            model_path (str): Path to trained model weights.
        """
        self.rasters=rasters
        self.datasets=datasets
        self.metric_list=metric_list

        self.model_path=model_path


    def compute_metric(self):
        """Compute evaluation metrics on datasets.

        Note: Implementation appears incomplete - references undefined variables.

        Returns:
            tuple: Reference and predicted values (when properly implemented).
        """
        ref, pred = DatasetEvaluator(model_path).evaluate(train_dataloader, device=device)