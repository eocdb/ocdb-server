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
import datetime
import io
import json
import os
import tempfile
import time
import zipfile
import chardet
from typing import Dict, List, Optional, Union, Tuple

from ..context import WsContext, _LOG
from ..utils import ensure_valid_path, ensure_valid_submission_id
from ...core.asserts import assert_not_none
from ...core.db.db_submission import DbSubmission
from ...core.models import DatasetRef, DatasetQueryResult, DatasetQuery, DATASET_VALIDATION_RESULT_STATUS_OK, \
    DATASET_VALIDATION_RESULT_STATUS_WARNING, QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED, \
    QC_STATUS_PUBLISHED, QC_STATUS_CANCELED, QC_STATUS_PROCESSED
from ...core.models.dataset_validation_result import DatasetValidationResult, DATASET_VALIDATION_RESULT_STATUS_ERROR
from ...core.models.issue import Issue, ISSUE_TYPE_ERROR
from ...core.models.submission import Submission, TYPE_MEASUREMENT, TYPE_DOCUMENT
from ...core.models.submission_file import SubmissionFile
from ...core.models.uploaded_file import UploadedFile
from ...core.seabass.sb_file_reader import SbFileReader, SbFormatError
from ...core.val import validator
from ...db.static_data import get_product_groups, get_products
from ...ws.controllers.datasets import find_datasets, get_dataset_by_id, delete_dataset
from ...ws.errors import WsBadRequestError


# noinspection PyUnusedLocal
def get_store_info(ctx: WsContext) -> Dict:
    return dict(products=get_products(), productGroups=get_product_groups())


