"""
Experience information module for machine learning experiments.

This module defines data structures for storing experiment information including
raster readers, mappers, transformers, and spatial bounds for ML experiments.
"""
import logging
from pathlib import Path
from typing import Any, Optional, Dict, List, Union, Literal
import tomli
from pydantic import BaseModel, Field, field_validator, model_validator, FilePath

from eoml.automation.configuration import SystemConfigModel
from eoml.raster.raster_utils import read_gdal_stats, SigmaNormalizer

logger = logging.getLogger(__name__)

from eoml.raster.raster_reader import RasterReader, MultiRasterReader, append_raster_reader
from eoml.raster.band import Band
from eoml.torch.cnn.db_dataset import Mapper
from eoml.torch.cnn.outputs_transformer import OutputTransformer


class MapperCategoryConfig(BaseModel):
    """Configuration for a single mapper category."""

    name: str = Field(
        ...,
        description="Name of the output category"
    )

    labels: List[Union[int, str]] = Field(
        ...,
        description="List of input labels that map to this category",
        min_length=1
    )

    map_value: Optional[int] = Field(
        None,
        description="Output value for this category. If None, uses category index"
    )


class MapperConfig(BaseModel):
    """Configuration for the label mapper."""

    no_target: int = Field(
        -1,
        description="Value to use for invalid/missing labels"
    )

    vectorize: bool = Field(
        False,
        description="Whether to use one-hot vector outputs instead of scalar"
    )

    label_dictionary: Optional[Dict[str, int]] = Field(
        None,
        description="Optional mapping from label names to integer values"
    )

    categories: List[MapperCategoryConfig] = Field(
        ...,
        description="List of output categories",
        min_length=1
    )

    def build_mapper(self) -> Mapper:
        """Build a Mapper instance from this configuration."""
        mapper = Mapper(
            no_target=self.no_target,
            vectorize=self.vectorize,
            label_dictionary=self.label_dictionary
        )

        for category in self.categories:
            mapper.add_category(
                name=category.name,
                labels=category.labels,
                map_value=category.map_value
            )

        return mapper


class RasterReaderConfig(BaseModel):
    """Configuration for a single raster reader."""

    type: Literal["single"] = Field(
        "single",
        description="Type of raster reader"
    )

    path: FilePath = Field(
        ...,
        description="Path to the raster file"
    )

    bands: Optional[List[int]] = Field(
        None,
        description="List of band indices to use (1-indexed). If None, uses all bands"
    )

    stats_path: Optional[FilePath] = Field(
        None,
        description="Path to statistics file for normalization"
    )

    interpolation: Optional[str] = Field(
        None,
        description="Interpolation method for resampling"
    )

    read_profile: Optional[Dict[str, Any]] = Field(
        None,
        description="Rasterio read profile configuration"
    )

    sharing: bool = Field(
        False,
        description="Enable file sharing mode"
    )

    def build_reader(self) -> RasterReader:
        """Build a RasterReader instance from this configuration."""
        # Create Band object
        if self.bands is not None:
            band = Band(self.bands)
        else:
            band = Band.from_file(self.path)

        # Load transformer (normalizer) if stats provided
        normalizers = None
        if self.stats_path:
            raster_stat = read_gdal_stats(self.stats_path)

            normalizers = SigmaNormalizer(raster_stat[band.selected, 0],
                                          raster_stat[band.selected, 1],
                                          3, True, 0)


        return RasterReader(
            path=self.path,
            bands_list=band,
            transformer=normalizers,
            interpolation=self.interpolation,
            read_profile=self.read_profile,
            sharing=self.sharing
        )


