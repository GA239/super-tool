import os
import hashlib
from typing import AnyStr, BinaryIO, Callable


def duplicates_printer(duplicates: dict) -> None:
    """
    Displays duplicates on the screen

    :param duplicates: a dictionary of duplicates,
    where the key is a hash,
    and the value is a list of paths to the duplicate files
    :return: None
    """

    if not isinstance(duplicates, dict):
        return

    if not duplicates:
        print('Duplicates not found!')
        return

    print('Duplicates found:')
    for key, values in duplicates.items():
        print(f'---\nWith hash {key}')
        print('\n'.join(values))


def chunk_reader(f_obj: BinaryIO, chunk_size: int = 1024) -> AnyStr:
    """
    Generator that reads a file in chunks of bytes

    :param f_obj: - file object for reading chunks of bytes
    :param chunk_size: atomic chunk size
    :return: AnyStr -- chunk of file
    """
    while True:
        chunk = f_obj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename: str, hash_func: Callable = hashlib.md5) -> str:
    """
    Estimate a hash of a file named filename,
    using hash_func as hash function

    :param filename: filename
    :param hash_func: hash function
    :return: str -- hash value
    """

    hash_obj = hash_func()
    with open(filename, 'rb') as file_object:
        for chunk in chunk_reader(file_object):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def append_value_in_hash_table(table: dict, value: str,
                               key: str) -> None:
    """
    Adds a value to the hash table by key.
    if there is already an entry in the key,
    it adds a value to the list.
    If there are no records for the key,
    creates a new list and adds the value

    :param table: hash-table
    :param value: value
    :param key: key
    """

    if table.get(key):
        table[key].append(value)
    else:
        table[key] = []  # create the list for this file size
        table[key].append(value)


def check_for_duplicates_by_size(path: str) -> tuple:
    """
    Creates a tuple that contains paths to files with the same size

    :param path: path to the directory, with files to check
    :return: tuple that contains paths to files
    """

    hashes_by_size = {}
    for dir_path, dir_names, file_names in os.walk(path):
        for filename in file_names:
            full_path = os.path.join(dir_path, filename)
            append_value_in_hash_table(hashes_by_size, full_path,
                                       os.path.getsize(full_path))

    # We are interested only in those elements of the dictionary,
    # the length of which is more than 1
    return tuple(filter(lambda entry: len(entry) > 1,
                        hashes_by_size.values()))


def check_for_duplicates(path: str) -> (dict, None):
    """
    Creates a dictionary where the key is the hash of the files,
    and the values ​​are lists of the paths to the files
    whose hash matches the key

    :param path: path to the directory, with files to check
    :return: dictionary that contains a list of paths to the same files
    """

    if not os.path.exists(path):
        print('directory is not exist!')
        return None

    hashes = {}
    # For all files with the same file size, get their hash
    for files in check_for_duplicates_by_size(path):
        for filename in files:
            append_value_in_hash_table(hashes, filename,
                                       get_hash(filename))

    # We are interested only in those elements of the dictionary,
    # the length of which is more than 1
    return dict(filter(lambda entry: len(entry[1]) > 1,
                       hashes.items()))


if __name__ == '__main__':  # pragma: no cover
    pass
