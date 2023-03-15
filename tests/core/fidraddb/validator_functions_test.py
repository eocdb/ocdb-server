import copy
import unittest
from unittest.mock import MagicMock
import ocdb.core.fidraddb.validator as v


class ValidatorCreationTest(unittest.TestCase):

    def testThatLinesAreReadInSplittedAndStriped(self):
        # preparation
        file_mock = MagicMock()
        file_mock.readlines.return_value = [
            'abc;d ef ; ghi \n',
            ' 12; jk24;\n\t\r',
            'l;m; n;o   ;p'
        ]

        # execution
        actual = v.read_lines_split_and_strip(file_mock)

        # validation
        expected = [
            ['abc', 'd ef', 'ghi'],
            ['12', 'jk24', ''],
            ['l', 'm', 'n', 'o', 'p']
        ]
        self.assertEqual(expected, actual)

    def testThatTransposeThrowsTypeExceptionIfTheArgumentIsNotAListOfList(self):
        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column(None)
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column("aaaa")
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column(['aa', 'bb'])
        self.assertEqual('list of lists expected', str(te.exception))

        with self.assertRaises(TypeError) as te:
            v.transpose_list_per_row_to_list_per_column([('aa', 'bb')])
        self.assertEqual('list of lists expected', str(te.exception))

        # valid
        v.transpose_list_per_row_to_list_per_column([['aa', 'bb']])

    def testTransositionFromRowsToColumns(self):
        # preparation
        rows = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        # execution
        columns = v.transpose_list_per_row_to_list_per_column(rows)

        # validation
        expected = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        self.assertEqual(expected, columns)

    def testThatGapsInFileTypeFunctionColumnsAreFilled(self):
        # preparation
        columnNames = ["any", "F_ab", "ANY", "Function", "Any", "F_cd"]
        cols = [
            [11, 12, 13, 14, 15],  # column any
            ["", "w", "", "v", ""],  # column F_ab
            [21, 22, 23, 24, 25],  # column ANY
            ["a", "b", "c", "d", "e"],  # column Function
            [31, 32, 33, 34, 35],  # column Any
            ["z", "", "y", "", "x"],  # column F_cd
        ]
        expected = copy.deepcopy(cols)

        # execution
        v.fill_function_columns(cols, columnNames)

        # validation
        expected[1] = ["a", "w", "c", "v", "e"]
        expected[5] = ["z", "b", "y", "d", "x"]
        self.assertEqual(expected, cols)

    def testGetFileTypeConfiguration(self):
        # preparation
        columnNames = ["Metadata", "FT1", "FT2", "Data type", "Function", "F_FT1", "F_FT2"]
        cols = [
            ["a", "b", "c", "d", "e"],  # column Metadata
            ["M", "O", "M", "x", "x"],  # column FT1
            ["M", "x", "x", "M", "O"],  # column FT2
            ["d", "s", "f", "b", "f"],  # column Data type (date, strinf, float, block, float)
            ["V", "W", "X", "Y", "Z"],  # column Function
            ["", "", "Q", "", ""],  # column F_FT1
            ["", "", "", "R", ""],  # column F_FT2
        ]

        # execution
        v.fill_function_columns(cols, columnNames)
        ft1_config = v.extractFileTypeConfigurationFor("FT1", columnNames, cols)
        ft2_config = v.extractFileTypeConfigurationFor("FT2", columnNames, cols)

        # validation
        expected_ft1 = {
            "File type": "FT1",
            "Mandatory": ["a", "c"],
            "Metadata": ["a", "b", "c"],
            "Data type": ["d", "s", "f"],
            "Functions": ["V", "W", "Q"]
        }
        self.assertEqual(expected_ft1, ft1_config)

        expected_ft2 = {
            "File type": "FT2",
            "Mandatory": ["a", "d"],
            "Metadata": ["a", "d", "e"],
            "Data type": ["d", "b", "f"],
            "Functions": ["V", "R", "Z"]
        }
        self.assertEqual(expected_ft2, ft2_config)