def upload_submission_files(ctx: WsContext,
                            path: str,
                            store_user_path: str,
                            submission_id: str,
                            user_name: str,
                            dataset_files: List[UploadedFile],
                            publication_date: Union[datetime.datetime, type(None)],
                            allow_publication: bool,
                            doc_files: List[UploadedFile]) -> Dict[str, DatasetValidationResult]:
    """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
    assert_not_none(submission_id)
    assert_not_none(path)
    assert_not_none(store_user_path)
    # assert_not_none(publication_date)
    assert_not_none(allow_publication)
    assert_not_none(dataset_files)
    assert_not_none(doc_files)
    ensure_valid_path(path)
    ensure_valid_submission_id(submission_id)

    if submission_id == '':
        raise WsBadRequestError(f"Submission label is empty!")

    result = ctx.db_driver.get_submission(submission_id)
    if result is not None:
        raise WsBadRequestError(f"Submission identifier already exists: {submission_id}")

    if path.count('/') < 2:
        raise WsBadRequestError(f"Please provide the path as format: AFFILIATION (acronym)/EXPERIMENT/CRUISE")

    if len(dataset_files) < 1:
        raise WsBadRequestError(f"Please provide at least one dataset.")

    datasets = dict()
    validation_results = dict()
    data_source = ''

    # Read dataset files and make sure their format is ok.
    for file in dataset_files:
        txt_encoding = chardet.detect(file.body)['encoding']
        try:
            text = file.body.decode(txt_encoding)
        except UnicodeDecodeError as e:
            raise WsBadRequestError("Decoding error for file: " + file.filename + '.\n' + str(e))

        try:
            fobj = text.split('\n')
            first_line = fobj[0]

            if '/begin_header' in first_line.lower():
                dataset = SbFileReader().read(io.StringIO(text))
                data_source = 'SEABASS'
            else:
                raise IOError('Unknown file format.')

        except SbFormatError as e:
            dataset = None
            validation_results[file.filename] = DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                                                        [Issue(ISSUE_TYPE_ERROR,
                                                                               f"Invalid format: {e}")])

        except OSError as e:
            dataset = None
            validation_results[file.filename] = DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                                                        [Issue(ISSUE_TYPE_ERROR, f"OSError: {e}")])
        if dataset is not None:
            # Save well-formatted datasets
            datasets[file.filename] = dataset

    for file in dataset_files:
        # Validate the datasets that could be successfully parsed:
        if file.filename in datasets and data_source == 'SEABASS':
            dataset = datasets[file.filename]
            dataset_validation_result = validator.validate_dataset(dataset, ctx.config)
            validation_results[file.filename] = dataset_validation_result

    # Write dataset files into upload space and record as submission files
    submission_files = []
    index = 0
    datasets_dir_path = ctx.get_datasets_upload_path(os.path.join(store_user_path, path))
    os.makedirs(datasets_dir_path, exist_ok=True)
    for file in dataset_files:
        file_path = os.path.join(datasets_dir_path, file.filename)
        with open(file_path, "w") as fp:
            txt_encoding = chardet.detect(file.body)['encoding']
            try:
                text = file.body.decode(txt_encoding)
            # TEST!!!
            except UnicodeDecodeError as e:
                raise WsBadRequestError("Decoding error for file: " + file.filename + '.\n' + str(e))

            fp.write(text)

        result = validation_results[file.filename]
        submission_files.append(SubmissionFile(index=index,
                                               submission_id=submission_id,
                                               filename=file.filename,
                                               filetype=TYPE_MEASUREMENT,
                                               status=result.status,
                                               result=result))
        index += 1

    # Write documentation files into store
    docs_dir_path = ctx.get_doc_files_upload_path(os.path.join(store_user_path, path))
    os.makedirs(docs_dir_path, exist_ok=True)
    for file in doc_files:
        file_path = os.path.join(docs_dir_path, file.filename)
        with open(file_path, "wb") as fp:
            fp.write(file.body)
        submission_files.append(SubmissionFile(index=index,
                                               submission_id=submission_id,
                                               filename=file.filename,
                                               filetype=TYPE_DOCUMENT,
                                               status=QC_STATUS_SUBMITTED,
                                               result=None))
        index += 1

    status = QC_STATUS_SUBMITTED
    qc_status = _get_summary_validation_status(validation_results)
    if not qc_status == DATASET_VALIDATION_RESULT_STATUS_ERROR:
        status = QC_STATUS_VALIDATED

    # Insert submission into database
    submission = DbSubmission(submission_id=submission_id,
                              user_id=user_name,
                              date=datetime.datetime.now(),
                              status=status,
                              qc_status=qc_status,
                              path=path,
                              store_user_path=store_user_path,
                              publication_date=publication_date,
                              allow_publication=allow_publication,
                              files=submission_files)
    ctx.db_driver.add_submission(submission)

    return validation_results


def delete_submission(ctx: WsContext, submission_id: str) -> bool:
    submission = ctx.db_driver.get_submission(submission_id)
    _delete_submission(ctx, submission)
    # for file in submission.files:
    #    _delete_submission_file(ctx=ctx, file_to_delete=file, submission=submission)

    result = find_datasets(ctx=ctx, submission_id=submission_id)

    for ds in result.datasets:
        delete_dataset(ctx=ctx, dataset_id=ds.id)

    return ctx.db_driver.delete_submission(submission_id)


def update_submission(ctx: WsContext, submission: DbSubmission, status: str, publication_date: datetime) -> bool:
    # old_status = submission.status

    # new_stati = QC_TRANSITIONS[old_status]
    # if status not in new_stati:
    #    return False
    ensure_valid_path(submission.path)
    ensure_valid_submission_id(submission.submission_id)

    submission.publication_date = None
    submission.status = status

    if status == QC_STATUS_PUBLISHED or status == QC_STATUS_PROCESSED:
        submission.publication_date = publication_date
        result = find_datasets(ctx=ctx, submission_id=submission.submission_id)

        for ds in result.datasets:
            delete_dataset(ctx=ctx, dataset_id=ds.id)

        _publish_submission(ctx, submission, status)

    if status == QC_STATUS_CANCELED:
        result = find_datasets(ctx=ctx, submission_id=submission.submission_id)

        for ds in result.datasets:
            delete_dataset(ctx=ctx, dataset_id=ds.id)

    return ctx.db_driver.update_submission(submission)


def get_submissions(ctx: WsContext, user_id: str = None, offset: int = None, count: int = None,
                    query_column: str = None,
                    query_value: Union[str, datetime.datetime, bool] = None,
                    query_operator: str = None,
                    sort_column: str = None,
                    sort_order: str = None) \
        -> Tuple[List[Submission], int]:

    result, tot_count = ctx.db_driver.get_submissions(offset=offset,
                                                      count=count,
                                                      user_id=user_id,
                                                      query_column=query_column,
                                                      query_value=query_value,
                                                      query_operator=query_operator,
                                                      sort_column=sort_column,
                                                      sort_order=sort_order)

    submissions = []
    for db_submission in result:
        submission = db_submission.to_submission()
        submissions.append(submission)

    return submissions, tot_count


def get_submission(ctx: WsContext, submission_id: str) -> Optional[DbSubmission]:
    return ctx.db_driver.get_submission(submission_id)


def get_submission_file(ctx: WsContext,
                        submission_id: str,
                        index: int):
    result = ctx.db_driver.get_submission_file(submission_id=submission_id, index=index)
    return result


def get_submission_file_by_filename(ctx: WsContext,
                                    submission_id: str,
                                    file_name: str):
    result = ctx.db_driver.get_submission_file_by_filename(submission_id=submission_id, file_name=file_name)
    return result


def update_submission_files(ctx: WsContext,
                            path: str,
                            store_user_path: str,
                            submission_id: str,
                            new_submission_id: str,
                            publication_date: datetime,
                            allow_publication: bool) -> bool:
    """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
    assert_not_none(submission_id)
    assert_not_none(path)
    assert_not_none(store_user_path)
    # assert_not_none(publication_date)
    assert_not_none(allow_publication)

    ensure_valid_path(path)
    ensure_valid_submission_id(submission_id)

    if new_submission_id == '':
        raise WsBadRequestError(f"Submission label is empty!")

    if path.count('/') < 2:
        raise WsBadRequestError(f"Please provide the path as format: acronym of affiliation/cruise/experiment")

    # archive_path = ctx.get_submission_path(path)

    submission = ctx.db_driver.get_submission(submission_id)
    submission_path = ctx.get_submission_path(os.path.join(submission.store_sub_path, ''))

    old_path = submission.path.split('/')
    new_path = path.split('/')

    import shutil
    if old_path[0] != new_path[0]:
        shutil.move(os.path.join(submission_path, old_path[0]), os.path.join(submission_path, new_path[0]))

    if old_path[1] != new_path[1]:
        shutil.move(os.path.join(submission_path, old_path[0], old_path[1]),
                    os.path.join(submission_path, new_path[0], new_path[1]))

    if old_path[2] != new_path[2]:
        shutil.move(os.path.join(submission_path, old_path[0], old_path[1], old_path[2]),
                    os.path.join(submission_path, new_path[0], new_path[1], new_path[2]))

    submission.submission_id = new_submission_id
    submission.path = path
    submission.store_sub_path = store_user_path
    submission.publication_date = publication_date
    submission.allow_publication = allow_publication
    submission.updated_date = datetime.datetime.now()

    ctx.db_driver.delete_submission(submission_id)
    ctx.db_driver.add_submission(submission)

    return True


