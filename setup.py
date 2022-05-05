#!/usr/bin/env python3

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


from setuptools import setup, find_packages

# in alphabetical oder
requirements = [
    # Production
    # 'numpy',
    # 'pymongo',
    # 'pyyaml',
    # 'tornado',
    # Development
    # 'mongomock', 'ftptool', 'bson', 'chardet'
]

packages = find_packages(exclude=["tests", "tests.*"])

VERSION = None
DESCRIPTION = None
with open('ocdb/version.py') as f:
    exec(f.read())

setup(
    name="ocdb-server",
    version=VERSION,
    description=DESCRIPTION,
    license='MIT',
    author='Brockmann Consult GmbH',
    packages=packages,
    package_data={
        'ocdb.ws.res': ['**/*'],
    },
    entry_points={
        'console_scripts': [
            'ocdb-server = ocdb.ws.main:main',
        ],
    },
    install_requires=requirements,
)
