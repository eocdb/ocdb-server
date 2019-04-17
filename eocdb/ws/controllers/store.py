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
import os
import tempfile
import time
import zipfile
from typing import Dict, List, Optional

from ..context import WsContext, _LOG
from ...core.asserts import assert_not_none
from ...core.db.db_submission import DbSubmission
from ...core.models import DatasetRef, DatasetQueryResult, DatasetQuery, DATASET_VALIDATION_RESULT_STATUS_OK, \
    DATASET_VALIDATION_RESULT_STATUS_WARNING, QC_STATUS_SUBMITTED, QC_STATUS_VALIDATED, \
    QC_STATUS_READY_TO_PUBLISHED, QC_STATUS_PUBLISHED, QC_STATUS_CANCELED, QC_STATUS_PROCESSED
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
                            submission_id: str,
                            user_id: int,
                            dataset_files: List[UploadedFile],
                            publication_date: datetime,
                            allow_publication: bool,
                            doc_files: List[UploadedFile]) -> Dict[str, DatasetValidationResult]:
    """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
    assert_not_none(submission_id)
    assert_not_none(path)
    assert_not_none(publication_date)
    assert_not_none(allow_publication)
    assert_not_none(dataset_files)
    assert_not_none(doc_files)

    if submission_id == '':
        raise WsBadRequestError(f"Submission identifier is empty!")

    result = ctx.db_driver.get_submission(submission_id)
    if result is not None:
        raise WsBadRequestError(f"Submission identifier already exists: {submission_id}")

    datasets = dict()
    validation_results = dict()

    # Read dataset files and make sure their format is ok.
    for file in dataset_files:
        text = file.body.decode("utf-8")
        try:
            dataset = SbFileReader().read(io.StringIO(text))
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
        if file.filename in datasets:
            dataset = datasets[file.filename]
            dataset_validation_result = validator.validate_dataset(dataset, ctx.config)
            validation_results[file.filename] = dataset_validation_result

    # Write dataset files into upload space and record as submission files
    submission_files = []
    index = 0
    datasets_dir_path = ctx.get_datasets_upload_path(path)
    os.makedirs(datasets_dir_path, exist_ok=True)
    for file in dataset_files:
        file_path = os.path.join(datasets_dir_path, file.filename)
        with open(file_path, "w") as fp:
            text = file.body.decode("utf-8")
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
    docs_dir_path = ctx.get_doc_files_upload_path(path)
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

    archive_path = ctx.get_submission_path(path)
    # Insert submission into database
    submission = DbSubmission(submission_id=submission_id,
                              user_id=user_id,
                              date=datetime.datetime.now(),
                              status=status,
                              qc_status=qc_status,
                              path=archive_path,
                              publication_date=publication_date,
                              allow_publication=allow_publication,
                              files=submission_files)
    ctx.db_driver.add_submission(submission)

    return validation_results


def delete_submission(ctx: WsContext, submission_id: str) -> bool:
    submission = ctx.db_driver.get_submission(submission_id)

    for file in submission.files:
        _delete_submission_file(ctx=ctx, file_to_delete=file, submission=submission)

    result = find_datasets(ctx=ctx, submission_id=submission_id)

    for ds in result.datasets:
        delete_dataset(ctx=ctx, dataset_id=ds.id, api_key="")

    return ctx.db_driver.delete_submission(submission_id)


def update_submission(ctx: WsContext, submission: DbSubmission, status: str, publication_date: datetime) -> bool:
    old_status = submission.status

    # new_stati = QC_TRANSITIONS[old_status]
    # if status not in new_stati:
    #    return False

    if status == QC_STATUS_READY_TO_PUBLISHED:
        submission.publication_date = publication_date
    else:
        submission.publication_date = None

    if status == QC_STATUS_PUBLISHED or status == QC_STATUS_PROCESSED:
        _publish_submission(ctx, submission)

    if status == QC_STATUS_CANCELED:
        result = find_datasets(ctx=ctx, submission_id=submission.submission_id)

        for ds in result.datasets:
            delete_dataset(ctx=ctx, dataset_id=ds.id, api_key="")

    submission.status = status
    return ctx.db_driver.update_submission(submission)


def get_submissions(ctx: WsContext, user_id: int) -> List[Submission]:
    roles = [];
    for u in ctx.config['users']:
        if u['id'] == user_id:
            roles = u['roles']

    if 'admin' in roles:
        result = ctx.db_driver.get_submissions()
    else:
        result = ctx.db_driver.get_submissions_for_user(user_id)

    submissions = []
    for db_subm in result:
        subm = db_subm.to_submission()
        submissions.append(subm)

    return submissions


def get_submission(ctx: WsContext, submission_id: str) -> Optional[DbSubmission]:
    return ctx.db_driver.get_submission(submission_id)


def get_submission_file(ctx: WsContext,
                        submission_id: str,
                        index: int):
    result = ctx.db_driver.get_submission_file(submission_id=submission_id, index=index)
    return result


def update_submission_file(ctx: WsContext, submission: DbSubmission,
                           index: int, file: UploadedFile, typ: str) -> Optional[DatasetValidationResult]:
    validation_result = None

    file_to_delete = submission.files[index]
    _delete_submission_file(ctx, file_to_delete, submission)

    if typ == TYPE_MEASUREMENT:
        text = file.body.decode("utf-8")
        try:
            dataset = SbFileReader().read(io.StringIO(text))
        except SbFormatError as e:
            return DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                           [Issue(ISSUE_TYPE_ERROR,
                                                  f"Invalid format: {e}")])
        except OSError as e:
            return DatasetValidationResult(DATASET_VALIDATION_RESULT_STATUS_ERROR,
                                           [Issue(ISSUE_TYPE_ERROR, f"OSError: {e}")])

        validation_result = validator.validate_dataset(dataset, ctx.config)
        #if DATASET_VALIDATION_RESULT_STATUS_ERROR == validation_result.status:
        #    return validation_result

        write_path = ctx.get_datasets_upload_path(submission.path)
        os.makedirs(write_path, exist_ok=True)
        file_path = os.path.join(write_path, file.filename)
        with open(file_path, "w") as fp:
            text = file.body.decode("utf-8")
            fp.write(text)
    else:
        write_path = ctx.get_doc_files_upload_path(submission.path)
        os.makedirs(write_path, exist_ok=True)
        file_path = os.path.join(write_path, file.filename)
        with open(file_path, "wb") as fp:
            fp.write(file.body)

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
        root_path = ctx.get_datasets_upload_path(submission.path)
    else:
        root_path = ctx.get_doc_files_upload_path(submission.path)
    file_path = os.path.join(root_path, file_to_delete.filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        _LOG.warning("File to delete des not exist: " + file_path)


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
        dataset_ref = DatasetRef(dsId, "fake_path")
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

    submission_file = get_submission_file(ctx, submission_id, index)

    if submission_file.filetype == TYPE_MEASUREMENT:
        source_path = os.path.join(ctx.get_datasets_upload_path(submission.path))
    else:
        source_path = os.path.join(ctx.get_doc_files_upload_path(submission.path))

    return _assemble_submission_file_zip_archive(ctx, submission_file, source_path)


def _assemble_submission_file_zip_archive(ctx, submission_file: SubmissionFile, path: str):
    tmp_dir = tempfile.gettempdir()
    zip_name = create_zip_file_name()
    zip_file_path = os.path.join(tmp_dir, zip_name)

    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        full_file_path = os.path.join(ctx.store_path, path + '/' + submission_file.filename)
        zip_file.write(full_file_path, path + '/' + submission_file.filename)

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

            full_file_path = os.path.join(ctx.store_path, dataset.path)
            zip_file.write(full_file_path, dataset.path)

            if not docs:
                continue

            if "documents" in dataset.metadata:
                doc_root_path = get_document_root_path(dataset.path)
                doc_archive_path = ctx.get_doc_files_store_path(doc_root_path)
                zip_store_path = os.path.join(doc_root_path, "documents")

                documents_string = dataset.metadata["documents"]
                document_names = documents_string.split(",")
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


def _publish_submission(ctx: WsContext, submission: DbSubmission) -> bool:
    source_meas_path = os.path.join(ctx.get_datasets_upload_path(submission.path))
    source_docs_path = os.path.join(ctx.get_doc_files_upload_path(submission.path))
    target_meas_path = os.path.join(ctx.get_datasets_store_path(submission.path))
    target_docs_path = os.path.join(ctx.get_doc_files_store_path(submission.path))

    datasets = []
    for file in submission.files:
        if file.filetype == TYPE_MEASUREMENT:
            source_path = os.path.join(source_meas_path, file.filename)
            target_path = os.path.join(target_meas_path, file.filename)
        else:
            source_path = os.path.join(source_docs_path, file.filename)
            target_path = os.path.join(target_docs_path, file.filename)

        os.rename(source_path, target_path)

        if file.filetype == TYPE_MEASUREMENT:
            try:
                dataset = SbFileReader().read(target_path)
            except (SbFormatError, OSError) as e:
                _LOG.warning("Error reading dataset: " + e)
                continue

            dataset.path = target_path
            dataset.submission_id = submission.submission_id
            dataset.user_id = submission.user_id
            dataset.status = submission.status

            datasets.append(dataset)

    for dataset in datasets:
        ctx.db_driver.add_dataset(dataset)

    return True
