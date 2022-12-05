import re

from ocdb.ws.errors import WsBadRequestError


def ensure_valid_submission_id(submission_id: str) -> bool:
    # noinspection RegExpRedundantEscape
    prog = re.compile(r'^[\w-]*$', re.DOTALL)
    if prog.match(submission_id):
        return True
    else:
        raise WsBadRequestError("Please use only alphanumeric characters or underscore in your submission id.")


def ensure_valid_path(path: str) -> bool:
    prog = re.compile(r'^[\w-]*/[\w-]*/[\w-]*$', re.DOTALL)
    if prog.match(path):
        return True
    else:
        raise WsBadRequestError("Please provide the path as format: AFFILIATION (acronym)/EXPERIMENT/CRUISE and use "
                                "characters, numbers and underscores only.")