class MultiRasterReaderConfig(BaseModel):
    """Configuration for multiple raster readers."""

    type: Literal["multi"] = Field(
        "multi",
        description="Type of raster reader"
    )

    readers: List[RasterReaderConfig] = Field(
        ...,
        description="List of raster reader configurations",
        min_length=1
    )

    reference_index: int = Field(
        0,
        description="Index of the reader to use as spatial reference",
        ge=0
    )

    read_profile: Optional[Dict[str, Any]] = Field(
        None,
        description="Rasterio read profile configuration"
    )

    sharing: bool = Field(
        False,
        description="Enable file sharing mode"
    )

    @field_validator('reference_index')
    @classmethod
    def validate_reference_index(cls, v, info):
        """Ensure reference_index is within bounds of readers list."""
        readers = info.data.get('readers', [])
        if readers and v >= len(readers):
            raise ValueError(f"reference_index {v} is out of bounds for {len(readers)} readers")
        return v

    def build_reader(self) -> MultiRasterReader:
        """Build a MultiRasterReader instance from this configuration."""
        readers_list = [r.build_reader() for r in self.readers]

        return append_raster_reader(
            readers_list,
            reference_index=self.reference_index,
            read_profile=self.read_profile,
            sharing=self.sharing
        )


class BoundariesConfig(BaseModel):
    """Configuration for spatial boundaries and masks."""

    map_bounds: Optional[List[float]] = Field(
        None,
        description="Spatial bounds for mapping [minx, miny, maxx, maxy]",
        min_length=4,
        max_length=4
    )

    map_mask: Optional[FilePath] = Field(
        None,
        description="Path to mask defining valid mapping areas"
    )

    sample_mask: Optional[FilePath] = Field(
        None,
        description="Path to mask for filtering training/validation samples"
    )

    @field_validator('map_bounds')
    @classmethod
    def validate_bounds(cls, v):
        """Ensure bounds are valid [minx, miny, maxx, maxy]."""
        if v is not None:
            if len(v) != 4:
                raise ValueError("map_bounds must contain exactly 4 values [minx, miny, maxx, maxy]")
        return v