def add_submission_file(ctx: WsContext, submission: DbSubmission, file: UploadedFile, typ: str) -> \
        Optional[DatasetValidationResult]:
    submission = get_submission(ctx, submission_id=submission.submission_id)
    submission.updated_date = datetime.datetime.now()

    index = submission.next_index

    return update_submission_file(ctx, submission, index, file, typ, 'add')


def update_submission_file(ctx: WsContext, submission: DbSubmission,
                           index: int, file: UploadedFile, typ: str, mode: str = None) -> \
        Optional[DatasetValidationResult]:
    validation_result = None

    if mode != 'add':
        file_to_delete = submission.files[index]
        _delete_submission_file(ctx, file_to_delete, submission)

    if typ == TYPE_MEASUREMENT:
        text = file.body.decode("utf-8")
        try:
            dataset = SbFileReader().read(io.StringIO(text))
            validation_result = validator.validate_dataset(dataset, ctx.config)
        except SbFormatError as e:
            validation_result = DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                           [Issue(ISSUE_TYPE_ERROR,
                                                  f"Invalid format: {e}")])
        except OSError as e:
            validation_result = DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                           [Issue(ISSUE_TYPE_ERROR, f"OSError: {e}")])

        write_path = ctx.get_datasets_upload_path(os.path.join(submission.store_sub_path, submission.path))
        os.makedirs(write_path, exist_ok=True)
        file_path = os.path.join(write_path, file.filename)
        with open(file_path, "w") as fp:
            text = file.body.decode("utf-8")
            fp.write(text)
    else:
        write_path = ctx.get_doc_files_upload_path(os.path.join(submission.store_sub_path, submission.path))
        os.makedirs(write_path, exist_ok=True)
        file_path = os.path.join(write_path, file.filename)
        with open(file_path, "wb") as fp:
            fp.write(file.body)

    if mode == 'add':
        if typ == TYPE_MEASUREMENT:
            submission.files.append(SubmissionFile(index=index,
                                                   submission_id=submission.submission_id,
                                                   filename=file.filename,
                                                   filetype=typ,
                                                   status=validation_result.status,
                                                   result=validation_result))
        else:
            submission.files.append(SubmissionFile(index=index,
                                                   submission_id=submission.submission_id,
                                                   filename=file.filename,
                                                   filetype=typ,
                                                   status=QC_STATUS_SUBMITTED,
                                                   result=None))
    else:
        submission.files[index].filename = file.filename
        submission.files[index].filetype = typ

    if typ == TYPE_MEASUREMENT:
        submission.files[index].status = validation_result.status
        submission.files[index].result = validation_result

    _update_validation_status(submission)

    result = ctx.db_driver.update_submission(submission)
    if not result:
        return DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                       [Issue(ISSUE_TYPE_ERROR, "Database access error")])

    submission.updated_date = datetime.datetime.now()
    return validation_result


