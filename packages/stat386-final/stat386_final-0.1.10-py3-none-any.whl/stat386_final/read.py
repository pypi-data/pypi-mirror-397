import os
from pathlib import Path
import pandas as pd
from importlib.resources import files, as_file
from typing import Union


def _resource_path(filename: str) -> Path:
    """Return a filesystem Path for a resource inside the package data folder.

    Works for zipped wheels and normal installs. Pass just the filename
    (e.g. 'game_data.csv').
    """
    # If your data folder is capitalized, change 'data' to 'Data'.
    resource = files(__package__).joinpath(f"data/{filename}")
    with as_file(resource) as real_path:
        return Path(real_path)


def read_data(filename: Union[str, os.PathLike]) -> pd.DataFrame:
    """Read a CSV from either a user path or the package's bundled data.

    Behavior:
    - If `filename` is an absolute or relative path that exists, read it.
    - Otherwise attempt to open the bundled data file inside the package.

    This makes the function work both for users that pass a path and
    for consumers who expect to load bundled data by name.
    """
    # If caller passed a path that exists, prefer it.
    candidate = Path(filename)
    if candidate.exists():
        sales = pd.read_csv(candidate)
    else:
        # Fall back to package resource
        resource_path = _resource_path(str(filename))
        sales = pd.read_csv(resource_path)

    # Normalization/cleanup
    if 'Year' in sales.columns:
        sales['Year'] = sales['Year'].astype('Int64')
    if 'Unnamed: 0' in sales.columns:
        sales.drop(columns=['Unnamed: 0'], inplace=True)
    return sales