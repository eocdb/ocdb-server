import functools
import logging

import tornado.httputil
import tornado.escape

from ocdb.ws.handlers._handlers import _login_required
from ocdb.ws.webservice import WsRequestHandler, _LOG_FidRadDb
from ocdb.ws.controllers.store import *

_logger_initialized = False
_history_path: str = None


class UserLogger(logging.LoggerAdapter):
    """
    This adapter expects a passed in dict-like object to have a 'username' key,
    whose value in brackets is presented to the log message.
    """

    KEY = "username"

    def process(self, msg, kwargs):
        pid = os.getpid()
        return 'user: %s pid[%s] - %s' % (self.extra[self.KEY], pid, msg), kwargs


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


# noinspection PyAbstractClass
class FidradRequestHandler(WsRequestHandler):

    def __init__(self, application, request, **kwargs):
        super(FidradRequestHandler, self).__init__(application, request, **kwargs)
        _ensure_logger_initialized(self.ws_context)
        self.logger = _userLogger(self.get_current_user())


# noinspection PyAbstractClass
class HandleCalCharUpload(FidradRequestHandler):

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

        result = self.upload_cal_char_files(cal_char_files=cal_char_files,
                                            doc_files=doc_files)
        self.finish(tornado.escape.json_encode(result))
        log.info("upload stop")

    def upload_cal_char_files(self,
                              cal_char_files: List[UploadedFile],
                              doc_files: List[UploadedFile]) -> Dict[str, any]:
        """ Return a dictionary mapping dataset file names to DatasetValidationResult."""
        assert_not_none(cal_char_files)
        assert_not_none(doc_files)
        log = self.logger

        if len(cal_char_files) < 1:
            raise WsBadRequestError(f"Please provide at least one cal/char file.")

        if len(cal_char_files) > 5:
            raise WsBadRequestError(f"Please provide a maximum of five Cal/Char files.")

        results = {}

        for file in cal_char_files:
            filename = file.filename
            # split filename into <class or serial number> <file type> <calibration date [pattern: YYYYMMDDhhmmss]>

        # First try to read ALL dataset files to ensure their format is ok.
        for file in cal_char_files:
            txt_encoding = chardet.detect(file.body)['encoding']
            try:
                text = file.body.decode(txt_encoding)
            except UnicodeDecodeError as e:
                raise WsBadRequestError("Decoding error for file: " + file.filename + '.\n' + str(e))

        count = 0
        ctx = self.ws_context

        # write cal/char files
        cal_char_existing = []
        cal_char_dir_path = ctx.get_fidraddb_store_path("cal_char")
        os.makedirs(cal_char_dir_path, exist_ok=True)
        for file in cal_char_files:
            filename = file.filename
            file_path = os.path.join(cal_char_dir_path, filename)
            if os.path.exists(file_path):
                log.warning(f"File already exists. The cal/char file {filename} is not uploaded.")
                cal_char_existing.append(filename)
            else:
                with open(file_path, "w") as fp:
                    txt_encoding = chardet.detect(file.body)['encoding']
                    text = file.body.decode(txt_encoding)
                    fp.write(text)
                    count += 1
                    log.info(f"file: {filename} written to {cal_char_dir_path}")

        # Write documentation files into store
        document_existing = []
        docs_dir_path = ctx.get_fidraddb_store_path("additional_docs")
        os.makedirs(docs_dir_path, exist_ok=True)
        for file in doc_files:
            filename = file.filename
            file_path = os.path.join(docs_dir_path, filename)
            if os.path.exists(file_path):
                log.warning(f"File already exists. The document file {filename} is not uploaded.")
                document_existing.append(filename)
            else:
                with open(file_path, "wb") as fp:
                    fp.write(file.body)
                    count += 1
                    log.info(f"file: {filename} written to {docs_dir_path}")

        results.update({"Num Files Uploaded": count})
        existing_warning = False
        if len(cal_char_existing) > 0:
            results.update({"Already existing Cal/Char files": cal_char_existing})
            existing_warning = True
        if len(document_existing) > 0:
            results.update({"Already existing document files": document_existing})
            existing_warning = True
        if existing_warning:
            results.update({"Warning!": ["Files with the same name already exist on the server.",
                                         "If you have a more recent or corrected version of the file with ",
                                         "the same name to replace the existing file, please inform an ",
                                         "administrator to delete the existing file first. ",
                                         "Then repeat the upload with those files that could not ",
                                         "be written at the first attempt."]})

        return results


# noinspection PyAbstractClass
class HandleFidradHistoryTail(FidradRequestHandler):

    @_login_required
    @_fidrad_search_authorization_required
    def get(self, num_lines: str):
        assert_not_none(num_lines, name="num_lines")
        n_lines = int(num_lines)
        global _history_path
        lines = []
        from collections import deque
        with open(_history_path, mode="r") as file:
            for line in deque(file, maxlen=n_lines):
                lines.append(line.strip())

        self.finish(tornado.escape.json_encode(lines))
        self.logger.info(f"Requested the last {n_lines} lines of the history.")


def reverse_readline(filename, buf_size=8192):
    with open(filename) as f:
        segment = None
        offset = 0
        f.seek(0, os.SEEK_END)
        file_size = remaining_size = f.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            f.seek(file_size - offset)
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


# noinspection PyAbstractClass
class HandleFidRadHistoryBottomUpSearch(FidradRequestHandler):

    @_login_required
    @_fidrad_search_authorization_required
    def get(self, search_string: str, max_num_lines):
        assert_not_none(search_string, name="search_string")
        assert_not_none(max_num_lines, name="max_num_lines")
        max_lines = int(max_num_lines)
        global _history_path
        lines = []

        for line in reverse_readline(_history_path):
            if search_string in line:
                line = line.strip()
                lines.insert(0, line)
            if len(lines) == max_lines:
                break

        self.finish(tornado.escape.json_encode(lines))
        self.logger.info(f"Gave the order to search the history for '{search_string}' and to collect a maximum "
                         f"of {max_lines} search results.")