class ExperimentConfig(BaseModel):
    """Configuration for experiment parameters."""

    gps_file: FilePath = Field(
        ...,
        description="Name of the geopackage file (without extension)"
    )

    extract_size: int = Field(
        47,
        description="Size of extracted windows from raster data",
        gt=0
    )

    size: int = Field(
        31,
        description="Size of input windows for the neural network",
        gt=0
    )

    class_label: str = Field(
        "Class",
        description="Name of the class label column in the geopackage"
    )

    model_name: str = Field(
        "Resnet20",
        description="Name of the neural network model to use"
    )

    batch_mult: float = Field(
        0.25,
        description="Batch size multiplier for training",
        gt=0
    )

    batch_mult_map: float = Field(
        0.5,
        description="Batch size multiplier for mapping",
        gt=0
    )

    epoch: int = Field(
        1,
        description="Number of training epochs",
        gt=0
    )

    map_tag_name: Optional[str] = Field(
        None,
        description="Tag name for the mapping output"
    )

    nfold: int = Field(
        5,
        description="Number of folds for k-fold cross-validation",
        gt=0
    )

    device: Union[str, List[int]] = Field(
        "auto",
        description="Device selection: 'auto', 'cpu', 'cuda', 'gpu', or list of CUDA device IDs [0, 1, 2]"
    )

    random_seed: Optional[int] = Field(
        None,
        description="Master random seed for reproducibility. If None, a random seed will be generated. "
                    "This sets the default for all other seeds if they are not specified.",
        ge=0
    )

    python_seed: Optional[int] = Field(
        None,
        description="Seed for Python's random module. If None, uses random_seed.",
        ge=0
    )

    numpy_seed: Optional[int] = Field(
        None,
        description="Seed for NumPy's random number generator. If None, uses random_seed.",
        ge=0
    )

    torch_seed: Optional[int] = Field(
        None,
        description="Seed for PyTorch's random number generator. If None, uses random_seed.",
        ge=0
    )

    torch_deterministic: bool = Field(
        False,
        description="Enable deterministic behavior in PyTorch (may reduce performance). "
                    "When True, sets torch.use_deterministic_algorithms(True) and "
                    "configures cuDNN for deterministic behavior."
    )

    @field_validator('size')
    @classmethod
    def validate_size(cls, v, info):
        """Ensure size <= extract_size."""
        extract_size = info.data.get('extract_size')
        if extract_size is not None and v > extract_size:
            raise ValueError(f"size ({v}) must be <= extract_size ({extract_size})")
        return v

    @field_validator('map_tag_name')
    @classmethod
    def set_default_map_tag_name(cls, v, info):
        """Set default map_tag_name based on gps_file if not provided."""
        if v is None:
            gps_file = info.data.get('gps_file', 'CH_39_all')
            return f"CH_2022_{gps_file}"
        return v

    @field_validator('device')
    @classmethod
    def validate_device(cls, v):
        """Validate device configuration."""
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower not in ['auto', 'automatic', 'cpu', 'cuda', 'gpu']:
                raise ValueError(
                    f"Invalid device string '{v}'. Must be one of: 'auto', 'automatic', 'cpu', 'cuda', 'gpu'"
                )
            # Normalize to standard values
            if v_lower in ['automatic', 'gpu']:
                return 'auto' if v_lower == 'automatic' else 'cuda'
            return v_lower
        elif isinstance(v, list):
            # Validate list of device IDs
            if not all(isinstance(x, int) and x >= 0 for x in v):
                raise ValueError(
                    f"Device list must contain only non-negative integers, got: {v}"
                )
            if len(v) == 0:
                raise ValueError("Device list cannot be empty")
            return v
        else:
            raise ValueError(
                f"Device must be a string or list of integers, got: {type(v).__name__}"
            )

    @field_validator('random_seed')
    @classmethod
    def validate_random_seed(cls, v):
        """Validate random seed and generate one if None."""
        if v is None:
            # Generate a random seed
            import random
            import time
            return int(time.time() * 1000) % (2**31)  # Use timestamp-based seed
        return v

    @model_validator(mode='after')
    def set_default_seeds(self):
        """
        Set individual seeds based on random_seed if not specified.

        Instead of using identical seeds (which can cause correlations), we derive
        independent seeds from the master seed using a simple but effective method:
        - python_seed = random_seed + 0
        - numpy_seed = random_seed + 1
        - torch_seed = random_seed + 2

        This ensures reproducibility while avoiding unwanted correlations between RNGs.
        """
        if self.python_seed is None:
            self.python_seed = self.random_seed
        if self.numpy_seed is None:
            # Derive a different seed to avoid correlation
            self.numpy_seed = (self.random_seed + 1) % (2**31)
        if self.torch_seed is None:
            # Derive yet another different seed
            self.torch_seed = (self.random_seed + 2) % (2**31)
        return self

    def get_device(self) -> str:
        """
        Get the PyTorch device string based on configuration.

        Returns:
            str: PyTorch device string (e.g., 'cpu', 'cuda', 'cuda:0', 'cuda:1')
        """
        import torch

        if isinstance(self.device, list):
            # Use first device in list as primary
            if torch.cuda.is_available():
                return f"cuda:{self.device[0]}"
            else:
                logger.warning("CUDA not available, falling back to CPU")
                return "cpu"

        device_str = self.device.lower()

        if device_str == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        elif device_str in ['cuda', 'gpu']:
            if torch.cuda.is_available():
                return 'cuda'
            else:
                logger.warning("CUDA not available, falling back to CPU")
                return 'cpu'
        else:  # 'cpu'
            return 'cpu'

    def get_map_mode(self) -> int:
        """
        Get the mapping mode based on device configuration.

        Returns:
            int: Mapping mode (0 for CPU, 1 for GPU)
        """
        device = self.get_device()
        return 1 if device.startswith('cuda') else 0

    def initialize_seeds(self, verbose: bool = True) -> Dict[str, int]:
        """
        Initialize all random number generators with configured seeds.

        Args:
            verbose: If True, print seed information. Defaults to True.

        Returns:
            Dict[str, int]: Dictionary of all seeds that were set.
        """
        import random
        import numpy as np
        import torch

        seed_info = {
            'master_seed': self.random_seed,
            'python_seed': self.python_seed,
            'numpy_seed': self.numpy_seed,
            'torch_seed': self.torch_seed,
        }

        # Set Python random seed
        random.seed(self.python_seed)

        # Set NumPy random seed
        np.random.seed(self.numpy_seed)

        # Set PyTorch random seed
        torch.manual_seed(self.torch_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.torch_seed)

        # Configure deterministic behavior
        if self.torch_deterministic:
            torch.use_deterministic_algorithms(True)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            seed_info['deterministic'] = True

            # Set environment variable for CUDA determinism
            import os
            os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
        else:
            seed_info['deterministic'] = False

        if verbose:
            logger.info("Random seeds initialized:")
            logger.info(f"  - Master seed: {self.random_seed}")

            # Show individual seeds (with indication if they're derived or custom)
            expected_numpy = (self.random_seed + 1) % (2**31)
            expected_torch = (self.random_seed + 2) % (2**31)

            if self.python_seed == self.random_seed:
                logger.info(f"  - Python:  {self.python_seed} (derived)")
            else:
                logger.info(f"  - Python:  {self.python_seed} (custom)")

            if self.numpy_seed == expected_numpy:
                logger.info(f"  - NumPy:   {self.numpy_seed} (derived)")
            else:
                logger.info(f"  - NumPy:   {self.numpy_seed} (custom)")

            if self.torch_seed == expected_torch:
                logger.info(f"  - PyTorch: {self.torch_seed} (derived)")
            else:
                logger.info(f"  - PyTorch: {self.torch_seed} (custom)")

            if self.torch_deterministic:
                logger.info("  - Deterministic mode: ENABLED (may reduce performance)")
            else:
                logger.info("  - Deterministic mode: Disabled")

        return seed_info