def delete_submission_file(ctx: WsContext, submission: DbSubmission, index: int) -> bool:
    file_to_delete = submission.files[index]

    _delete_submission_file(ctx, file_to_delete, submission)

    del submission.files[index]
    new_index = 0
    for file_ref in submission.files:
        file_ref.index = new_index
        new_index += 1

    return ctx.db_driver.update_submission(submission)


def _delete_submission_file(ctx, file_to_delete, submission):
    if file_to_delete.filetype == TYPE_MEASUREMENT:
        root_path = ctx.get_datasets_upload_path(os.path.join(submission.store_sub_path, submission.path))
    else:
        root_path = ctx.get_doc_files_upload_path(os.path.join(submission.store_sub_path, submission.path))
    file_path = os.path.join(root_path, file_to_delete.filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        _LOG.warning("File to delete des not exist: " + file_path)


def _delete_submission(ctx, submission):
    import shutil
    path = ctx.get_submission_path(submission.store_sub_path)
    shutil.rmtree(path, ignore_errors=True)


def update_submission_file_status(ctx: WsContext, submission: DbSubmission, index: int, status: str) -> bool:
    submission.files[index].status = status

    return ctx.db_driver.update_submission(submission)


# noinspection PyTypeChecker
def download_store_files(ctx: WsContext,
                         expr: str = None,
                         region: List[float] = None,
                         s_time: List[str] = None,
                         wdepth: List[float] = None,
                         mtype: str = 'all',
                         wlmode: str = 'all',
                         shallow: str = 'no',
                         pmode: str = 'contains',
                         pgroup: List[str] = None,
                         pname: List[str] = None,
                         docs: bool = False) -> zipfile.ZipFile:
    result = find_datasets(ctx,
                           expr=expr,
                           region=region,
                           time=s_time,
                           wdepth=wdepth,
                           mtype=mtype,
                           wlmode=wlmode,
                           shallow=shallow,
                           pmode=pmode,
                           pgroup=pgroup,
                           pname=pname,
                           geojson=False)

    if result.total_count < 1:
        # @todo 2 tb/tb is this correct? Or raise exception? 2018-12-13
        return None

    return _assemble_zip_archive(ctx, docs, result)


# noinspection PyTypeChecker
def download_store_files_by_id(ctx: WsContext,
                               dataset_ids: List[str] = None,
                               docs: bool = False) -> zipfile.ZipFile:
    result_list = []
    for dsId in dataset_ids:
        dataset_ref = DatasetRef(dsId, "fake_path", 'fake_filename')
        result_list.append(dataset_ref)

    result = DatasetQueryResult(locations={}, total_count=len(result_list), datasets=result_list, query=DatasetQuery())

    if result.total_count < 1:
        # @todo 2 tb/tb is this correct? Or raise exception? 2018-12-13
        return None

    return _assemble_zip_archive(ctx, docs, result)


# noinspection PyTypeChecker
def download_submission_file_by_id(ctx: WsContext,
                                   submission_id: str = None,
                                   index: int = None) -> zipfile.ZipFile:
    submission = get_submission(ctx, submission_id)

    if not submission:
        return None

    submission_file = get_submission_file(ctx, submission_id, index)

    path = os.path.join(submission.store_sub_path, submission.path)
    if submission_file.filetype == TYPE_MEASUREMENT:
        source_path = os.path.join(ctx.get_datasets_upload_path(path))
    else:
        source_path = os.path.join(ctx.get_doc_files_upload_path(path))

    return _assemble_submission_file_zip_archive(submission_file, source_path, path)


def _assemble_submission_file_zip_archive(submission_file: SubmissionFile, source_path: str, path: str):
    tmp_dir = tempfile.gettempdir()
    zip_name = create_zip_file_name()
    zip_file_path = os.path.join(tmp_dir, zip_name)

    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        zip_file.write(os.path.join(source_path, submission_file.filename),
                       os.path.join(path, submission_file.filename))

    return zip_file


def _assemble_zip_archive(ctx, docs, result):
    tmp_dir = tempfile.gettempdir()
    zip_name = create_zip_file_name()
    zip_file_path = os.path.join(tmp_dir, zip_name)
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        for dataset_ref in result.datasets:
            dataset = get_dataset_by_id(ctx, dataset_ref.id)
            if dataset is None:
                continue

            full_file_path = os.path.join(ctx.store_path, dataset.user_id + '_' + dataset.submission_id, dataset.path,
                                          "archive", dataset.filename)
            if not os.path.exists(full_file_path):
                raise FileNotFoundError(f"Could not find file {full_file_path} on server. Please contact eumetsat.")
            zip_file.write(full_file_path, os.path.join(dataset.path, "archive", dataset.filename))

            if not docs:
                continue

            if "documents" in dataset.metadata:
                doc_root_path = get_document_root_path(
                    os.path.join(dataset.user_id + '_' + dataset.submission_id, dataset.path))
                doc_archive_path = ctx.get_doc_files_store_path(doc_root_path)
                zip_store_path = os.path.join(dataset.path, "documents")

                document_names = json.loads(dataset.metadata["documents"])

                for document_name in document_names:
                    document_path = os.path.join(doc_archive_path, document_name)
                    document_zip_path = os.path.join(zip_store_path, document_name)
                    if os.path.isfile(document_path):
                        zip_file.write(document_path, document_zip_path)
    return zip_file


def create_zip_file_name():
    # @todo 1 tb/tb assemble meaningful zip-archive name from query 2018-12-13
    now = datetime.datetime.now()
    now_secs = int(time.mktime(now.timetuple()))
    zip_name = str(now_secs) + ".zip"
    return zip_name


def get_document_root_path(dataset_path):
    segments = dataset_path.split(os.sep)
    valid_segments = []
    for segment in segments:
        if segment == "archive":
            break
        valid_segments.append(segment)

    if len(valid_segments) > 1:
        path = os.path.join(valid_segments[0], valid_segments[1])
        for idx in range(2, len(valid_segments)):
            path = os.path.join(path, valid_segments[idx])
        return path
    else:
        return valid_segments[0]


def _get_summary_validation_status(validation_results: dict) -> str:
    errors = 0
    warnings = 0
    for key, value in validation_results.items():
        if value.status == DATASET_VALIDATION_RESULT_STATUS_ERROR:
            errors += 1
        if value.status == DATASET_VALIDATION_RESULT_STATUS_WARNING:
            warnings += 1

    if errors > 0:
        return DATASET_VALIDATION_RESULT_STATUS_ERROR
    if warnings > 0:
        return DATASET_VALIDATION_RESULT_STATUS_WARNING

    return DATASET_VALIDATION_RESULT_STATUS_OK


def _update_validation_status(submission: DbSubmission):
    errors = 0
    for file in submission.files:
        if file.status == DATASET_VALIDATION_RESULT_STATUS_ERROR:
            errors += 1

    if errors > 0:
        submission.status = QC_STATUS_SUBMITTED
    else:
        submission.status = QC_STATUS_VALIDATED


def _publish_submission(ctx: WsContext, submission: DbSubmission, status) -> bool:
    submission_path = os.path.join(submission.store_sub_path, submission.path)
    source_meas_path = os.path.join(ctx.get_datasets_upload_path(submission_path))
    source_docs_path = os.path.join(ctx.get_doc_files_upload_path(submission_path))

    # collect related documents
    docs = []
    for file in submission.files:
        if file.filetype == TYPE_DOCUMENT:
            docs.append(file.filename)

    datasets = []
    for file in submission.files:
        if file.filetype == TYPE_MEASUREMENT:
            source_path = os.path.join(source_meas_path, file.filename)
        else:
            source_path = os.path.join(source_docs_path, file.filename)

        if file.filetype == TYPE_MEASUREMENT:
            try:
                dataset = SbFileReader().read(source_path)
            except (SbFormatError, OSError) as e:
                _LOG.warning("Error reading dataset: " + str(e))
                raise e

            dataset.path = submission.path
            dataset.metadata['documents'] = json.dumps(docs)
            dataset.filename = file.filename
            dataset.submission_id = submission.submission_id
            dataset.user_id = submission.user_id
            dataset.status = status

            datasets.append(dataset)

    for dataset in datasets:
        ctx.db_driver.add_dataset(dataset)

    return True
