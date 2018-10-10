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


from ._handlers import *
from ..webservice import url_pattern


MAPPINGS = (
    (url_pattern('/store/info'), StoreInfo),
    (url_pattern('/store/upload'), StoreUpload),
    (url_pattern('/store/download'), StoreDownload),
    (url_pattern('/datasets'), Datasets),
    (url_pattern('/datasets/{id}'), DatasetsId),
    (url_pattern('/datasets/{affil}/{project}/{cruise}'), DatasetsAffilProjectCruise),
    (url_pattern('/datasets/{affil}/{project}/{cruise}/{name}'), DatasetsAffilProjectCruiseName),
    (url_pattern('/docfiles'), Docfiles),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}'), DocfilesAffilProjectCruise),
    (url_pattern('/docfiles/{affil}/{project}/{cruise}/{name}'), DocfilesAffilProjectCruiseName),
    (url_pattern('/users'), Users),
    (url_pattern('/users/login'), UsersLogin),
    (url_pattern('/users/logout'), UsersLogout),
    (url_pattern('/users/{id}'), UsersId),
)
