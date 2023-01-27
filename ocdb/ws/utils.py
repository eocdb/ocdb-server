import re

from ocdb.ws.errors import WsBadRequestError

# Pattern to ensure string contain at least one letter
name_pattern = r'[\w-]*[a-zA-Z]+[\w-]*'

def ensure_valid_submission_id(submission_id: str) -> bool:
    compiled = re.compile(name_pattern)
    if compiled.fullmatch(submission_id):
        return True
    else:
        raise WsBadRequestError(
            "Please use only alphanumeric characters, underscore or minus sign in your submission id. At least one "
            "letter must be used.")


def ensure_valid_path(path: str) -> bool:
    compiled = re.compile(name_pattern + "/" + name_pattern + "/" + name_pattern)
    if compiled.fullmatch(path):
        return True
    else:
        raise WsBadRequestError("Provide the path as follows: name/name/name (AFFILIATION/EXPERIMENT/CRUISE). "
                                "Each name must contain at least one letter. Use characters, numbers, minus and "
                                "underscores only.")
