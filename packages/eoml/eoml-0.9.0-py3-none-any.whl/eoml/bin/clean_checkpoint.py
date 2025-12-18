"""
Checkpoint cleanup utility for EOML.

This command-line utility helps manage disk space by cleaning up old checkpoint
files from model training. It keeps only the N most recent files in each
subdirectory, removing older checkpoints to save space.

Usage:
    python clean_checkpoint.py <root_directory>

The script will:
1. Scan all subdirectories for files
2. Identify files sorted by modification time
3. Keep the 4 most recent files in each directory
4. Remove older files after user confirmation
5. Report disk space saved
"""

import os
import typer
from pathlib import Path
from datetime import datetime


def get_dir_size(path):
    """
    Calculate total size of directory in bytes.

    Recursively computes the total size of all files in a directory and its
    subdirectories.

    Args:
        path (str or Path): Path to the directory to measure.

    Returns:
        int: Total size in bytes.

    Examples:
        >>> size = get_dir_size("/path/to/checkpoints")
        >>> print(f"Directory size: {size / (1024**3):.2f} GB")
    """
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def get_files_by_time(directory):
    """
    Get list of files sorted by modification time.

    Retrieves all files in a directory and sorts them by modification time
    in descending order (most recent first).

    Args:
        directory (str or Path): Path to the directory to scan.

    Returns:
        list: List of os.DirEntry objects sorted by modification time (newest first).

    Examples:
        >>> files = get_files_by_time("/path/to/checkpoints")
        >>> most_recent = files[0]  # Most recently modified file
    """
    files = []
    with os.scandir(directory) as it:
        for entry in it:
            if entry.is_file():
                files.append(entry)
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)


app = typer.Typer()


@app.command()
def cleanup_folders(
        root_dir: Path = typer.Argument(
            ...,
            exists=True,
            dir_okay=True,
            file_okay=False,
            help="Root directory to clean up"
        )
):
    """
    Clean up folders by keeping only 4 most recent files.

    This command scans all subdirectories under root_dir and keeps only the
    4 most recently modified files in each directory, removing older files
    to save disk space.

    Args:
        root_dir (Path): Root directory containing subdirectories with checkpoint files.

    The function will:
    - Show a list of files to be removed
    - Ask for user confirmation before deleting
    - Report the amount of disk space saved
    - Display the number of files removed

    Examples:
        To clean up a checkpoints directory:
        $ python clean_checkpoint.py /path/to/checkpoints
    """
    root_path = Path(root_dir)
    initial_size = get_dir_size(root_path)

    files_to_remove = []

    # Collect files to remove
    for folder in root_path.glob('*/'):
        if folder.is_dir():
            files = get_files_by_time(folder)
            if len(files) > 4:
                files_to_remove.extend([f.path for f in files[4:]])

    if not files_to_remove:
        typer.echo("No files need to be removed.")
        return

    # Show files to be removed
    typer.echo(f"The following {len(files_to_remove)} files will be removed:")
    for file in files_to_remove:
        typer.echo(f"  {file}")

    # Ask for confirmation
    if typer.confirm('Do you want to proceed?'):
        for file in files_to_remove:
            os.remove(file)

        final_size = get_dir_size(root_path)
        saved = initial_size - final_size

        typer.echo(f"\nSpace saved: {saved / (1024 * 1024):.2f} MB")
        typer.echo(f"Number of files removed: {len(files_to_remove)}")
    else:
        typer.echo("Operation cancelled.")


if __name__ == '__main__':
    app()
