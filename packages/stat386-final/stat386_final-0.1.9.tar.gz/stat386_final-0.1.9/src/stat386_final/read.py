import pandas as pd
from importlib.resources import files, as_file

def get_data_path(filename: str):
    """
    Return a resource handle for a data file inside the package.
    Works in wheels/zip installs. Pass just the filename (e.g., 'game_data.csv').
    """
    # If your data folder is capitalized, change 'data' to 'Data'.
    return files(__package__).joinpath(f"data/{filename}")

def read_data(filename: str) -> pd.DataFrame:
    """
    Reads a CSV from the package's data directory.
    Accepts a filename (not an absolute path).
    """
    resource = get_data_path(filename)
    # as_file provides a real filesystem path even if package is zipped
    with as_file(resource) as real_path:
        sales = pd.read_csv(real_path)

    # Your cleanup logic
    sales['Year'] = sales['Year'].astype('Int64')
    if 'Unnamed: 0' in sales.columns:
        sales.drop(columns=['Unnamed: 0'], inplace=True)
    return sales