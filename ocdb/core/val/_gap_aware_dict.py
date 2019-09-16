
class GapAwareDict(dict):
    def __missing__(self, key):
        return "#MISSING_REFERENCE"
