import os
from pathlib import Path


def get_resource_filepath(resource_name):
    """Returns the absolute filepath of a file in the resource folder."""
    base_path = Path(__file__).parent
    file_path = (base_path / f'../resources/{resource_name}').resolve()

    if not os.path.exists(file_path):
        raise ValueError(f'{file_path} does not exist!')
    elif not os.path.isfile(file_path):
        raise ValueError(f'{file_path} is not a file!')

    return str(file_path)
