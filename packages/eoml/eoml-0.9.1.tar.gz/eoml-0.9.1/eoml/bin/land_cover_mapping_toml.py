"""
Land cover mapping script using TOML configuration.

This script demonstrates how to run a complete land cover mapping workflow
using configuration loaded from a TOML file, leveraging the ExperienceInfo
configuration system.

Usage:
    python land_cover_mapping_toml.py <path_to_config.toml>

Example:
    python land_cover_mapping_toml.py ../example_experience_config.toml
"""
import logging
import os
import sys
import random
from datetime import datetime
from pathlib import Path

import torch
from rasterio.enums import Resampling
from torch import nn
from torch.optim import AdamW

from rasterop.tiled_op.operation.mapping import CountCategoryToBand, MaxCategory, MaxScore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from eoml.automation.experience import ExperienceInfo
from eoml.automation.tasks import (
    samples_split_setup,
    samples_k_fold_setup,
    extract_sample,
    train_and_map, tiled_task,
)
from eoml.torch.cnn.augmentation import RandomTransform, CropTransform

# TODO: Import these classes from the appropriate module
# from eoml.raster.operations import CountCategoryToBand, MaxCategory, MaxScore


def run_land_cover_mapping(config_path: str):
    """
    Run the complete land cover mapping workflow from a TOML configuration.

    Args:
        config_path: Path to the TOML configuration file.
    """
    # ----------------------------------------------------------------------------------------------------------------
    # Setup
    # ----------------------------------------------------------------------------------------------------------------

    # For GPU support in multiple threads (also needed for mapping)
    torch.multiprocessing.set_start_method('spawn')

    logger.info(f"Loading configuration from: {config_path}")

    # ----------------------------------------------------------------------------------------------------------------
    # Load Configuration from TOML
    # ----------------------------------------------------------------------------------------------------------------

    # Load and validate the experience configuration
    experience = ExperienceInfo.from_toml(config_path)

    logger.info("Configuration loaded successfully!")
    logger.info(f"  GPS file: {experience.experiment.gps_file}")
    logger.info(f"  Model: {experience.experiment.model_name}")
    logger.info(f"  Extract size: {experience.experiment.extract_size}")
    logger.info(f"  Network size: {experience.experiment.size}")
    logger.info(f"  Epochs: {experience.experiment.epoch}")
    logger.info(f"  Batch multiplier: {experience.experiment.batch_mult}")
    logger.info(f"  N-fold: {experience.experiment.nfold}")

    # Extract runtime objects from experience
    raster_reader = experience.raster_reader
    mapper_full = experience.mapper
    nn_output_transformer = experience.nn_output_transformer
    system_config = experience.system_config

    # Extract configuration values for convenient access
    map_bounds = experience.boundaries.map_bounds
    map_mask = experience.boundaries.map_mask
    sample_mask = experience.boundaries.sample_mask
    gps_file = experience.experiment.gps_file
    extract_size = experience.experiment.extract_size
    size = experience.experiment.size
    class_label = experience.experiment.class_label
    model_name = experience.experiment.model_name
    batch_mult = experience.experiment.batch_mult
    batch_mult_map = experience.experiment.batch_mult_map
    epoch = experience.experiment.epoch
    map_tag_name = experience.experiment.map_tag_name
    nfold = experience.experiment.nfold

    # ----------------------------------------------------------------------------------------------------------------
    # Random Seed Configuration
    # ----------------------------------------------------------------------------------------------------------------

    # Initialize all random seeds (Python, NumPy, PyTorch) and set deterministic mode if configured
    seed_info = experience.experiment.initialize_seeds(verbose=True)

    # ----------------------------------------------------------------------------------------------------------------
    # Device Configuration
    # ----------------------------------------------------------------------------------------------------------------

    device = experience.experiment.get_device()
    map_mode = experience.experiment.get_map_mode()

    logger.info(f"  Device: {device} (mode: {map_mode})")

    # Log additional device info for multi-GPU setup
    if isinstance(experience.experiment.device, list):
        logger.info(f"  Available GPUs: {experience.experiment.device}")
        if torch.cuda.is_available():
            for gpu_id in experience.experiment.device:
                if gpu_id < torch.cuda.device_count():
                    logger.info(f"    - GPU {gpu_id}: {torch.cuda.get_device_name(gpu_id)}")
                else:
                    logger.warning(f"    - GPU {gpu_id}: Not available")

    # ----------------------------------------------------------------------------------------------------------------
    # File Path Management
    # ----------------------------------------------------------------------------------------------------------------

    gps_path = gps_file
    db_path = f"{system_config.data_dir}/land_cover/samples/{gps_file.stem}_lmdb_NaN_to_0_{extract_size}"

    # Training output paths
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_name = f"ch-{timestamp}"
    run_stats_dir = f"{system_config.data_dir}/land_cover/nn_run_stats"
    model_base_path = f"{system_config.data_dir}/land_cover/nn/{run_name}"

    logger.info(f"Output directory: {model_base_path}")

    # ----------------------------------------------------------------------------------------------------------------
    # Sample Extraction Configuration
    # ----------------------------------------------------------------------------------------------------------------

    extractor_param = {
        "gps_path": gps_path,
        "raster_reader": raster_reader,
        "db_path": db_path,
        "windows_size": extract_size,
        "label_name": class_label,
        "mask_path": sample_mask,
        "force_write": False
    }

    # ----------------------------------------------------------------------------------------------------------------
    # Sample Split Configuration (K-Fold or Simple Split)
    # ----------------------------------------------------------------------------------------------------------------

    # K-fold cross-validation (recommended)
    sample_param_kfold = {
        "methode": samples_k_fold_setup,
        "param": {
            "db_path": db_path,
            "mapper": mapper_full,
            "n_fold": nfold
        }
    }

    # Simple train/validation split (alternative)
    sample_param_split = {
        "methode": samples_split_setup,
        "param": {
            "db_path": db_path,
            "mapper": mapper_full,
            "split": [0.8, 0.2]
        }
    }

    # Use K-fold by default
    sample_param = sample_param_kfold

    # ----------------------------------------------------------------------------------------------------------------
    # Data Augmentation Configuration
    # ----------------------------------------------------------------------------------------------------------------

    augmentation_param = {
        "methode": "no_dep",
        "transform_train": RandomTransform(
            width=size,
            p_rot=0.90,
            p_flip=0.50,
            p_scale=0.4,
            p_shear=0.3,
            p_blur=0.3
        ),
        "transform_valid": CropTransform(size)
    }

    # ----------------------------------------------------------------------------------------------------------------
    # DataLoader Configuration
    # ----------------------------------------------------------------------------------------------------------------

    dataloader_parameter = {
        "batch_size": int(batch_mult * 1024),
        "num_worker": 5,
        "prefetch": 1,
        "device": device,
        "balance_sample": False,
        "persistent_workers": True
    }

    # ----------------------------------------------------------------------------------------------------------------
    # Neural Network Configuration
    # ----------------------------------------------------------------------------------------------------------------

    nn_parameter = {
        "in_size": size,
        "n_bands": raster_reader.n_band,
        "n_out": len(mapper_full)
    }

    model_parameter = {
        "model_name": model_name,
        "type": "normal",
        "path": None,
        "device": device,
        "nn_parameter": nn_parameter
    }

    # ----------------------------------------------------------------------------------------------------------------
    # Optimizer Configuration
    # ----------------------------------------------------------------------------------------------------------------

    optimizer_parameter = {
        "loss": nn.CrossEntropyLoss(),
        "optimizer": AdamW,
        "optimizer_parameter": {
            "lr": 1.5 * 0.018 * 1e-2,
            "weight_decay": 0.001 * 0.0020
        },
        "scheduler_mode": "cycle",
        "scheduler_parameter": {
            "max_lr": 0.0008
        }
    }

    # ----------------------------------------------------------------------------------------------------------------
    # Training Configuration
    # ----------------------------------------------------------------------------------------------------------------

    dataset_parameter = {
        "db_path": db_path,
        "mapper": mapper_full
    }

    train_nn_parameter = {
        "max_epochs": epoch,
        "run_stats_dir": run_stats_dir,
        "model_base_path": model_base_path,
        "model_tag": model_name,
        "grad_clip_value": 0.1,
        "device": device
    }

    train_parameter = {
        "sample_param": sample_param,
        "augmentation_param": augmentation_param,
        "dataset_parameter": dataset_parameter,
        "dataloader_parameter": dataloader_parameter,
        "model_parameter": model_parameter,
        "optimizer_parameter": optimizer_parameter,
        "train_nn_parameter": train_nn_parameter
    }

    # ----------------------------------------------------------------------------------------------------------------
    # Mapping Configuration
    # ----------------------------------------------------------------------------------------------------------------

    map_parameter = {
        "raster_reader": raster_reader,
        "windows_size": size,
        "batch_size": int(batch_mult_map * 1024),
        "map_tag": map_tag_name,
        "transformer": nn_output_transformer,
        "mask": map_mask,
        "bounds": map_bounds,
        "mode": map_mode,
        "num_worker": 7,
        "prefetch": 1
    }

    # Map modes:
    # 0 - Full CPU, no pinning
    # 1 - Pinned memory in loader, moved asynchronously to GPU (recommended for GPU)
    # 2 - Start CUDA in each thread, prepare samples directly on GPU
    #     (uses ~1GB per thread, requires torch.multiprocessing.set_start_method('spawn'))

    train_map_parameter = train_parameter.copy()
    train_map_parameter.update({"map_parameter": map_parameter})

    # ----------------------------------------------------------------------------------------------------------------
    # Execute Workflow
    # ----------------------------------------------------------------------------------------------------------------

    logger.info("=" * 80)
    logger.info("STARTING LAND COVER MAPPING WORKFLOW")
    logger.info("=" * 80)

    # Create output directory
    os.makedirs(model_base_path, exist_ok=True)

    # Save configuration log
    with open(f"{model_base_path}/log.txt", "w") as log:
        log.write(repr(train_map_parameter))

    # Copy TOML configuration to output directory for reference
    import shutil
    shutil.copy(config_path, f"{model_base_path}/config.toml")
    logger.info(f"Configuration saved to: {model_base_path}/config.toml")

    # Step 1: Extract samples from raster data
    logger.info("[1/4] Extracting samples from raster data...")
    extract_sample(**extractor_param)
    logger.info("✓ Sample extraction complete")

    # Step 2: Train model and generate maps
    logger.info("[2/4] Training model and generating maps...")
    maps = train_and_map(**train_map_parameter)
    logger.info(f"✓ Training complete, generated {len(maps)} maps")

    # ----------------------------------------------------------------------------------------------------------------
    # Post-Processing: Merge and Aggregate Maps
    # ----------------------------------------------------------------------------------------------------------------

    logger.info("[3/4] Post-processing maps...")

    raster_out_merge = f"{model_base_path}/01_{run_name}_merged.tif"
    raster_out_score = f"{model_base_path}/02_{run_name}_max_arg.tif"
    raster_out_score_max = f"{model_base_path}/02_{run_name}_max_score.tif"

    default_op_param = {
        "bounds": map_bounds,
        "res": None,
        "resampling": Resampling.nearest,
        "target_aligned_pixels": False,
        "indexes": None,
        "src_kwds": None,
        "dst_kwds": None,
        "num_workers": 8
    }

    # TODO: Uncomment when CountCategoryToBand, MaxCategory, MaxScore are available
    #
    # Count categories across all maps
    category_count_op = CountCategoryToBand(max(mapper_full.map_values()), dtype="int16")
    category_count_param = {
        "maps": maps,
        "raster_out": raster_out_merge,
        "operation": category_count_op
    }
    category_count_param.update(default_op_param)

    # Find maximum category (mode)
    category_max_op = MaxCategory()
    category_max_param = {
        "maps": [raster_out_merge],
        "raster_out": raster_out_score,
        "operation": category_max_op
    }
    category_max_param.update(default_op_param)

    # Find maximum score (confidence)
    category_max_score_op = MaxScore()
    category_max_score_param = {
        "maps": [raster_out_merge],
        "raster_out": raster_out_score_max,
        "operation": category_max_score_op
    }
    category_max_score_param.update(default_op_param)

    # Execute tiled operations
    logger.info(f"  - Merging {len(maps)} maps...")
    tiled_task(**category_count_param)
    logger.info("  - Computing maximum category...")
    tiled_task(**category_max_param)
    logger.info("  - Computing maximum score...")
    tiled_task(**category_max_score_param)
    #
    # logger.info("✓ Post-processing complete")

    logger.warning("Post-processing operations are commented out.")
    logger.warning("Uncomment the operations in the code once the required classes are available.")

    # ----------------------------------------------------------------------------------------------------------------
    # Done
    # ----------------------------------------------------------------------------------------------------------------

    logger.info("[4/4] Workflow complete!")
    logger.info("=" * 80)
    logger.info("RESULTS")
    logger.info("=" * 80)
    logger.info(f"Output directory: {model_base_path}")
    logger.info(f"Maps generated: {len(maps)}")
    for i, map_path in enumerate(maps, 1):
        logger.info(f"  [{i}] {map_path}")
    # logger.info(f"\nMerged output: {raster_out_merge}")
    # logger.info(f"Category map: {raster_out_score}")
    # logger.info(f"Confidence map: {raster_out_score_max}")
    logger.info("=" * 80)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        logger.error("Usage: python land_cover_mapping_toml.py <path_to_config.toml>")
        logger.info("Example:")
        logger.info("  python land_cover_mapping_toml.py ../example_experience_config.toml")
        sys.exit(1)

    config_path = sys.argv[1]

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        run_land_cover_mapping(config_path)
    except Exception as e:
        logger.exception(f"Error during execution: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
