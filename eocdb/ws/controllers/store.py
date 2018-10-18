# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import io
import os
from typing import Dict, List

from ..context import WsContext
from ...core.asserts import assert_not_none, assert_one_of
from ...core.models.dataset_validation_result import DatasetValidationResult, DATASET_VALIDATION_RESULT_STATUS_ERROR
from ...core.models.issue import Issue, ISSUE_TYPE_ERROR
from ...core.models.uploaded_file import UploadedFile
from ...core.seabass.sb_file_reader import SbFileReader
from ...core.val import validator
from ...db.static_data import get_product_groups, get_products


# noinspection PyUnusedLocal
def get_store_info(ctx: WsContext) -> Dict:
    return dict(products=get_products(), productGroups=get_product_groups())


def upload_store_files(ctx: WsContext,
                       path: str,
                       dataset_files: List[UploadedFile],
                       doc_files: List[UploadedFile]) -> Dict[str, DatasetValidationResult]:
    """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
    assert_not_none(path)
    assert_not_none(dataset_files)
    assert_not_none(doc_files)

    datasets = dict()
    validation_results = dict()
    has_errors = False

    # Read dataset files and make sure their format is ok.
    for file in dataset_files:
        text = file.body.decode("utf-8")
        try:
            dataset = SbFileReader().read(io.StringIO(text))
        # TODO by forman:  except FormatError as e:
        except IOError as e:
            dataset = None
            has_errors = True
            validation_results[file.filename] = DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                                                        [Issue(ISSUE_TYPE_ERROR, f"{e}")])
        if dataset is not None:
            # Save well-formatted datasets
            datasets[file.filename] = dataset

    for file in dataset_files:
        # Validate the datasets that could be successfully parsed:
        if file.filename in datasets:
            dataset = datasets[file.filename]
            dataset_validation_result = validator.validate_dataset(dataset)
            validation_results[file.filename] = dataset_validation_result
            if dataset_validation_result.status == "ERROR":
                has_errors = True

    if has_errors:
        # Don't copy any files into store
        # Don't insert anything into database
        return validation_results

    # Write dataset files into store
    datasets_dir_path = ctx.get_datasets_store_path(path)
    os.makedirs(datasets_dir_path, exist_ok=True)
    for file in dataset_files:
        file_path = os.path.join(datasets_dir_path, file.filename)
        with open(file_path, "w") as fp:
            text = file.body.decode("utf-8")
            fp.write(text)

    # Write documentation files into store
    docs_dir_path = ctx.get_doc_files_store_path(path)
    os.makedirs(docs_dir_path, exist_ok=True)
    for file in doc_files:
        file_path = os.path.join(docs_dir_path, file.filename)
        with open(file_path, "wb") as fp:
            fp.write(file.body)

    # Insert datasets into database after all files are in the store
    for file in dataset_files:
        dataset = datasets[file.filename]
        dataset.name = file.filename
        dataset.metadata["qc_status"] = "todo"
        ctx.db_driver.add_dataset(dataset)

    return validation_results


# noinspection PyUnusedLocal,PyTypeChecker
def download_store_files(ctx: WsContext,
                         expr: str = None,
                         region: List[float] = None,
                         time: List[str] = None,
                         wdepth: List[float] = None,
                         mtype: str = 'all',
                         wlmode: str = 'all',
                         shallow: str = 'no',
                         pmode: str = 'contains',
                         pgroup: List[str] = None,
                         pname: List[str] = None,
                         docs: bool = False) -> str:
    assert_not_none(mtype, name='mtype')
    assert_not_none(wlmode, name='wlmode')
    assert_one_of(wlmode, ['all', 'multispectral', 'hyperspectral'], name='wlmode')
    assert_not_none(shallow, name='shallow')
    assert_one_of(shallow, ['no', 'yes', 'exclusively'], name='shallow')
    assert_not_none(pmode, name='pmode')
    assert_one_of(pmode, ['contains', 'same_cruise', 'dont_apply'], name='pmode')
    assert_not_none(docs, name='docs')
    # TODO (generated): implement operation download_store_files()
    raise NotImplementedError('operation download_store_files() not yet implemented')
