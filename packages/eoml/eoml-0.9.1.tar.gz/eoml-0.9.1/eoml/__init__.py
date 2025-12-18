"""
Earth Observation Machine Learning (EOML) Package.

This package provides tools and utilities for processing Earth observation data
and machine learning workflows for remote sensing applications. It includes modules
for data processing, raster operations, neural network training, and automation.

The package is organized into the following main modules:
- automation: Task automation and experiment configuration
- data: Data structures and persistence utilities
- ee: Google Earth Engine integration
- raster: Raster data reading and processing
- torch: PyTorch-based machine learning models and training
- bin: Command-line utilities
"""

default_read_profile = {'num_threads': 'all_cpus'}  #'all_cpus'

default_write_profile = {'driver': 'GTiff',
                        'BIGTIFF':  'IF_SAFER',
                        'num_threads': 'all_cpus',
                        'tiled': True,
                        'blockxsize': 512,
                        'blockysize': 512,
                        'compress': 'zstd'}


def get_read_profile(**kargs):
    """
    Get a default reasonable TIFF reader profile.

    Returns a profile dictionary with default settings for reading GeoTIFF files
    using rasterio. The default profile uses all available CPU threads for reading.

    Args:
        **kargs: Additional keyword arguments to override default profile settings.

    Returns:
        dict: A profile dictionary suitable for use with rasterio.open().

    Examples:
        >>> profile = get_read_profile()
        >>> profile = get_read_profile(num_threads=4)
    """
    profile = default_read_profile.copy()
    profile.update(kargs)
    return profile


def get_write_profile(**kargs):
    """
    Get a default reasonable TIFF writer profile.

    Returns a profile dictionary with default settings for writing GeoTIFF files
    using rasterio. The default profile uses:
    - GTiff driver
    - ZSTD compression
    - Tiled format with 512x512 blocks
    - All available CPU threads
    - BIGTIFF when safer

    Args:
        **kargs: Additional keyword arguments to override default profile settings.

    Returns:
        dict: A profile dictionary suitable for use with rasterio.open() in write mode.

    Examples:
        >>> profile = get_write_profile()
        >>> profile = get_write_profile(compress='lzw', num_threads=4)
    """
    profile = default_write_profile.copy()
    profile.update(kargs)
    return profile
