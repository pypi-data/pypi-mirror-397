import typer
from pathlib import Path

from rasterio.enums import Resampling

from eoml import get_read_profile, get_write_profile
from eoml.automation.tasks import tiled_task
from rasterop.tiled_op.operation import CopyFirstNonNullOP
from rasterop.tiled_op.tiled_raster_op import get_image_file, TiledOPExecutor

app = typer.Typer(help="Raster merging utility that take all the TIFF file in the input directories sorted by"
                       " alphabetical order and copies the first non-nan value to the final TIFF")

def parse_resampling(value: str) -> Resampling:
    value_norm = value.strip().lower()

    by_name = {m.name.lower(): m for m in Resampling}
    if value_norm in by_name:
        return by_name[value_norm]

    # Optional: allow numeric values too (handy for backwards-compat)
    if value_norm.isdigit():
        return Resampling(int(value_norm))

    raise typer.BadParameter(
        f"Invalid resampling '{value}'. Choose one of: {', '.join(sorted(by_name))}"
    )


@app.command()
def merge_rasters(
        input_dir: Path = typer.Argument(
            ...,
            help="Input directory containing TIFF files",
            exists=True,
            dir_okay=True,
            file_okay=False
        ),
        output_file: Path = typer.Argument(
            ...,
            help="Output TIFF file path"
        ),
        num_threads: str = typer.Option(
            "all_cpus",
            "--threads", "-t",
            help="Number of threads to use by gdal for compression"
        ),
        block_size: int = typer.Option(
            256,
            "--block-size", "-b",
            help="Block size for x and y dimensions for the geotiff internal structure"
        ),
        tile_size: int = typer.Option(
            2028,
            "--tile-size", "-T",
            help="Block size for the operation"
        ),
        num_workers: int = typer.Option(
            8,
            "--workers", "-w",
            help="Number of workers for processing"
        ),
        resampling: Resampling = typer.Option(
            Resampling.nearest,  # internal default as enum
            "--resampling", "-r",
            callback=lambda v: parse_resampling(v) if isinstance(v, str) else v,
            help="Resampling method by name (nearest, bilinear, cubic, ...)",
        )
):
    """
    Merge multiple raster files by copying the first non-nan value to the final TIFF.
    """
    try:
        # Get the list of raster files
        rasters = get_image_file(input_dir,  extension = ["tif", "tiff", "TIF", "TIFF"])
        rasters.sort()
        if len(rasters) == 0:
            raise typer.BadParameter(f"No raster files found in {input_dir}")

        # Set up writing and reading profiles
        read_profile = get_read_profile()
        profile = get_write_profile()

        read_profile.update({'num_threads': num_threads})
        profile.update({
            "driver": "COG",
            'num_threads': num_threads,
            'blockxsize': block_size,
            'blockysize': block_size
        })

        # Set up operation parameters
        default_op_param = {
            "bounds": None,
            "res": None,
            "resampling": resampling,
            "target_aligned_pixels": False,
            "indexes": None,
            "src_kwds": None,
            "dst_kwds": None,
            "num_workers": num_workers
        }

        # Create operator and set parameters
        operator = CopyFirstNonNullOP.same_as(rasters[0])
        operator_param = {
            "maps": rasters,
            "raster_out": str(output_file),
            "operation": operator,
            "dst_kwds": profile
        }
        operator_param.update(default_op_param)

        # Execute tiled task
        typer.echo(f"Merging {len(rasters)} raster files...")

        # TiledOPExecutor(res=None,
        #          indexes=None,
        #          resampling=Resampling.nearest,
        #          target_aligned_pixels=False,
        #          dst_kwds=None,
        #          src_kwds=None,
        #          num_workers=2,
        #          window_size=None).execute(**operator_param)
        #
        #
        tiled_task(**operator_param)
        typer.echo(f"Successfully merged rasters to {output_file}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

