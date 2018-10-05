# Development Guide

Our coding style is defined in [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### Imports

From own modules we import other own modules using relative paths. In our main entry
point scripts - where `__name__ == "__main__"` - and in test modules under top-level package `tests`
and we (have to) use absolute paths.

We import *single* classes, functions, constants only from own modules. That is, `from .util import string_to_list`.
From standard libraries or packages we depend on, we always import *with context* so our code is readable and
comprehensive. That is, we don't `from os.path import join`, instead we do `import os` and later
write `os.path.join(a, b, c)` so everyone can understand which `join` it is, e.g. not the `str.join` method.


