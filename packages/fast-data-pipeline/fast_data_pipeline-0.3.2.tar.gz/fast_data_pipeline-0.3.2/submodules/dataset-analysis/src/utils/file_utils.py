from pathlib import Path


def get_files_from_directory(
    directory: str | Path, extensions: tuple | list = None, include_subfolders: bool = False
) -> list:
    """Return a list of files in a directory.

    :param directory: Directory to iterate over.
    :type directory: str | Path
    :param extensions: List of valid file extensions, defaults to None
    :type extensions: tuple | list, optional
    :param include_subfolders: _description_, defaults to False
    :type include_subfolders: bool, optional
    """
    if isinstance(directory, str):
        directory = Path(directory)

    directory: Path = directory.resolve(strict=True)
    extensions: tuple = tuple(extensions) if extensions else None
    include_subfolders: bool = include_subfolders

    valid_files = []

    if include_subfolders:
        files = directory.rglob("*.*")
    else:
        files = directory.glob("*.*")
    for file in list(files):
        if file.is_file() and (not extensions or file.suffix in extensions):
            valid_files.append(file)

    return valid_files
