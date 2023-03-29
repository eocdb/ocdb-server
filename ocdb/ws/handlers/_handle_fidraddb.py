import functools
import logging
import os.path
import datetime
from mimetypes import guess_type

import tornado.httputil
import tornado.escape

from collections import deque
from ocdb.core.fidraddb.validator import CalCharValidator
from ocdb.ws.handlers._handlers import _login_required, _admin_required, _submission_send_authorization_required, \
    _ensure_string_argument
from ocdb.ws.webservice import WsRequestHandler, _LOG_FidRadDb
from ocdb.ws.controllers.store import *

_DATA_DIR_NAME = "cal_char"

_logger_initialized = False
_history_path: str = None


def _ensure_logger_initialized(ctx: WsContext):
    global _logger_initialized, _history_path
    if not _logger_initialized:
        _history_path = ctx.get_fidraddb_store_path("history.txt")
        parent = os.path.dirname(_history_path)
        os.makedirs(parent, exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(_history_path)
        file_handler.setFormatter(formatter)
        _LOG_FidRadDb.addHandler(file_handler)
        _LOG_FidRadDb.setLevel(logging.DEBUG)
        _logger_initialized = True


def _userLogger(username: str):
    return UserLogger(_LOG_FidRadDb, {UserLogger.KEY: username})


def _bottom_up_file_line_reader(filename, buf_size=8192):
    with open(filename) as f:
        segment = None
        bottom_up_offset = 0
        f.seek(0, os.SEEK_END)
        file_size = remaining_size = f.tell()
        while remaining_size > 0:
            bottom_up_offset = min(file_size, bottom_up_offset + buf_size)
            f.seek(file_size - bottom_up_offset)
            buffer = f.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            if segment is not None:
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        if segment is not None:
            yield segment


def _fidrad_submit_authorization_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        allowed = False
        if self.has_fidrad_rights():
            allowed = True

        if not allowed:
            self.set_status(status_code=403, reason='Not enough access rights to perform FidRadDb submissions.')
            return

        func(self, *args, **kwargs)

    return wrapper


def _fidrad_search_authorization_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        allowed = False
        if self.has_fidrad_rights() or self.has_admin_rights:
            allowed = True

        if not allowed:
            self.set_status(status_code=403, reason='Not enough access rights to perform FidRadDb search operations.')
            return

        func(self, *args, **kwargs)

    return wrapper


class UserLogger(logging.LoggerAdapter):
    """
    This adapter expects a passed in dict-like object to have a 'username' key,
    whose value in brackets is presented to the log message.
    """

    KEY = "username"

    def process(self, msg, kwargs):
        pid = os.getpid()
        return 'user: %s pid[%s] - %s' % (self.extra[self.KEY], pid, msg), kwargs


# noinspection PyAbstractClass
class FidRadDbRequestHandler(WsRequestHandler):

    def __init__(self, application, request, **kwargs):
        super(FidRadDbRequestHandler, self).__init__(application, request, **kwargs)
        _ensure_logger_initialized(self.ws_context)
        self.logger = _userLogger(self.get_current_user())


# noinspection PyAbstractClass
class HandleCalCharUpload(FidRadDbRequestHandler):

    @_login_required
    @_fidrad_submit_authorization_required
    def post(self):
        """Provide API operation uploadStoreFiles()."""
        log = self.logger
        log.info("upload start")
        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)

        cal_char_files = []
        for file in files.get("cal_char_files", []):
            cal_char_files.append(UploadedFile.from_dict(file))

        doc_files = []
        for file in files.get("docfiles", []):
            doc_files.append(UploadedFile.from_dict(file))

        allow_publication = arguments.get("allow_publication")
        allow_publication = _ensure_string_argument(allow_publication, "allow_publication")
        allow_publication = True if allow_publication and allow_publication.strip().lower() == "true" else False

        result = None
        try:
            result = self.upload_cal_char_files(cal_char_files=cal_char_files, doc_files=doc_files,
                                                allow_publication=allow_publication)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log.error(f"A {type(e)} occurred, while uploading files")
            log.error(f"Error message: {e}")
            log.error(f"Traceback-Informationen: {tb}")
            result = {f"A {type(e)} occurred": str(e)}

        self.finish(tornado.escape.json_encode(result))
        log.info("upload stop")

    def upload_cal_char_files(self,
                              cal_char_files: List[UploadedFile],
                              doc_files: List[UploadedFile],
                              allow_publication: bool) -> Dict[str, any]:
        """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
        assert_not_none(cal_char_files)
        assert_not_none(doc_files)
        log = self.logger

        cal_char_count = len(cal_char_files)
        if cal_char_count < 1:
            msg = f"Please provide at least one cal/char file."
            log.warning("Upload stopped. " + msg)
            raise WsBadRequestError(msg)

        if cal_char_count > 15:
            msg = f"Please provide a maximum of 15 Cal/Char files. Received {cal_char_count}"
            log.warning("Upload stopped. " + msg)
            raise WsBadRequestError(msg)

        key_upload_count = "Upload count"
        key_invalid_filename = "Invalid filenames"
        key_already_existing_files = "Existing Cal/Char files"
        key_file_not_valid = "Invalid file content"

        results = {}
        results.update({key_upload_count: 0})
        results.update({key_invalid_filename: []})
        results.update({key_already_existing_files: []})
        results.update({key_file_not_valid: {}})

        ctx = self.ws_context

        cal_char_validator = CalCharValidator()

        cal_char_dir_path = ctx.get_fidraddb_store_path(_DATA_DIR_NAME)
        os.makedirs(cal_char_dir_path, exist_ok=True)
        for file in cal_char_files:
            filename = file.filename
            if not CalCharValidator.isValidFilename(filename):
                log.warning(f"Invalid filename: '{filename}'. Upload cal/char file aborted.")
                results[key_invalid_filename].append(filename)
                continue
            file_path = os.path.join(cal_char_dir_path, filename)
            if os.path.isfile(file_path):
                log.warning(f"File '{filename}' already exists. Upload cal/char file aborted.")
                results[key_already_existing_files].append(filename)
                continue
            validation_result = cal_char_validator.validate(filename, file.body)
            if validation_result:
                log.warning(f"File '{filename}' not valid. Upload cal/char file aborted. "
                            + validation_result.get(filename))
                results[key_file_not_valid].update(validation_result)
                continue
            with open(file_path, "wb") as fp:
                fp.write(file.body)
                results[key_upload_count] = results[key_upload_count] + 1
                log.info(f"file: {filename} successfully uploaded.")
                user_name = self.get_current_user()
                utc_time = datetime.datetime.now(datetime.timezone.utc)
                ctx.db_driver.add_cal_char_file({"filename": filename,
                                                 "user_name": user_name,
                                                 "public": allow_publication,
                                                 "utc_upload_time": str(utc_time)})

        # Write documentation files into store
        # document_existing = []
        # docs_dir_path = ctx.get_fidraddb_store_path("additional_docs")
        # os.makedirs(docs_dir_path, exist_ok=True)
        # for file in doc_files:
        #     filename = file.filename
        #     file_path = os.path.join(docs_dir_path, filename)
        #     if os.path.exists(file_path):
        #         log.warning(f"File already exists. The document file {filename} is not uploaded.")
        #         document_existing.append(filename)
        #     else:
        #         with open(file_path, "wb") as fp:
        #             fp.write(file.body)
        #             count += 1
        #             log.info(f"file: {filename} successfully uploaded.")

        if len(results[key_invalid_filename]) == 0:
            results.pop(key_invalid_filename)
        if len(results[key_already_existing_files]) == 0:
            results.pop(key_already_existing_files)
        # if len(document_existing) > 0:
        #     results.update({"Already existing document files": document_existing})
        #     existing_warning = True
        if key_already_existing_files in results:
            results.update({"Warning!": ["Files with the same name already exist on the server.",
                                         "If you have a newer or corrected version of the file with ",
                                         "the same name to replace the existing file, please inform an ",
                                         "administrator to delete the existing file first. ",
                                         "Then repeat the upload with those files that could not ",
                                         "be written at the first attempt."]})

        return results


# noinspection PyAbstractClass
class HandleGetHistoryTail(FidRadDbRequestHandler):

    @_login_required
    @_fidrad_search_authorization_required
    def get(self, num_lines: str):
        assert_not_none(num_lines, name="num_lines")
        n_lines = int(num_lines)
        global _history_path
        lines = []
        with open(_history_path, mode="r") as file:
            for line in deque(file, maxlen=n_lines):
                lines.append(line.strip())

        self.finish(tornado.escape.json_encode(lines))


# noinspection PyAbstractClass
class HandleHistoryBottomUpSearch(FidRadDbRequestHandler):

    @_login_required
    @_fidrad_search_authorization_required
    def get(self, search_string: str, max_num_lines):
        assert_not_none(search_string, name="search_string")
        assert_not_none(max_num_lines, name="max_num_lines")
        max_lines = int(max_num_lines)
        global _history_path
        lines = []

        for line in _bottom_up_file_line_reader(_history_path):
            lower_search = search_string.lower()
            lower_line = line.lower()
            if lower_search in lower_line:
                line = line.strip()
                lines.insert(0, line)
            if len(lines) == max_lines:
                break

        self.finish(tornado.escape.json_encode(lines))


# noinspection PyAbstractClass
class HandleListFiles(FidRadDbRequestHandler):

    # All are allowed to download a list of public cal/char files available on the server, even guest users who
    # are not logged in.
    def get(self, name_part: str):
        data_dir_path = self.ws_context.get_fidraddb_store_path(_DATA_DIR_NAME)
        # files = os.listdir(data_dir_path)
        current_user_name = self.get_current_user()
        is_admin = self.has_admin_rights()
        files = self.ws_context.db_driver.get_cal_char_files_list(current_user_name, is_admin)
        result = []
        if name_part == "__ALL__":
            result = files
        else:
            part_lower = name_part.lower()
            for name in files:
                name_lower = name.lower()
                if part_lower in name_lower:
                    result.append(name)
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass
class HandleDeleteFile(FidRadDbRequestHandler):

    @_login_required
    # @_admin_required
    def delete(self, filename: str):
        assert_not_none(filename, name="filename")
        current_user_name = self.get_current_user()
        is_admin = self.has_admin_rights()
        files_list = self.ws_context.db_driver.get_cal_char_files_list(current_user_name, is_admin, for_deletion=True)
        if files_list.count(filename) == 0:
            raise WsBadRequestError(f"You are not allowed to delete the file '{filename}' because you are not the "
                                    f"owner of this file or you are not an administrator.")
        data_dir_path = self.ws_context.get_fidraddb_store_path(_DATA_DIR_NAME)
        file_path = os.path.join(data_dir_path, filename)
        log = self.logger
        message = ''
        if os.path.exists(file_path):
            if os.access(file_path, os.W_OK):
                try:
                    os.remove(file_path)
                except Exception as e:
                    exception_string: str = repr(e)
                    message = f"Deletion requested for {filename}. Exception occurred. {exception_string}."
                    if os.path.exists(file_path):
                        message += " The file still exists on the server."
                    log.error(message)
                    self.set_status(423, message)
                else:
                    message = f"Deletion requested for {filename}. Successfully deleted."
                    log.info(message)
                    self.ws_context.db_driver.remove_cal_char_file_entry(filename)
                    self.set_status(200, message)
            else:
                message = f"Deletion requested for {filename}. File exist but can not be deleted."
                log.error(message)
                self.set_status(403, message)
        else:
            message = f"Deletion requested for {filename} but file does not exist."
            log.warning(message)
            self.set_status(404, message)

        self.finish(tornado.escape.json_encode(message))


# noinspection PyAbstractClass
class HandleDownloadFile(FidRadDbRequestHandler):

    # All are allowed to download cal/char files, even for guest users who are not logged in.
    def get(self, filename: str):
        assert_not_none(filename, name="filename")
        data_dir_path = self.ws_context.get_fidraddb_store_path(_DATA_DIR_NAME)

        file_path = os.path.join(data_dir_path, filename)
        log = self.logger
        message = ''
        if os.path.exists(file_path):
            if os.access(file_path, os.R_OK):
                try:
                    mime_type, encoding = guess_type(file_path)
                    self.set_header('Content-Type', mime_type or 'application/octet-stream')
                    self.set_header('Content-Disposition', f'attachment; filename={filename}')
                    with open(file_path, 'rb') as f:
                        while True:
                            data = f.read(32768)
                            if not data:
                                break
                            self.write(data)

                except Exception as e:
                    exception_string: str = repr(e)
                    message = f"Exception occurs while streaming requested file '{filename}'. " \
                              f"Exception: {exception_string}."
                    log.error(message)
                    self.set_status(404, message)
                else:
                    message = f"Download requested for {filename}. Successfully downloaded."
                    log.info(message)
                    self.set_status(200, message)
            else:
                message = f"Download requested for {filename}. File exist but can not be read."
                log.error(message)
                self.set_status(403, message)
        else:
            message = f"Download requested for {filename} but file does not exist."
            log.warning(message)
            self.set_status(404, message)

        self.finish(tornado.escape.json_encode(message))
