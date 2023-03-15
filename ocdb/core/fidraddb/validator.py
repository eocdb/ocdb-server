def read_lines_split_and_strip(csv_f):
    csv = csv_f.readlines()
    for i in range(len(csv)):
        split = csv[i].split(';')
        csv[i] = split
        for j in range(len(split)):
            split[j] = split[j].strip()
    return csv


def transpose_list_per_row_to_list_per_column(csv: list):
    ensure_is_a_list_of_lists(csv)

    cols = list(zip(*csv))
    for j in range(len(cols)):
        cols[j] = list(cols[j])
    return cols


def ensure_is_a_list_of_lists(list_obj):
    type_error = TypeError("list of lists expected")
    if not isinstance(list_obj, list):
        raise type_error

    for item in list_obj:
        if not isinstance(item, list):
            raise type_error


def fill_function_columns(columns: list[list], columNames: list[str]):
    colsToBeFilled = []
    for columName in columNames:
        if columName.strip().startswith("F_"):
            colsToBeFilled.append(columNames.index(columName))
    functionsColumn = columns[columNames.index("Function")]
    for i in colsToBeFilled:
        currentColumn = columns[i]
        for j in range(len(currentColumn)):
            if currentColumn[j] == '':
                currentColumn[j] = functionsColumn[j]


class CalCharValidator:

    def __init__(self, path_to_csv_configuration_file: str) -> None:
        super().__init__()
        self.col_names = []
        self.configs = {}
        with open(path_to_csv_configuration_file) as csv_f:
            self.initialize(csv_f)

    def initialize(self, csv_f):
        csv = read_lines_split_and_strip(csv_f)
        self.col_names = csv.pop(0)
        cols = transpose_list_per_row_to_list_per_column(csv)
        fill_function_columns(cols)
        for col in cols:
            print(col)

        # print('DeepDiff: ', DeepDiff(cols, new_cols))


def extractFileTypeConfigurationFor(fileTypeName: str, columnNames: list, cols: list[list]):
    fileTypeColumn = cols[columnNames.index(fileTypeName)].copy()
    mandatory = []
    metadataColumn = cols[columnNames.index("Metadata")].copy()
    dataTypeColumn = cols[columnNames.index("Data type")].copy()
    functionsColumn = cols[columnNames.index("F_" + fileTypeName)].copy()

    for i in reversed(range(len(fileTypeColumn))):
        mandatoryOptionalOrExcluded = fileTypeColumn[i]
        if mandatoryOptionalOrExcluded == "x":
            metadataColumn.pop(i)
            dataTypeColumn.pop(i)
            functionsColumn.pop(i)
        elif mandatoryOptionalOrExcluded == "M":
            mandatory.append(metadataColumn[i])

    mandatory.reverse()
    return {
        "File type": fileTypeName,
        "Mandatory": mandatory,
        "Metadata": metadataColumn,
        "Data type": dataTypeColumn,
        "Functions": functionsColumn
    }
