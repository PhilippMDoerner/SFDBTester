from pathlib import Path


def get_resource_filepath(resource_name):
    """Returns the absolute filepath of a file in the resource folder."""
    base_path = Path(__file__).parent
    file_path = (base_path / f'../resources/{resource_name}').resolve()
    return file_path
