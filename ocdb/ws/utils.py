import re

from ocdb.ws.errors import WsBadRequestError


def ensure_valid_submission_id(path: str) -> bool:
    # noinspection RegExpRedundantEscape
    prog = re.compile(r'^.*[\./]+.*$', re.DOTALL)
    if prog.match(path):
        raise WsBadRequestError("Please do not use dots and slashes in your submission id.")
    else:
        return True


def ensure_valid_path(path: str) -> bool:
    prog = re.compile(r'^[a-zA-Z0-9_-]*/[a-zA-Z0-9_-]*/[a-zA-Z0-9_-]*$', re.DOTALL)
    if prog.match(path):
        return True
    else:
        raise WsBadRequestError("Please provide the path as format: AFFILIATION (acronym)/EXPERIMENT/CRUISE and use "
                                "characters, numbers and underscores only.")
