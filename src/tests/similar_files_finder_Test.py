from io import StringIO
from tempfile import TemporaryDirectory
import os
import random
import unittest
from unittest.mock import patch

from supertool import similar_files_finder


class HashTableTestsCase(unittest.TestCase):
    """TestCase for testing the append_value_in_hash_table function"""

    def test_append_value_in_hash_table(self):
        """
        verifies the correct addition of a value
        to the empty hash table
        """

        test_dict = {}
        similar_files_finder.append_value_in_hash_table(test_dict,
                                                        'val1', 'key1')
        self.assertDictEqual(test_dict, {'key1': ['val1', ]},
                             'Incorrect appended hash-table')

    def test_append_value_in_hash_table_with_existing_key(self):
        """
        verifies the correct addition of a value to the hash table
        with key, which contains in table
        """

        test_dict = {'key1': ['val1', ]}
        similar_files_finder.append_value_in_hash_table(test_dict,
                                                        'val2', 'key1')
        self.assertDictEqual(test_dict, {'key1': ['val1', 'val2']},
                             'Incorrect appended hash-table')

    def test_append_value_in_hash_table_with_new_key(self):
        """
        verifies the correct addition of a value to the hash table
        """

        test_dict = {'key1': ['val1', ]}
        similar_files_finder.append_value_in_hash_table(test_dict,
                                                        'val2', 'key2')
        self.assertDictEqual(test_dict, {'key1': ['val1', ], 'key2': ['val2', ]},
                             'Incorrect appended hash-table')


def create_file_with_content(file_path: str, content: str) -> None:
    """
    Creates a file with the given name
    and fills it with content

    :param file_path: path to the file being created
    :param content: content that will be filled with the file
    """

    with open(file_path, 'w') as file:
        file.write(content)


class HashReadingTestsCase(unittest.TestCase):
    """TestCase for testing the get_hash function"""

    def create_file_and_test_get_hash(self, content='',
                                      expected_hash='d41d8cd98f00b204e9800998ecf8427e'):
        """
        Creates a file with the specified content and
        checks that its hash matches the expected

        :param content: content that will be filled with the file
        :param expected_hash: expected hash of the file
        :return: None
        """

        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'tmp_file')
            create_file_with_content(file_path, content)
            self.assertEqual(similar_files_finder.get_hash(file_path),
                             expected_hash, 'hashes do not match')

    def test_get_hash_from_empty_file(self):
        """
        Checks the hash of an empty file

        :return: None
        """
        self.create_file_and_test_get_hash()

    def test_get_hash(self):
        """
        Checks the hash of an non-empty file

        :return: None
        """

        self.create_file_and_test_get_hash('text',
                                           '1cb251ec0d568de6a929b520c4aed8d1')


class SimilarFilesTestsCase(unittest.TestCase):
    """TestCase for testing the check_for_duplicates function"""

    @staticmethod
    def create_unique_files(dir_name: str) -> None:
        """
        Creates a unique file group in the specified directory

        :param dir_name: The path to the directory
        where the files will be created
        :return: None
        """

        content = 'mask for unique content__'
        for i in range(random.randint(1, 100)):
            file_path = os.path.join(dir_name, 'unique_file_' + str(i))
            create_file_with_content(file_path, content + str(i))

    @staticmethod
    def create_non_unique_files(dir_name: str) -> dict:
        """
        Creates a non-unique file groups in the specified directory

        :param dir_name: The path to the directory
        where the files will be created
        :return: dict{hash,[str]} -- a dictionary where the key is the hash of the files,
        and the values ​​are lists of the paths to the files
        whose hash matches the key
        """

        non_unique_table = {}
        file_counter = 0
        for group_number in range(random.randint(1, 10)):
            content = 'mask for non unique content__' + str(group_number)
            for i in range(random.randint(2, 10)):
                file_path = os.path.join(dir_name, str(file_counter))
                create_file_with_content(file_path, content)
                similar_files_finder.append_value_in_hash_table(non_unique_table,
                                                                file_path,
                                                                similar_files_finder.get_hash(file_path))
                file_counter += 1

        return non_unique_table

    def test_check_for_duplicates_for_unique_files(self):
        """
        Verifies the search for duplicates in a directory
        in which there are no duplicate files
        :return: None
        """
        with TemporaryDirectory() as temp_dir:
            self.create_unique_files(temp_dir)
            self.assertDictEqual(similar_files_finder.check_for_duplicates(temp_dir),
                                 {}, 'dicts for unique files do not match')

    def test_check_for_duplicates_for_empty_dir(self):
        """
        Verifies the search for duplicates in an empty dir
        :return: None
        """
        with TemporaryDirectory() as temp_dir:
            self.assertDictEqual(similar_files_finder.check_for_duplicates(temp_dir),
                                 {}, 'dicts for unique files do not match')

    def test_check_for_duplicates_for_only_non_unique_files(self):
        """
        Verifies the search for duplicates in a directory
        in which there are only duplicate files
        :return: None
        """

        with TemporaryDirectory() as temp_dir:
            non_unique_table = self.create_non_unique_files(temp_dir)
            non_unique_table_set = set((k, tuple(sorted(v)))
                                       for k, v, in non_unique_table.items())
            result_set = set((k, tuple(sorted(v)))
                             for k, v, in
                             similar_files_finder.check_for_duplicates(temp_dir).items())

            self.assertSetEqual(non_unique_table_set, result_set,
                                'dicts for unique files do not match')

    def test_check_for_duplicates_for_mixed_non_unique_and_unique_files(self):
        """
        Verifies the search for duplicates in a directory
        in which there are duplicate files and non-duplicate files
        :return: None
        """

        with TemporaryDirectory() as temp_dir:
            non_unique_table = self.create_non_unique_files(temp_dir)
            self.create_unique_files(temp_dir)
            non_unique_table_set = set((k, tuple(sorted(v)))
                                       for k, v, in non_unique_table.items())
            result_set = set((k, tuple(sorted(v)))
                             for k, v, in
                             similar_files_finder.check_for_duplicates(temp_dir).items())

            self.assertSetEqual(non_unique_table_set, result_set,
                                'dicts for unique files do not match')

    def test_duplicates_printer_empty_dir(self):
        """
        tests the representation of the dictionary with duplicates,
        if the dictionary is empty
        """

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with TemporaryDirectory() as temp_dir:
                similar_files_finder.duplicates_printer(similar_files_finder.check_for_duplicates(temp_dir))
        self.assertEqual(fake_out.getvalue().strip(),
                         'Duplicates not found!')

    def test_duplicates_no_exist_dir(self):
        """
        tests reaction on non existing directory
        """

        with patch('sys.stdout', new=StringIO()) as fake_out:
            similar_files_finder.duplicates_printer(similar_files_finder.check_for_duplicates('fake'))
        self.assertEqual(fake_out.getvalue().strip(),
                         'directory is not exist!')

    def test_duplicates_printer_unique_files(self):
        """
        tests the representation of the dictionary with duplicates,
        if the dictionary is non-empty
        """

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with TemporaryDirectory() as temp_dir:
                file_path1 = os.path.join(temp_dir, '1')
                create_file_with_content(file_path1, 'hello')
                file_path2 = os.path.join(temp_dir, '2')
                create_file_with_content(file_path2, 'hello')
                similar_files_finder.duplicates_printer(similar_files_finder.check_for_duplicates(temp_dir))
                output = 'Duplicates found:\n---\nWith hash 5d41402abc4b2a76b9719d911017c592\n'
                output += file_path1 + '\n'
                output += file_path2
            self.assertEqual(fake_out.getvalue().strip(), output)
