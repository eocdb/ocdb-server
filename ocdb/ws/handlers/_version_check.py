from packaging import version


# class VersionCheck:    see PEP 440 versioning
def is_version_valid(current: str, minimum: str):
    cv = version.parse(current)
    mv = version.parse(minimum)
    return not cv < mv
