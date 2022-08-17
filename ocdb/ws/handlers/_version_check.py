from packaging import version


# class VersionCheck:
def is_version_valid(current: str, minimum: str):
    cv = version.parse(current)
    mv = version.parse(minimum)
    return not cv < mv
