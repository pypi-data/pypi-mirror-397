"""
Configuration management module for EOML automation.

This module provides system-wide configuration management for EOML experiments,
including paths to data directories, raster processing profiles, and neural
network device settings.
"""

import os

import toml
from typing import Any, Dict, Union, Optional

from eoml import default_read_profile, default_write_profile

# Pydantic model for configuration (v2)
try:
    from pydantic import BaseModel, Field, AliasChoices
except Exception:  # pragma: no cover - optional import hint
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore
    class AliasChoices:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

SYSTEM_CONFIG = None

class SystemConfigModel(BaseModel):
    """
    Pydantic representation of System configuration.

    This class stores configuration settings for data directories, raster
    processing profiles, and neural network execution parameters.

    Attributes:
        data_dir (str): Base directory for data storage.
        raster_dir (str): Directory containing raster files.
        shade_dir (str): Directory for shade/canopy data.
        land_cover_dir (str): Directory for land cover data.
        raster_read_profile (dict): Rasterio profile for reading rasters.
        raster_write_profile (dict): Rasterio profile for writing rasters.
        device (str): Device for neural network execution ('cpu', 'cuda', etc.).
        mapping_mode (int): Mode for map generation (0=CPU, 1=GPU with pinned memory, etc.).
    """

    data_dir: str
    raster_dir: str
    shade_dir: str
    land_cover_dir: str
    raster_read_profile: Dict[str, Any]
    raster_write_profile: Dict[str, Any]
    device: str
    mapping_mode: int

    @classmethod
    def load_toml(cls, path: str) -> "SystemConfigModel":
        """Load a configuration model from a TOML file."""
        data = toml.load(path)
        return cls(**data)

    def set_as_global(self, name: str = "default", set_default: bool = True) -> None:
        """
        Set this configuration as a global system configuration.

        This method stores the configuration in the global SYSTEM_CONFIG dictionary
        and optionally updates the default raster read/write profiles.

        Args:
            name (str, optional): Name to store this configuration under in the
                SYSTEM_CONFIG dictionary. Defaults to "default".
            set_default (bool, optional): If True, updates the global default_read_profile
                and default_write_profile with values from this configuration.
                Defaults to True.

        Side Effects:
            - Updates global SYSTEM_CONFIG dictionary
            - Optionally updates global default_read_profile and default_write_profile

        Examples:
            >>> config = SystemConfigModel.load_toml("/path/to/config.toml")
            >>> config.set_as_global("my_config")
        """
        global SYSTEM_CONFIG

        SYSTEM_CONFIG[name] = self

        if set_default:
            default_read_profile.update(self.raster_read_profile)
            default_write_profile.update(self.raster_write_profile)




def get_config() -> Optional[SystemConfigModel]:
    """
    Retrieve a stored system configuration by name.

    Returns:
        SystemConfig: The requested configuration object.

    Examples:
        >>> config = get_config()
    """
    return SYSTEM_CONFIG

