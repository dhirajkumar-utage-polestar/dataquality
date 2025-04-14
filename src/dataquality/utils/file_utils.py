import glob
import os

import yaml


def check_file_exists(file_path):
    """
    Checks if the file exists and raises an exception if it doesn't.

    :param file_path: The path to the file.
    :raises FileNotFoundError: If the file doesn't exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at '{file_path}' does not exist.")


def get_file_size_in_bytes(file_path):
    """
    Returns the size of the file in bytes.

    :param file_path: The path to the file.
    :return: File size in bytes.
    """
    check_file_exists(file_path)
    return os.path.getsize(file_path)


def convert_size_to_unit(file_size_bytes, unit='bytes'):
    """
    Converts the file size from bytes to the specified unit.

    :param file_size_bytes: The file size in bytes.
    :param unit: The unit to convert to ('bytes', 'kb', 'mb', 'gb').
    :return: File size in the specified unit.
    :raises ValueError: If the unit is unsupported.
    """
    if unit == 'bytes':
        return file_size_bytes
    elif unit == 'kb':
        return file_size_bytes / 1024  # Convert bytes to kilobytes
    elif unit == 'mb':
        return file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes
    elif unit == 'gb':
        return file_size_bytes / (1024 * 1024 * 1024)  # Convert bytes to gigabytes
    else:
        raise ValueError("Unsupported unit. Please use 'bytes', 'kb', 'mb', or 'gb'.")


def get_file_size(file_path, unit='bytes'):
    """
    Returns the size of the file in the specified unit, after checking if the file exists.

    :param file_path: The path to the file.
    :param unit: The unit in which to return the file size ('bytes', 'kb', 'mb', 'gb').
    :return: File size in the specified unit.
    :raises ValueError: If an unsupported unit is specified.
    :raises FileNotFoundError: If the file doesn't exist at the given path.
    """

    file_size_bytes = get_file_size_in_bytes(file_path)
    return convert_size_to_unit(file_size_bytes, unit)


def list_files_recursive(file_path: str):
    """A method to list files recursively using glob.iglob()"""
    if os.path.isdir(file_path):
        # Using iglob with '**' to search recursively
        pattern = os.path.join(file_path, '**', '*')
        for file_name in glob.iglob(pattern, recursive=True):
            yield file_name
    else:
        raise ValueError(f"The provided path {file_path} is not a directory.")


def load_yaml_config(file_path: str) -> dict:
    """  Load the yaml file and Parse
    :param file_path:
    :return:
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except:
        print("Invalid file YAML")
        raise ("Invalid file YAML")