class ExperienceInfo(BaseModel):
    """
    Complete configuration and runtime container for machine learning experiments.

    This class stores both the configuration (loaded from TOML) and built runtime
    components for running a machine learning experiment including data readers,
    neural network mappers, and output transformers.

    The class uses Pydantic for configuration parsing and validation. After loading,
    the raster_reader and mapper fields are automatically transformed from config
    objects to built runtime objects.

    Attributes:
        system_config: System configuration (paths, IO profiles, device/mapping settings).
        experiment: Experiment parameters (training settings, model config, etc.).
        raster_reader: Configuration (during init), then built reader object after validation.
        mapper: Configuration (during init), then built mapper object after validation.
        boundaries: Spatial boundaries and masks.
        nn_output_transformer: Built transformer for post-processing model outputs (property).
    """

    # Configuration fields
    system_config: SystemConfigModel = Field(
        None,
        description="System configuration (paths, IO profiles, device/mapping settings)"
    )

    experiment: ExperimentConfig = Field(
        default_factory=ExperimentConfig,
        description="Experiment parameters"
    )

    raster_reader: Union[RasterReaderConfig, MultiRasterReaderConfig] = Field(
        ...,
        description="Raster reader configuration",
        discriminator='type'
    )

    mapper: MapperConfig = Field(
        ...,
        description="Label mapper configuration"
    )

    boundaries: BoundariesConfig = Field(
        default_factory=BoundariesConfig,
        description="Spatial boundaries and masks"
    )

    # Runtime objects (stored privately, exposed via properties after building)
    _built_raster_reader: Optional[Any] = None
    _built_mapper: Optional[Any] = None
    _built_nn_output_transformer: Optional[Any] = None

    @model_validator(mode='after')
    def build_runtime_objects(self):
        """Build runtime objects from configuration."""
        # Build and store runtime objects
        self._built_raster_reader = self.raster_reader.build_reader()
        self._built_mapper = self.mapper.build_mapper()
        self._built_nn_output_transformer = self._built_mapper.map_output_transformer()

        # Override the config fields with runtime objects for backward compatibility
        object.__setattr__(self, 'raster_reader', self._built_raster_reader)
        object.__setattr__(self, 'mapper', self._built_mapper)

        return self

    @property
    def nn_output_transformer(self) -> Any:
        """Get the built neural network output transformer."""
        return self._built_nn_output_transformer

    @classmethod
    def from_toml(cls, toml_path: str) -> "ExperienceInfo":
        """Load ExperienceInfo from a TOML configuration file with full validation.

        This method loads and validates the configuration using Pydantic,
        then automatically builds all runtime objects.

        Args:
            toml_path: Path to the TOML configuration file.

        Returns:
            ExperienceInfo: Fully configured and validated experiment information object.

        Raises:
            ValidationError: If the TOML configuration is invalid.
            FileNotFoundError: If the TOML file doesn't exist.
        """
        with open(toml_path, 'rb') as f:
            config_dict = tomli.load(f)

        # Pydantic will validate and build runtime objects automatically
        return cls(**config_dict)
